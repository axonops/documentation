---
title: "Cassandra Data Modeling: The Complete Guide"
description: "Cassandra data modeling guide. Design patterns, best practices, and examples."
meta:
  - name: keywords
    content: "Cassandra data modeling, schema design, data model patterns"
---

# Cassandra Data Modeling: The Complete Guide

Data modeling in Cassandra is fundamentally different from relational databases—and getting it wrong is the primary cause of performance problems, operational nightmares, and failed Cassandra deployments. This guide teaches the query-driven paradigm that Cassandra requires.

The most important lesson: **In Cassandra, tables are designed around queries, not around data relationships.**

---

## Why Data Modeling Is Critical in Cassandra

### The Relational Mindset vs. Cassandra Reality

In relational databases:
```
1. Define your entities (customers, orders, products)
2. Normalize to eliminate redundancy
3. Write any query needed (JOIN tables at runtime)
4. Add indexes when queries are slow
```

In Cassandra, this approach **will fail spectacularly**:
```
1. There are no JOINs
2. Every query must be served by a single table
3. Data must be denormalized (duplicated intentionally)
4. Schema design determines query performance (not indexes)
5. Wrong design = slow queries that cannot be fixed without migration
```

### What Goes Wrong With Bad Data Models

| Symptom | Description | Impact |
|---------|-------------|--------|
| **Hot Partitions** | One partition receives all traffic | One node overloaded while others idle; timeouts and failed requests |
| **Large Partitions** | Partition grows to GB+ size | Reads timeout; compaction stalls; repairs take days |
| **Tombstone Accumulation** | Deletes create tombstones that pile up | Reads slow down scanning tombstones; eventual query failures |
| **Scatter-Gather Queries** | Query hits many partitions | Coordinator waits for all responses; P99 latency determined by slowest partition; does not scale |

!!! danger "Root Cause"
    All of these are **data model problems**, not Cassandra problems.

---

## The Query-First Methodology

### Step 1: List Every Query the Application Needs

Before writing any CQL, document every read pattern:

```
APPLICATION: E-commerce Store

Q1: Get product details by product_id
Q2: List products in a category (sorted by price)
Q3: Get all orders for a customer (most recent first)
Q4: Get order details by order_id
Q5: Find orders by status (for admin dashboard)
Q6: Get customer by email (for login)
Q7: List reviews for a product (most recent first)
Q8: Get inventory levels for a product across warehouses
```

### Step 2: Design One Table Per Query

Each query gets its own table. Data is duplicated across tables.

```sql
-- Q1: Get product by ID
CREATE TABLE products (
    product_id UUID PRIMARY KEY,
    name TEXT,
    description TEXT,
    price DECIMAL,
    category TEXT
);

-- Q2: Products by category (sorted by price)
CREATE TABLE products_by_category (
    category TEXT,
    price DECIMAL,
    product_id UUID,
    name TEXT,
    PRIMARY KEY ((category), price, product_id)
) WITH CLUSTERING ORDER BY (price ASC);

-- Q3: Orders for customer (most recent first)
CREATE TABLE orders_by_customer (
    customer_id UUID,
    order_date TIMESTAMP,
    order_id UUID,
    status TEXT,
    total DECIMAL,
    PRIMARY KEY ((customer_id), order_date, order_id)
) WITH CLUSTERING ORDER BY (order_date DESC);

-- And so on for each query...
```

### Step 3: Write the Queries

Verify each table supports its query:

```sql
-- Q1: Product by ID
SELECT * FROM products WHERE product_id = ?;
-- ✓ Single partition lookup

-- Q2: Products in category
SELECT * FROM products_by_category WHERE category = 'Electronics' LIMIT 100;
-- ✓ Single partition, sorted by price

-- Q3: Customer's recent orders
SELECT * FROM orders_by_customer WHERE customer_id = ? LIMIT 20;
-- ✓ Single partition, sorted by date DESC
```

### Step 4: Validate Partition Sizes

Estimate how large each partition will grow:

