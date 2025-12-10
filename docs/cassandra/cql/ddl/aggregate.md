# Aggregate Commands

User-Defined Aggregates (UDAs) process multiple rows and produce a single result value. UDAs combine a state function, optional final function, and initial state to implement custom aggregation logic like weighted averages, custom statistics, or domain-specific calculations.

---

## Overview

### What are User-Defined Aggregates?

UDAs extend CQL's aggregation capabilities beyond the built-in functions (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`). They enable custom aggregation logic implemented in Java or JavaScript, executed on the coordinator node during query processing.

```sql
-- Built-in aggregate
SELECT AVG(price) FROM products WHERE category = 'electronics';

-- User-defined aggregate for weighted average
SELECT weighted_avg(price, quantity) FROM order_items WHERE order_id = ?;
```

### Version Support

| Feature | Cassandra Version | Notes |
|---------|-------------------|-------|
| User-Defined Aggregates | 2.2+ | Initial UDA support |
| OR REPLACE syntax | 3.0+ | Replace existing aggregates |
| Java UDFs | 2.2+ | Always available |
| JavaScript UDFs | 2.2+ | Requires configuration |
| Improved null handling | 3.0+ | Better INITCOND behavior |

### Configuration Requirements

UDAs require User-Defined Functions (UDFs) to be enabled in `cassandra.yaml`:

```yaml
# Enable Java UDFs (required for UDAs)
enable_user_defined_functions: true

# Enable JavaScript UDFs (optional)
enable_scripted_user_defined_functions: true

# Timeout settings
user_defined_function_warn_timeout: 500ms
user_defined_function_fail_timeout: 10000ms
```

!!! warning "Security Consideration"
    Enabling UDFs allows execution of user-provided code on cluster nodes. In multi-tenant environments, restrict UDF creation permissions to trusted roles only.

### Built-in vs User-Defined Aggregates

| Aspect | Built-in Aggregates | User-Defined Aggregates |
|--------|---------------------|-------------------------|
| Performance | Optimized native code | JVM overhead |
| Availability | Always available | Requires configuration |
| Customization | Fixed behavior | Fully customizable |
| Maintenance | Automatic | User managed |
| Examples | COUNT, SUM, AVG, MIN, MAX | Weighted avg, percentiles, custom stats |

!!! tip "When to Use UDAs"
    Use built-in aggregates when possible—they are faster and require no setup. Use UDAs when:

    - Built-in aggregates don't meet requirements
    - Custom business logic is needed
    - Multiple values must be combined (e.g., weighted calculations)
    - Domain-specific statistics are required

---

## Aggregate Architecture

### How UDAs Work

Aggregates process rows through a state accumulation pattern:

```graphviz dot uda-execution-flow.svg
digraph uda_flow {
    rankdir=TB
    node [fontname="Helvetica" fontsize=11]
    edge [fontname="Helvetica" fontsize=10]

    subgraph cluster_main {
        label="UDA Execution Flow"
        labelloc="t"
        fontname="Helvetica Bold"
        fontsize=14
        style="rounded"
        bgcolor="#f5f5f5"

        init [label="INITCOND\n(Initial State)" shape=box style="rounded,filled" fillcolor="#e3f2fd"]

        loop [label=<
            <TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" CELLPADDING="8">
                <TR><TD BGCOLOR="#fff3e0"><B>For each row:</B></TD></TR>
                <TR><TD BGCOLOR="white">state = SFUNC(state, row_values)</TD></TR>
            </TABLE>
        > shape=none]

        final_state [label="Final State" shape=box style="rounded,filled" fillcolor="#f5f5f5"]

        finalfunc [label="FINALFUNC(state)\n(optional)" shape=box style="rounded,filled" fillcolor="#e8f5e9"]

        result [label="Result" shape=box style="rounded,filled" fillcolor="#c8e6c9"]

        init -> loop [label="initialize"]
        loop -> loop [label="repeat" style=dashed]
        loop -> final_state [label="all rows\nprocessed"]
        final_state -> finalfunc
        finalfunc -> result
    }

    legend [shape=none label=<
        <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="4" CELLPADDING="4">
            <TR><TD ALIGN="LEFT"><B>Components:</B></TD></TR>
            <TR><TD ALIGN="LEFT">• SFUNC: State function (required)</TD></TR>
            <TR><TD ALIGN="LEFT">• STYPE: State data type (required)</TD></TR>
            <TR><TD ALIGN="LEFT">• FINALFUNC: Final transformation (optional)</TD></TR>
            <TR><TD ALIGN="LEFT">• INITCOND: Initial state value (optional)</TD></TR>
        </TABLE>
    >]
}
```

