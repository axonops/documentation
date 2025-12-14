---
description: "Cassandra CREATE KEYSPACE syntax and options in CQL. Configure replication strategy and datacenter settings."
meta:
  - name: keywords
    content: "CREATE KEYSPACE, CQL keyspace, replication strategy, NetworkTopologyStrategy"
---

# Keyspace Commands

Keyspaces are the top-level namespace in Cassandra, analogous to databases in relational systems. Each keyspace defines replication strategy and options that apply to all tables within it.

---

## Behavioral Guarantees

### What Keyspace Operations Guarantee

- CREATE KEYSPACE creates metadata that propagates to all nodes via gossip
- Schema changes are atomic at the coordinator level
- IF NOT EXISTS and IF EXISTS clauses provide idempotent operations
- Replication settings take effect immediately for new writes after schema agreement
- DROP KEYSPACE triggers automatic snapshot creation when `auto_snapshot: true` (default)

### What Keyspace Operations Do NOT Guarantee

!!! warning "Undefined Behavior"
    The following behaviors are undefined and must not be relied upon:

    - **Immediate schema visibility**: Other nodes may not see schema changes until gossip propagates (typically milliseconds, but can be longer under load)
    - **Data movement on ALTER**: Changing replication settings does not automatically move data; repair or rebuild is required
    - **Atomic multi-node updates**: Schema propagation is eventually consistent, not transactional
    - **Immediate replica deletion**: Reducing replication factor does not immediately delete excess replicas

### Schema Agreement Contract

Schema changes require agreement across the cluster:

| State | Description | Client Impact |
|-------|-------------|---------------|
| Schema agreed | All nodes have same schema version | Safe to proceed |
| Schema disagreement | Nodes have different schema versions | Operations may fail or behave unexpectedly |

Monitor schema agreement with:
```bash
nodetool describecluster
```

### Failure Semantics

| Failure Mode | Outcome | Client Action |
|--------------|---------|---------------|
| Timeout during CREATE/ALTER | Undefined - schema may or may not have propagated | Check schema agreement, retry if needed |
| Node down during schema change | Schema propagates when node returns | Monitor schema agreement |
| `InvalidRequest` | Operation rejected, no change | Fix request and retry |
| `Unauthorized` | Permission denied, no change | Request appropriate permissions |

### Version-Specific Behavior

| Version | Behavior |
|---------|----------|
| 3.0+ | Improved schema propagation via `system_schema` keyspace |
| 4.0+ | Schema pull on gossip (CASSANDRA-13426), faster agreement |
| 5.0+ | Transactional metadata (CEP-21) for atomic schema changes |

---

## CREATE KEYSPACE

Create a new keyspace with specified replication configuration.

### Synopsis

```cqlsyntax
CREATE KEYSPACE [ IF NOT EXISTS ] *keyspace_name*
    WITH REPLICATION = { *replication_map* }
    [ AND DURABLE_WRITES = { true | false } ]
```

**replication_map**:

```cqlsyntax
{ 'class': '*strategy_name*' [, *strategy_options* ] }
```

### Description

`CREATE KEYSPACE` defines a new namespace for tables with specified replication settings. The keyspace name becomes a namespace prefix for all objects created within it.

The replication strategy determines how Cassandra distributes data replicas across nodes. Choosing the correct strategy is critical for data durability, availability, and performance.

### Parameters

#### *keyspace_name*

The identifier for the new keyspace. Must be unique within the cluster.

- Unquoted names are case-insensitive and stored in lowercase
- Quoted names (`"MyKeyspace"`) preserve case
- Maximum length: 48 characters
- Valid characters: letters, digits, underscores (must start with letter)

#### IF NOT EXISTS

Optional clause that prevents an error if a keyspace with the same name already exists. When specified:

- If keyspace exists: statement succeeds with no effect
- If keyspace does not exist: keyspace is created