```
Table: orders_by_customer
Partition key: customer_id

Assumptions:
- Average customer places 50 orders/year
- Each order row: ~500 bytes
- Customer retention: 5 years

Partition size: 50 orders × 5 years × 500 bytes = 125KB

✓ GOOD: Well under 100MB limit
```

```
Table: products_by_category
Partition key: category

Assumptions:
- 100 categories
- 10,000 products total
- Average 100 products per category
- Each product row: ~1KB

Partition size: 100 products × 1KB = 100KB

✓ GOOD: Small partitions
```

---

## Primary Key Design

The primary key is the most important decision in Cassandra data modeling.

### Anatomy of a Primary Key

```sql
PRIMARY KEY ((partition_key_col1, partition_key_col2), clustering_col1, clustering_col2)
--           |___________________________________|   |__________________________________|
--                      PARTITION KEY                        CLUSTERING COLUMNS
```

**Partition Key**:
- Determines which node stores the data
- All rows with same partition key = one partition
- Used in `WHERE` clause equality (`=`)
- Can be single column or composite

**Clustering Columns**:
- Determine sort order within partition
- Enable range queries (`>`, `<`, `>=`, `<=`)
- Required for uniqueness when partition key is not unique

### Single Column Partition Key

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username TEXT,
    email TEXT
);

-- Each user_id is its own partition
-- Perfect for: Entity lookup by unique ID
```

### Compound Primary Key (Partition Key + Clustering)

```sql
CREATE TABLE messages (
    conversation_id UUID,    -- Partition key
    sent_at TIMESTAMP,       -- Clustering column 1
    message_id UUID,         -- Clustering column 2 (for uniqueness)
    sender_id UUID,
    content TEXT,
    PRIMARY KEY ((conversation_id), sent_at, message_id)
) WITH CLUSTERING ORDER BY (sent_at DESC, message_id DESC);
```

**Partition for conversation_id = abc-123** (sorted by sent_at DESC, then message_id DESC):

| sent_at | message_id | content |
|---------|------------|---------|
| 2024-01-15 10:30:00 | 111 | "Hi" |
| 2024-01-15 10:29:00 | 110 | "Hello" |
| 2024-01-15 10:28:00 | 109 | "Hey" |
| ... | ... | ... |

### Composite Partition Key

```sql
CREATE TABLE events (
    tenant_id TEXT,          -- Part of partition key
    event_date DATE,         -- Part of partition key (time bucket)
    event_time TIMESTAMP,    -- Clustering column
    event_id UUID,
    data TEXT,
    PRIMARY KEY ((tenant_id, event_date), event_time, event_id)
);
```

```
Partitions:
- (tenant_id=acme, event_date=2024-01-15) = one partition
- (tenant_id=acme, event_date=2024-01-16) = another partition
- (tenant_id=globex, event_date=2024-01-15) = another partition

Benefits:
- Tenant data is isolated (multi-tenancy)
- Each day is a bounded partition (time bucketing)
- No partition grows unbounded
```

---

## Partition Sizing: The Most Critical Constraint

### The Numbers That Matter

**Partition Size Guidelines:**

| Size | Status | Impact |
|------|--------|--------|
| < 10 MB | Ideal | Fast reads, fast compaction |
| 10-100 MB | Acceptable | Works fine, monitor growth |
| 100 MB - 1 GB | Warning | Noticeable latency, compaction slower |
| > 1 GB | Critical | Timeouts, repairs fail, must redesign |

**Row Count Guidelines** (depends on row size):

| Row Size | Maximum Rows per Partition |
|----------|---------------------------|
| Small (~100 bytes) | < 100,000 rows |
| Medium (~1 KB) | < 100,000 rows |
| Large (~10 KB) | < 10,000 rows |

**Hard Limits:**

- Cells per partition: 2 billion (theoretical)
- Practical limit: Stay under 100,000 rows

### Calculating Partition Size

```
Partition Size = Number of Rows × Average Row Size