### Components

| Component | Required | Purpose | Example |
|-----------|----------|---------|---------|
| **SFUNC** | Yes | State function called for each row | `sum_state(state, val)` |
| **STYPE** | Yes | Data type of the state variable | `BIGINT`, `TUPLE<...>` |
| **FINALFUNC** | No | Transforms final state to result | `avg_final(state) → DOUBLE` |
| **INITCOND** | No | Initial state value (defaults to null) | `0`, `(0, 0)` |

### Execution Flow

1. State initialized to `INITCOND` (or null if not specified)
2. For each row matching the query:
    - State function called: `new_state = SFUNC(current_state, input_values)`
    - State is updated with return value
3. After all rows processed:
    - If `FINALFUNC` defined: `result = FINALFUNC(final_state)`
    - Otherwise: `result = final_state`

### Execution Location

UDAs execute entirely on the **coordinator node**:

```graphviz dot uda-coordinator.svg
digraph coordinator {
    rankdir=LR
    node [fontname="Helvetica" fontsize=10 shape=box style="rounded"]

    client [label="Client" fillcolor="#e3f2fd" style="rounded,filled"]

    subgraph cluster_coordinator {
        label="Coordinator Node"
        style="rounded"
        bgcolor="#fff3e0"

        query [label="Parse Query"]
        fetch [label="Fetch Rows\nfrom Replicas"]
        aggregate [label="Execute UDA\n(SFUNC per row)"]
        finalize [label="FINALFUNC"]
    }

    replicas [label="Replica\nNodes" fillcolor="#f5f5f5" style="rounded,filled"]

    client -> query
    query -> fetch
    fetch -> replicas [dir=both label="data"]
    fetch -> aggregate
    aggregate -> finalize
    finalize -> client [label="result"]
}
```

!!! warning "Performance Implications"
    - All matching rows are streamed to the coordinator
    - UDA computation happens in coordinator's JVM
    - Large result sets can cause memory pressure
    - Consider filtering with WHERE clause to limit rows

### Null Handling

!!! note "Null Handling"
    If `INITCOND` is not specified and the first row has null input, the state remains null. Subsequent rows with non-null values may then fail if the state function doesn't handle null state.

    **Best practice**: Always specify `INITCOND` and make `SFUNC` null-safe with `CALLED ON NULL INPUT`.

---

## CREATE AGGREGATE

Create a user-defined aggregate function.

### Synopsis

```cqlsyntax
CREATE [ OR REPLACE ] AGGREGATE [ IF NOT EXISTS ]
    [ *keyspace_name*. ] *aggregate_name*
    ( [ *arg_type* [, *arg_type* ... ] ] )
    SFUNC *state_function*
    STYPE *state_type*
    [ FINALFUNC *final_function* ]
    [ INITCOND *initial_condition* ]
```

### Description

`CREATE AGGREGATE` defines a UDA composed of user-defined functions. The state function and optional final function must be created before the aggregate.

### Parameters

#### OR REPLACE

Replace existing aggregate with same signature.

#### IF NOT EXISTS

Prevent error if aggregate already exists.

#### *aggregate_name*

Identifier for the aggregate. Aggregates can be overloaded like functions.

#### Argument Types