!!! note "Idempotent Operations"
    Use `IF NOT EXISTS` in application startup scripts and migration tools to make keyspace creation idempotent. This prevents errors when scripts run multiple times.

#### REPLICATION

Required. Defines how data is replicated across the cluster.

**strategy_name** must be one of:

| Strategy | Use Case | Required Options |
|----------|----------|------------------|
| `SimpleStrategy` | Development, single datacenter | `'replication_factor': *n*` |
| `NetworkTopologyStrategy` | Production, multi-datacenter | `'*datacenter_name*': *n*` per DC |
| `LocalStrategy` | System keyspaces only | None (internal use) |

##### SimpleStrategy

Places the first replica on the node determined by the partitioner, then places additional replicas on consecutive nodes in the ring, regardless of datacenter or rack topology.

```sql
WITH REPLICATION = {
    'class': 'SimpleStrategy',
    'replication_factor': 3
}
```

!!! danger "Production Warning"
    **Never use `SimpleStrategy` in production multi-datacenter deployments.** It does not respect datacenter boundaries, potentially placing all replicas in a single datacenter. This creates a single point of failure and increases cross-datacenter traffic.

##### NetworkTopologyStrategy

Places replicas in each datacenter according to specified replication factors. Within each datacenter, replicas are distributed across different racks when possible.

```sql
WITH REPLICATION = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3,
    'dc2': 3
}
```

The datacenter names must match the datacenter names configured in each node's `cassandra-rackdc.properties` file or snitch configuration.

!!! tip "Datacenter Naming"
    Use consistent, meaningful datacenter names across the cluster. Common conventions:

    - Geographic: `us-east`, `eu-west`, `ap-south`
    - Functional: `analytics`, `oltp`, `search`
    - Provider-specific: `aws-us-east-1`, `gcp-europe-west1`

##### Replication Factor Guidelines

| Workload | Recommended RF | Rationale |
|----------|----------------|-----------|
| Development | 1 | Minimize resources |
| Testing | 2 | Basic redundancy |
| Production | 3 | Survives single node failure with QUORUM |
| High durability | 5 | Survives two node failures with QUORUM |

#### DURABLE_WRITES

Optional. Controls whether writes are recorded in the commit log before being acknowledged.

| Value | Behavior |
|-------|----------|
| `true` (default) | Writes go to commit log, ensuring durability |
| `false` | Writes bypass commit log, risking data loss on node failure |

!!! danger "Data Loss Risk"
    Setting `DURABLE_WRITES = false` disables the commit log for the keyspace. If a node crashes before memtables flush to SSTables, **data will be permanently lost**. Use only for:

    - Caches that can be regenerated
    - Temporary data that can be recomputed
    - Development/testing environments

### Examples

#### Development Keyspace

```sql
CREATE KEYSPACE dev_keyspace
WITH REPLICATION = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};
```

#### Production Single-Datacenter

```sql
CREATE KEYSPACE prod_keyspace
WITH REPLICATION = {
    'class': 'NetworkTopologyStrategy',
    'datacenter1': 3
};
```

#### Production Multi-Datacenter

```sql
CREATE KEYSPACE global_keyspace
WITH REPLICATION = {
    'class': 'NetworkTopologyStrategy',
    'us-east': 3,
    'eu-west': 3,
    'ap-south': 3
};
```

#### Cache Keyspace (No Durability)

```sql
CREATE KEYSPACE cache_keyspace
WITH REPLICATION = {
    'class': 'NetworkTopologyStrategy',
    'datacenter1': 2
}
AND DURABLE_WRITES = false;
```

#### Idempotent Creation

```sql
CREATE KEYSPACE IF NOT EXISTS my_keyspace
WITH REPLICATION = {
    'class': 'NetworkTopologyStrategy',
    'datacenter1': 3
};
```

### Restrictions

!!! warning "Restrictions"
    - Keyspace names cannot be changed after creation
    - System keyspaces (`system`, `system_schema`, etc.) cannot be created or dropped
    - Replication factor cannot exceed the number of nodes in a datacenter
    - At least one datacenter must be specified for `NetworkTopologyStrategy`