Row Size = Column Metadata Overhead (~23 bytes)
         + Primary Key Columns (serialized size)
         + Data Columns (serialized size)
         + Timestamps (~8 bytes per column)

Example calculation:

Table: messages
Columns: conversation_id (16 bytes), sent_at (8 bytes), message_id (16 bytes),
         sender_id (16 bytes), content (average 200 bytes)

Row size ≈ 23 + 16 + 8 + 16 + 16 + 200 + (5 × 8) = ~319 bytes

Messages per conversation: 10,000 over lifetime
Partition size: 10,000 × 319 bytes = 3.19 MB ✓ GOOD

Messages per conversation: 1,000,000 (very active chat)
Partition size: 1,000,000 × 319 bytes = 319 MB ⚠️ WARNING
```

### Time Bucketing to Control Partition Size

When partitions grow unbounded over time:

```sql
-- PROBLEM: Unbounded partition growth
CREATE TABLE sensor_data_bad (
    sensor_id UUID,
    reading_time TIMESTAMP,
    value DOUBLE,
    PRIMARY KEY ((sensor_id), reading_time)
);
-- Sensor runs for years → partition grows forever!

-- SOLUTION: Time bucketing
CREATE TABLE sensor_data_good (
    sensor_id UUID,
    day DATE,                -- Bucket (new partition each day)
    reading_time TIMESTAMP,
    value DOUBLE,
    PRIMARY KEY ((sensor_id, day), reading_time)
);
-- Each day is a new partition, bounded by readings/day
```

**Choosing the bucket size**:

| Readings/Second | Bucket | Rows/Partition | Size Estimate |
|-----------------|--------|----------------|---------------|
| 1/min | MONTH | ~43,000 | ~2 MB |
| 1/sec | DAY | ~86,000 | ~4 MB |
| 10/sec | HOUR | ~36,000 | ~2 MB |
| 100/sec | HOUR | ~360,000 | ~18 MB |
| 1000/sec | MINUTE | ~60,000 | ~3 MB |

---

## Clustering Columns and Sort Order

### How Clustering Works

Within a partition, rows are stored sorted by clustering columns:

```sql
CREATE TABLE orders (
    customer_id UUID,
    order_date DATE,
    order_id UUID,
    status TEXT,
    total DECIMAL,
    PRIMARY KEY ((customer_id), order_date, order_id)
) WITH CLUSTERING ORDER BY (order_date DESC, order_id DESC);
```

**Partition for customer_id = customer-123** (storage order determined by CLUSTERING ORDER BY):

| order_date | order_id | total |
|------------|----------|-------|
| 2024-01-15 | order-999 | 150.00 |
| 2024-01-15 | order-998 | 75.50 |
| 2024-01-14 | order-997 | 200.00 |
| 2024-01-10 | order-995 | 50.00 |
| ...older orders... | | |

Reading "most recent orders" reads from the **top** of the partition—a sequential read, very fast.

### Range Queries on Clustering Columns

```sql
-- Get orders from January 2024
SELECT * FROM orders
WHERE customer_id = ?
  AND order_date >= '2024-01-01'
  AND order_date < '2024-02-01';

-- Cassandra finds the range in the sorted partition
-- Sequential read of just the matching rows
```

**Clustering column restrictions**:

```sql
-- WORKS: Restrict first clustering column
SELECT * FROM orders WHERE customer_id = ? AND order_date = '2024-01-15';

-- WORKS: Range on first clustering column
SELECT * FROM orders WHERE customer_id = ? AND order_date > '2024-01-01';

-- WORKS: Equality on first, range on second
SELECT * FROM orders WHERE customer_id = ? AND order_date = '2024-01-15'
                                           AND order_id > ?;