Input types matching the state function's input parameters (after the state parameter):

```sql
-- Aggregate taking INT values
CREATE AGGREGATE my_sum(INT) ...

-- Aggregate taking multiple arguments
CREATE AGGREGATE weighted_avg(DOUBLE, DOUBLE) ...
```

#### SFUNC

The state function called for each row. Must:

- Accept state type as first parameter
- Accept aggregate argument types as subsequent parameters
- Return the state type

```sql
-- State function signature for my_sum(INT)
CREATE FUNCTION sum_state(state INT, val INT)
    RETURNS INT ...
```

#### STYPE

Data type for the accumulated state. Can be:

- Native types (`INT`, `BIGINT`, `DOUBLE`, etc.)
- Tuples (for multi-value state)
- User-defined types
- Collections

```sql
-- Simple state
STYPE INT

-- Tuple state (for average: sum and count)
STYPE TUPLE<BIGINT, BIGINT>

-- UDT state
STYPE FROZEN<stats_accumulator>
```

#### FINALFUNC

Optional function to transform final state into result:

- Takes state type as input
- Returns the aggregate's result type

```sql
-- Final function for average
CREATE FUNCTION avg_final(state TUPLE<BIGINT, BIGINT>)
    RETURNS DOUBLE ...
```

If not specified, the final state is returned directly.

#### INITCOND

Initial value for the state. Format depends on state type:

```sql
-- Scalar initial condition
INITCOND 0

-- Tuple initial condition
INITCOND (0, 0)

-- Collection initial condition
INITCOND []

-- UDT initial condition
INITCOND {field1: 0, field2: 0}
```

!!! warning "INITCOND Importance"
    Without `INITCOND`:
    - State starts as null
    - First row must handle null state
    - Empty result sets return null

    With `INITCOND`:
    - State has defined starting value
    - Empty result sets return FINALFUNC(INITCOND) or INITCOND

### Examples

#### Simple Sum Aggregate

```sql
-- State function
CREATE FUNCTION sum_state(state BIGINT, val INT)
    CALLED ON NULL INPUT
    RETURNS BIGINT
    LANGUAGE java
    AS '
        if (val == null) return state;
        if (state == null) return (long) val;
        return state + val;
    ';

-- Aggregate
CREATE AGGREGATE my_sum(INT)
    SFUNC sum_state
    STYPE BIGINT
    INITCOND 0;

-- Usage
SELECT my_sum(quantity) FROM orders WHERE customer_id = ?;
```

#### Average Aggregate

```sql
-- State function (accumulates sum and count)
CREATE FUNCTION avg_state(state TUPLE<BIGINT, BIGINT>, val DOUBLE)
    CALLED ON NULL INPUT
    RETURNS TUPLE<BIGINT, BIGINT>
    LANGUAGE java
    AS '
        if (val == null) return state;
        long sum = state.getLong(0) + val.longValue();
        long count = state.getLong(1) + 1;
        return new com.datastax.driver.core.TupleValue(
            com.datastax.driver.core.TupleType.of(
                com.datastax.driver.core.DataType.bigint(),
                com.datastax.driver.core.DataType.bigint()
            )
        ).setLong(0, sum).setLong(1, count);
    ';

-- Final function (computes average)
CREATE FUNCTION avg_final(state TUPLE<BIGINT, BIGINT>)
    RETURNS NULL ON NULL INPUT
    RETURNS DOUBLE
    LANGUAGE java
    AS '
        long count = state.getLong(1);
        if (count == 0) return null;
        return (double) state.getLong(0) / count;
    ';

-- Aggregate
CREATE AGGREGATE my_avg(DOUBLE)
    SFUNC avg_state
    STYPE TUPLE<BIGINT, BIGINT>
    FINALFUNC avg_final
    INITCOND (0, 0);

-- Usage
SELECT my_avg(price) FROM products WHERE category = ?;
```

#### Weighted Average