### Notes

- After creating a keyspace, no data movement occurs until tables are created and populated
- The keyspace metadata propagates to all nodes via gossip
- Creating a keyspace with RF > number of nodes succeeds but triggers warnings
- Monitor `nodetool describecluster` to verify schema agreement after creation

---

## ALTER KEYSPACE

Modify the replication strategy or options of an existing keyspace.

### Synopsis

```cqlsyntax
ALTER KEYSPACE *keyspace_name*
    WITH REPLICATION = { *replication_map* }
    [ AND DURABLE_WRITES = { true | false } ]
```

### Description

`ALTER KEYSPACE` changes the replication configuration of an existing keyspace. This is a metadata-only operation that takes effect immediately for new writes.

!!! warning "Repair Required"
    After altering replication settings, existing data does not automatically redistribute. Run `nodetool repair` on all nodes to ensure data is replicated according to the new settings.

### Parameters

#### REPLICATION

The new replication configuration. Completely replaces the existing configuration.

To add a datacenter, include all existing datacenters plus the new one:

```sql
-- Original: dc1: 3
-- Adding dc2
ALTER KEYSPACE my_keyspace
WITH REPLICATION = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3,
    'dc2': 3
};
```

To remove a datacenter, omit it from the new configuration:

```sql
-- Removing dc2
ALTER KEYSPACE my_keyspace
WITH REPLICATION = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3
};
```

!!! danger "Removing Datacenters"
    Before removing a datacenter from replication:

    1. Ensure no clients are reading from or writing to that datacenter
    2. Run `nodetool repair` to ensure data is replicated elsewhere
    3. Verify data integrity before decommissioning nodes

#### DURABLE_WRITES

Change the commit log behavior for the keyspace.

### Examples

#### Increase Replication Factor

```sql
ALTER KEYSPACE my_keyspace
WITH REPLICATION = {
    'class': 'NetworkTopologyStrategy',
    'datacenter1': 5
};

-- Then run repair on all nodes
-- nodetool repair my_keyspace
```

#### Add a Datacenter

```sql
ALTER KEYSPACE my_keyspace
WITH REPLICATION = {
    'class': 'NetworkTopologyStrategy',
    'us-east': 3,
    'eu-west': 3  -- New datacenter
};

-- Repair to populate new datacenter
-- nodetool rebuild -- dc us-east  (run on eu-west nodes)
```

#### Migrate from SimpleStrategy to NetworkTopologyStrategy

```sql
ALTER KEYSPACE legacy_keyspace
WITH REPLICATION = {
    'class': 'NetworkTopologyStrategy',
    'datacenter1': 3
};

-- Run repair to ensure proper replica placement
-- nodetool repair legacy_keyspace
```

#### Enable Durable Writes

```sql
ALTER KEYSPACE cache_keyspace
WITH REPLICATION = {
    'class': 'NetworkTopologyStrategy',
    'datacenter1': 2
}
AND DURABLE_WRITES = true;
```

### Restrictions

!!! warning "Restrictions"
    - Cannot change keyspace name
    - Cannot alter system keyspaces
    - Reducing RF does not immediately delete excess replicas (removed during compaction)
    - Changing strategy class requires specifying all new strategy options

### Notes

- Schema changes propagate via gossip; monitor schema agreement
- Increasing RF: run `nodetool repair` to create new replicas
- Decreasing RF: excess replicas are removed during compaction
- Adding datacenter: use `nodetool rebuild` on new datacenter nodes

---

## DROP KEYSPACE

Remove a keyspace and all its contents permanently.

### Synopsis

```cqlsyntax
DROP KEYSPACE [ IF EXISTS ] *keyspace_name*
```

### Description

`DROP KEYSPACE` permanently removes a keyspace and all objects within it: tables, indexes, materialized views, user-defined types, functions, and aggregates. All data is deleted.