-- DOESN'T WORK: Skip first clustering column
SELECT * FROM orders WHERE customer_id = ? AND order_id = ?;
-- Error: Must restrict order_date first!
```

---

## Denormalization: Embracing Data Duplication

### Why Cassandra Requires Denormalization

**Relational approach:** Query "Get order with customer name and product details"

```sql
SELECT o.*, c.name, p.name, p.price
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.order_id = 123;
-- Database figures out how to JOIN these at runtime
```

**Cassandra approach:** Query "Get order with all details"

```sql
SELECT * FROM orders_with_details WHERE order_id = 123;
-- The table ALREADY CONTAINS customer name and product details
-- Data was duplicated at write time
```

### One Table Per Query Pattern

```sql
-- Query 1: Orders by customer
CREATE TABLE orders_by_customer (
    customer_id UUID,
    order_date TIMESTAMP,
    order_id UUID,
    customer_name TEXT,      -- Denormalized from customers
    status TEXT,
    total DECIMAL,
    PRIMARY KEY ((customer_id), order_date, order_id)
);

-- Query 2: Orders by status (for admin)
CREATE TABLE orders_by_status (
    status TEXT,
    order_date DATE,
    order_id UUID,
    customer_id UUID,
    customer_name TEXT,      -- Same data, different partition
    total DECIMAL,
    PRIMARY KEY ((status, order_date), order_id)
);

-- Query 3: Order details by ID
CREATE TABLE orders_by_id (
    order_id UUID PRIMARY KEY,
    customer_id UUID,
    customer_name TEXT,
    status TEXT,
    total DECIMAL,
    items LIST<FROZEN<order_item>>  -- Nested items
);
```

### Managing Denormalized Data

**Option 1: Application-level consistency**
```python
# Write to all tables in application code
def create_order(order):
    session.execute(orders_by_customer_insert, order)
    session.execute(orders_by_status_insert, order)
    session.execute(orders_by_id_insert, order)
```

**Option 2: Logged batches (same partition)**
```sql
-- Only efficient for same-partition writes
BEGIN BATCH
    INSERT INTO orders_by_customer (...) VALUES (...);
    INSERT INTO orders_by_customer_items (...) VALUES (...);
APPLY BATCH;
```

**Option 3: Unlogged batches (different partitions)**
```sql
-- Cassandra optimizes multi-partition batches
BEGIN UNLOGGED BATCH
    INSERT INTO orders_by_customer (...) VALUES (...);
    INSERT INTO orders_by_status (...) VALUES (...);
APPLY BATCH;
-- Note: Not atomic! Can partially fail.
```

---

## Collection Types

Cassandra supports collections for storing multiple values in a single column.

### Lists, Sets, and Maps

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username TEXT,
    emails SET<TEXT>,              -- Unique values, no order
    phone_numbers LIST<TEXT>,      -- Ordered, allows duplicates
    preferences MAP<TEXT, TEXT>    -- Key-value pairs
);

INSERT INTO users (user_id, username, emails, phone_numbers, preferences)
VALUES (
    uuid(),
    'alice',
    {'alice@home.com', 'alice@work.com'},
    ['+1-555-0100', '+1-555-0101'],
    {'theme': 'dark', 'notifications': 'enabled'}
);
```

### Collection Limitations

!!! warning "Collection Gotchas"

    **1. Size Limit**

    - Collections are loaded entirely into memory
    - Max ~64KB recommended (technically 2GB but avoid)
    - Large collections = slow queries + heap pressure

    **2. Read-Before-Write**

    - Updating one element reads the whole collection
    - Avoid for frequently updated data

    **3. No Querying Inside Collections**

    - Cannot use: `WHERE preferences['theme'] = 'dark'`
    - Must return whole collection and filter in application

    **4. Frozen Collections**

    - `FROZEN<LIST<TEXT>>` = immutable, stored as blob
    - Cannot update individual elements
    - Required for nested collections or UDTs in collections

### When to Use Collections

**Good use cases**:
- Small lists of tags, categories
- User preferences (small map)
- Contact information (few emails/phones)

**Bad use cases**:
- Order items (use a separate table)
- Activity history (use clustering columns)
- Large lists of anything

---

## Static Columns

Static columns share a single value across all rows in a partition:

```sql
CREATE TABLE orders (
    customer_id UUID,
    customer_name TEXT STATIC,    -- Same for all rows in partition
    customer_email TEXT STATIC,
    order_date TIMESTAMP,
    order_id UUID,
    total DECIMAL,
    PRIMARY KEY ((customer_id), order_date, order_id)
);
```

**Partition for customer_id = cust-123:**

| Column Type | Column | Value |
|-------------|--------|-------|
| **STATIC** | customer_name | "Alice" |
| **STATIC** | customer_email | "alice@mail.com" |

| order_date | order_id | total |
|------------|----------|-------|
| 2024-01-15 | ord-1 | 100.00 |
| 2024-01-10 | ord-2 | 50.00 |
| 2024-01-05 | ord-3 | 75.00 |

Static columns are stored **once per partition**, not per row.

**Use cases**:
- Metadata about the partition (customer name for customer's orders)
- Counters at partition level
- Settings that apply to all rows

---

## User-Defined Types (UDTs)

Group related columns into reusable types:

```sql
-- Define the type
CREATE TYPE address (
    street TEXT,
    city TEXT,
    state TEXT,
    zip TEXT,
    country TEXT
);

-- Use in a table
CREATE TABLE customers (
    customer_id UUID PRIMARY KEY,
    name TEXT,
    billing_address FROZEN<address>,
    shipping_address FROZEN<address>
);

-- Insert
INSERT INTO customers (customer_id, name, billing_address, shipping_address)
VALUES (
    uuid(),
    'Alice',
    {street: '123 Main St', city: 'Boston', state: 'MA', zip: '02101', country: 'USA'},
    {street: '456 Oak Ave', city: 'Boston', state: 'MA', zip: '02102', country: 'USA'}
);
```

**UDT limitations**:
- Must be FROZEN when used in collections or as clustering columns
- FROZEN means the entire UDT is updated at once (no partial updates)
- Can't add/remove fields after data is written (schema evolution is hard)

---

## Secondary Indexes: When to Use (Rarely)

### Native Secondary Indexes

```sql
CREATE INDEX ON users (email);

-- Now queries are possible:
SELECT * FROM users WHERE email = 'alice@example.com';
```

**How it works:** Secondary index creates a hidden table:

| email (partition key) | user_id |
|-----------------------|---------|
| alice@example.com | user-123 |
| bob@example.com | user-456 |

Query on email → look up in index → get user_id → fetch from main table.

### When Secondary Indexes Are OK

| Use Case | Reason |
|----------|--------|
| Low cardinality columns (status, country) | Few unique values; index partitions are manageable |
| Combined with partition key | Filters within a known partition (e.g., `WHERE customer_id = ? AND status = 'pending'`) |
| Infrequent queries | Admin dashboards, analytics—not user-facing hot paths |

### When Secondary Indexes Are Dangerous

| Anti-Pattern | Problem |
|--------------|---------|
| High cardinality columns (email, user_id) | Every value is its own partition; scatter-gather across entire cluster; worse than no index |
| Frequently updated columns | Index updates are expensive; write amplification |
| User-facing queries at scale | Unpredictable latency; does not scale with cluster size |

### Alternative: Materialized Views (Also Use With Caution)

```sql
CREATE MATERIALIZED VIEW users_by_email AS
    SELECT * FROM users
    WHERE email IS NOT NULL AND user_id IS NOT NULL
    PRIMARY KEY (email, user_id);
```

**Materialized View problems**:
- Write amplification (every write to base table updates view)
- Can get out of sync (known bugs, especially during repair)
- Repair does not automatically repair views
- Generally: prefer explicit denormalized tables

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Unbounded Partition Growth

```sql
-- BAD: Partition grows forever
CREATE TABLE events (
    device_id UUID PRIMARY KEY,
    event_time TIMESTAMP,
    data TEXT
);
-- Every event for a device in one partition!

-- GOOD: Time-bucketed
CREATE TABLE events (
    device_id UUID,
    day DATE,
    event_time TIMESTAMP,
    data TEXT,
    PRIMARY KEY ((device_id, day), event_time)
);
```

### Anti-Pattern 2: Using ALLOW FILTERING

```sql
-- BAD: Full table scan
SELECT * FROM products WHERE price > 100 ALLOW FILTERING;
-- Scans EVERY partition on EVERY node!

-- GOOD: Design a table for this query
CREATE TABLE products_by_price_range (
    price_bucket TEXT,  -- 'under_50', '50_to_100', 'over_100'
    price DECIMAL,
    product_id UUID,
    name TEXT,
    PRIMARY KEY ((price_bucket), price, product_id)
);
```

### Anti-Pattern 3: Queue-Like Patterns

```sql
-- BAD: Using Cassandra as a queue
CREATE TABLE job_queue (
    status TEXT,
    created_at TIMESTAMP,
    job_id UUID,
    data TEXT,
    PRIMARY KEY ((status), created_at, job_id)
);
-- 'pending' partition becomes huge and hot

-- GOOD: Use an actual queue (Kafka, RabbitMQ)
-- Or: Bucket by time AND status
CREATE TABLE jobs_by_status (
    status TEXT,
    day DATE,
    created_at TIMESTAMP,
    job_id UUID,
    data TEXT,
    PRIMARY KEY ((status, day), created_at, job_id)
);
```

### Anti-Pattern 4: Over-Denormalization

```
Problem: Creating 15 tables for 15 queries
         Every write updates all 15 tables
         Write throughput tanks
         Consistency nightmares

Solution: Group queries that can share a table
          Accept some inefficiency in exchange for simplicity
          Use LIMIT liberally
```

### Anti-Pattern 5: Wide Rows With Frequent Deletes

```sql
-- BAD: Delete old messages frequently
DELETE FROM messages WHERE conversation_id = ? AND sent_at < ?;
-- Creates range tombstones that pile up

-- GOOD: Use TTL for automatic expiration
INSERT INTO messages (...) VALUES (...) USING TTL 2592000; -- 30 days
```

---

## Testing Your Data Model

### Before Production

1. **Estimate partition sizes** for realistic data volumes
2. **Run load tests** with production-like patterns
3. **Monitor** with `nodetool tablestats`:
   - Partition size (max, mean)
   - SSTable count
   - Tombstone warnings
4. **Verify queries** work without ALLOW FILTERING

### Useful Commands

```bash
# Check partition sizes
nodetool tablestats keyspace.table | grep -i partition

# Check for large partitions
nodetool tablestats keyspace.table | grep "Compacted partition maximum"

# Check tombstones
nodetool tablestats keyspace.table | grep -i tombstone
```

### Red Flags

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| One node hot, others idle | Hot partition | Change partition key |
| Read latency increasing over time | Growing partitions | Add time bucketing |
| "Scanned N tombstones" warnings | Delete-heavy partition | Use TTL, redesign |
| Query times out | Partition too large | Split partition |

---

## Data Modeling Checklist

Before deploying the schema:

- [ ] Every query maps to exactly one table
- [ ] Partition keys include all `WHERE` equality columns
- [ ] Clustering columns match `ORDER BY` requirements
- [ ] Estimated partition size < 100MB
- [ ] No unbounded partition growth
- [ ] TTL set for time-series/ephemeral data
- [ ] No reliance on `ALLOW FILTERING`
- [ ] No secondary indexes on high-cardinality columns
- [ ] Write path does not update too many tables
- [ ] Tested with production-scale data

---

## Next Steps

- **[Primary Keys Deep Dive](concepts/index.md)** - Advanced partition key strategies
- **[Time Bucketing Pattern](patterns/time-bucketing.md)** - Handling time-series data
- **[Anti-Patterns Guide](anti-patterns/index.md)** - What to avoid
- **[E-Commerce Example](examples/e-commerce.md)** - Complete worked example
- **[CQL Reference](../cql/index.md)** - Query language details