```sql
-- State function
CREATE FUNCTION weighted_avg_state(
    state TUPLE<DOUBLE, DOUBLE>,
    value DOUBLE,
    weight DOUBLE
)
    CALLED ON NULL INPUT
    RETURNS TUPLE<DOUBLE, DOUBLE>
    LANGUAGE java
    AS '
        if (value == null || weight == null) return state;
        double sum = state.getDouble(0) + (value * weight);
        double totalWeight = state.getDouble(1) + weight;
        return state.getType().newValue()
            .setDouble(0, sum)
            .setDouble(1, totalWeight);
    ';

-- Final function
CREATE FUNCTION weighted_avg_final(state TUPLE<DOUBLE, DOUBLE>)
    RETURNS NULL ON NULL INPUT
    RETURNS DOUBLE
    LANGUAGE java
    AS '
        double totalWeight = state.getDouble(1);
        if (totalWeight == 0.0) return null;
        return state.getDouble(0) / totalWeight;
    ';

-- Aggregate
CREATE AGGREGATE weighted_avg(DOUBLE, DOUBLE)
    SFUNC weighted_avg_state
    STYPE TUPLE<DOUBLE, DOUBLE>
    FINALFUNC weighted_avg_final
    INITCOND (0.0, 0.0);

-- Usage
SELECT weighted_avg(score, credit_hours) FROM grades
WHERE student_id = ?;
```

#### String Concatenation Aggregate

```sql
-- State function
CREATE FUNCTION concat_state(state TEXT, val TEXT, delimiter TEXT)
    CALLED ON NULL INPUT
    RETURNS TEXT
    LANGUAGE java
    AS '
        if (val == null) return state;
        if (state == null || state.isEmpty()) return val;
        return state + delimiter + val;
    ';

-- Aggregate
CREATE AGGREGATE group_concat(TEXT, TEXT)
    SFUNC concat_state
    STYPE TEXT
    INITCOND '';

-- Usage
SELECT group_concat(tag, ', ') FROM items WHERE category = ?;
```

#### Min/Max with Metadata

```sql
-- State type to track min value and its metadata
CREATE TYPE min_with_id (
    min_value DOUBLE,
    id UUID
);

-- State function
CREATE FUNCTION min_state(state FROZEN<min_with_id>, value DOUBLE, id UUID)
    CALLED ON NULL INPUT
    RETURNS FROZEN<min_with_id>
    LANGUAGE java
    AS '
        if (value == null) return state;
        if (state.getDouble("min_value") == null ||
            value < state.getDouble("min_value")) {
            return state.getType().newValue()
                .setDouble("min_value", value)
                .setUUID("id", id);
        }
        return state;
    ';

-- Aggregate returns the UDT
CREATE AGGREGATE min_with_metadata(DOUBLE, UUID)
    SFUNC min_state
    STYPE FROZEN<min_with_id>;

-- Usage
SELECT min_with_metadata(price, product_id) FROM products;
```

#### Count Distinct Approximation

```sql
-- Using a set to track unique values (limited scalability)
CREATE FUNCTION count_distinct_state(state SET<TEXT>, val TEXT)
    CALLED ON NULL INPUT
    RETURNS SET<TEXT>
    LANGUAGE java
    AS '
        if (val == null) return state;
        java.util.Set<String> result = new java.util.HashSet<>(state);
        result.add(val);
        return result;
    ';

CREATE FUNCTION count_distinct_final(state SET<TEXT>)
    RETURNS NULL ON NULL INPUT
    RETURNS INT
    LANGUAGE java
    AS 'return state.size();';

CREATE AGGREGATE count_distinct(TEXT)
    SFUNC count_distinct_state
    STYPE SET<TEXT>
    FINALFUNC count_distinct_final
    INITCOND {};

-- Usage (caution: memory intensive for high cardinality)
SELECT count_distinct(category) FROM products;
```

### Restrictions