!!! danger "Irreversible Operation"
    Dropping a keyspace **cannot be undone**. All data is permanently deleted.

!!! note "Automatic Snapshots"
    If `auto_snapshot: true` is set in `cassandra.yaml` (enabled by default), Cassandra automatically creates a snapshot before deleting data. Verify this setting before relying on automatic snapshots:

    ```yaml
    # cassandra.yaml
    auto_snapshot: true  # Default: true
    ```

    Automatic snapshots are stored in `<data_directory>/<keyspace>/<table>/snapshots/`. These can be used to restore data if needed, but should not be relied upon without verification—always confirm `auto_snapshot` is enabled in the cluster configuration.

### Parameters

#### IF EXISTS

Optional clause that prevents an error if the keyspace does not exist.

| Condition | Without IF EXISTS | With IF EXISTS |
|-----------|-------------------|----------------|
| Keyspace exists | Keyspace dropped | Keyspace dropped |
| Keyspace does not exist | Error | No error, no effect |

### Examples

#### Basic Drop

```sql
DROP KEYSPACE old_keyspace;
```

#### Safe Drop

```sql
DROP KEYSPACE IF EXISTS temp_keyspace;
```

#### With Prior Snapshot

```bash
# Create snapshot first
nodetool snapshot -t backup_before_drop my_keyspace

# Then drop
cqlsh -e "DROP KEYSPACE my_keyspace;"
```

### Restrictions

!!! warning "Restrictions"
    - Cannot drop system keyspaces (`system`, `system_schema`, `system_auth`, etc.)
    - Cannot drop a keyspace while connected to it via `USE` (disconnect first or use fully qualified names)
    - Requires appropriate permissions (DROP on keyspace or superuser)

### Notes

- Drop is a metadata operation; data files are deleted asynchronously
- Connected clients using the keyspace receive errors after drop
- Snapshots created before drop preserve data and can be restored
- If any table in the keyspace has a materialized view, the view is also dropped

---

## USE

Set the current working keyspace for the session.

### Synopsis

```cqlsyntax
USE *keyspace_name*
```

### Description

`USE` sets the default keyspace for subsequent CQL statements in the current session. After executing `USE`, table names can be specified without the keyspace prefix.

This is a session-level setting that does not affect other connections or persist across sessions.

### Parameters

#### *keyspace_name*

The name of an existing keyspace to use as the default.

### Examples

#### Set Default Keyspace

```sql
USE my_keyspace;

-- Now these are equivalent:
SELECT * FROM users;
SELECT * FROM my_keyspace.users;
```

#### Switch Keyspaces

```sql
USE keyspace_a;
SELECT * FROM table1;  -- Queries keyspace_a.table1

USE keyspace_b;
SELECT * FROM table1;  -- Queries keyspace_b.table1
```

#### Fully Qualified Names Override USE

```sql
USE keyspace_a;
SELECT * FROM keyspace_b.table1;  -- Queries keyspace_b despite USE
```

### Restrictions

!!! warning "Restrictions"
    - Keyspace must exist
    - No `IF EXISTS` clause available
    - Does not verify user has permissions on the keyspace (permissions checked on subsequent operations)

### Notes

- `USE` is primarily for interactive `cqlsh` sessions
- Application code should typically use fully qualified table names
- Driver connection configurations often specify default keyspace
- Using `USE` in application code can lead to subtle bugs if connections are pooled

!!! tip "Application Best Practice"
    In application code, prefer fully qualified table names (`keyspace.table`) over `USE` statements. This makes queries explicit and avoids issues with connection pooling where keyspace state might be unexpected.

---

## Related Documentation

- **[CREATE TABLE](table.md)** - Create tables within keyspaces
- **[Data Modeling](../../data-modeling/index.md)** - Keyspace design considerations
- **[Architecture: Replication](../../architecture/distributed-data/replication.md)** - How replication works