!!! danger "Restrictions"
    **Component Requirements:**

    - SFUNC must exist before creating aggregate
    - SFUNC must accept STYPE as first parameter
    - SFUNC must return STYPE
    - FINALFUNC (if specified) must accept STYPE

    **Type Restrictions:**

    - Counter columns not supported
    - State type must be serializable

    **Execution Restrictions:**

    - Aggregates execute on coordinator only
    - Memory bounded by function limits
    - Cannot aggregate across partitions without ALLOW FILTERING

!!! warning "Performance Considerations"
    - Aggregates process all matching rows
    - Large result sets consume coordinator memory
    - Collection state types grow with data volume
    - Consider pre-aggregating for large datasets

### Notes

- Aggregates stored in `system_schema.aggregates`
- View with `DESCRIBE AGGREGATE`
- Built-in aggregates (COUNT, SUM, AVG) are more efficient than UDAs
- Test with representative data volumes before production use

---

## DROP AGGREGATE

Remove a user-defined aggregate.

### Synopsis

```cqlsyntax
DROP AGGREGATE [ IF EXISTS ] [ *keyspace_name*. ] *aggregate_name*
    [ ( [ *arg_type* [, *arg_type* ... ] ] ) ]
```

### Description

`DROP AGGREGATE` removes a UDA. Specify argument types if multiple overloads exist.

### Parameters

#### IF EXISTS

Prevent error if aggregate doesn't exist.

#### Argument Types

Identify specific overload when multiple exist:

```sql
-- If aggregate has overloads
DROP AGGREGATE my_agg(INT);
DROP AGGREGATE my_agg(DOUBLE);
```

### Examples

```sql
-- Drop simple aggregate
DROP AGGREGATE my_sum;

-- Drop with keyspace
DROP AGGREGATE my_keyspace.weighted_avg;

-- Drop specific overload
DROP AGGREGATE my_avg(DOUBLE);

-- Safe drop
DROP AGGREGATE IF EXISTS temp_aggregate;
```

### Restrictions

!!! warning "Restrictions"
    - Cannot drop aggregate while queries using it are running
    - Dropping aggregate does not drop underlying functions
    - Requires DROP permission

### Finding Aggregates

```sql
-- List aggregates in keyspace
SELECT aggregate_name, argument_types, state_type, state_func
FROM system_schema.aggregates
WHERE keyspace_name = 'my_keyspace';

-- Describe aggregate
DESCRIBE AGGREGATE my_keyspace.my_sum;
```

---

## Best Practices

### When to Use UDAs

!!! tip "Good Use Cases"
    - Custom statistical calculations
    - Domain-specific aggregations
    - Multi-value aggregations (returning tuples/UDTs)
    - Aggregations with complex accumulation logic

### When to Avoid UDAs

!!! warning "Avoid When"
    - Built-in aggregates suffice (COUNT, SUM, AVG, MIN, MAX)
    - Aggregating across entire table (too many rows)
    - High-frequency queries (UDA overhead significant)
    - Memory-intensive state types on large datasets

### Design Guidelines

1. **Choose appropriate state type**
   - Simple types for simple aggregations
   - Tuples for multi-value accumulation
   - Avoid unbounded collections

2. **Handle null state correctly**
   - Use INITCOND when possible
   - Make SFUNC null-safe

3. **Test with realistic volumes**
   - Profile memory usage
   - Test with expected result set sizes

4. **Consider pre-aggregation**
   - Maintain aggregated tables for common queries
   - Update aggregates via application logic

### Cleanup: Dropping Aggregate and Functions

```sql
-- Order matters: drop aggregate before its functions
DROP AGGREGATE IF EXISTS my_avg;
DROP FUNCTION IF EXISTS avg_final;
DROP FUNCTION IF EXISTS avg_state;
```

---

## Related Documentation

- **[CREATE FUNCTION](function.md)** - User-defined functions for aggregates
- **[Functions Reference](../functions/index.md)** - Built-in aggregate functions
- **[SELECT](../dml/index.md#select)** - Using aggregates in queries
