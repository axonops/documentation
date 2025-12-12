# AxonOps Workbench

AxonOps Workbench is an open-source desktop application for Apache Cassandra development. It provides a graphical interface for schema management, query execution, and data exploration without requiring command-line interaction.

---

## Overview

AxonOps Workbench simplifies Cassandra development by providing visual tools for common database tasks. Instead of writing CQL commands in a terminal, developers can browse schemas, execute queries, and export data through a modern graphical interface.

| Aspect | Description |
|--------|-------------|
| **Type** | Desktop application (GUI) |
| **License** | Apache License 2.0 (open source) |
| **Platforms** | Windows, macOS, Linux |
| **Source Code** | [github.com/axonops/axonops-workbench-cassandra](https://github.com/axonops/axonops-workbench-cassandra) |

---

## Key Features

### Connection Management

Manage connections to multiple Cassandra clusters from a single interface:

- Save connection profiles with host, port, credentials, and SSL settings
- Organize connections by environment (development, staging, production)
- Quick-switch between clusters without re-entering credentials
- Support for authentication (username/password)
- SSL/TLS connection support

### Schema Browser

Explore cluster schema through a visual tree structure:

- **Keyspaces** — View all keyspaces with replication settings
- **Tables** — Browse table structures, columns, and primary key definitions
- **Indexes** — View secondary indexes and their configurations
- **User-Defined Types** — Inspect UDT definitions and field types
- **Materialized Views** — Examine view definitions and base table relationships
- **Functions and Aggregates** — Browse user-defined functions

The schema browser provides immediate visibility into database structure without executing `DESCRIBE` commands.

### Query Editor

Write and execute CQL queries with development-focused features:

| Feature | Description |
|---------|-------------|
| **Syntax Highlighting** | CQL keywords, strings, and numbers are color-coded |
| **Auto-completion** | Context-aware suggestions for tables, columns, and keywords |
| **Query History** | Access previously executed queries |
| **Multi-query Execution** | Run multiple statements in sequence |
| **Query Formatting** | Auto-format CQL for readability |
| **Error Highlighting** | Visual indication of syntax errors |

### Result Visualization

View query results in a structured, interactive format:

- **Tabular Display** — Results shown in sortable, filterable tables
- **Column Resizing** — Adjust column widths for readability
- **Data Type Formatting** — Proper display of UUIDs, timestamps, collections, and blobs
- **Large Result Handling** — Pagination for queries returning many rows
- **NULL Visualization** — Clear distinction between NULL values and empty strings

### Data Export

Export query results and table data to various formats:

| Format | Use Case |
|--------|----------|
| **CSV** | Spreadsheet analysis, data import to other systems |
| **JSON** | Application integration, data transformation |
| **SQL/CQL** | Data migration, backup scripts |

### DDL Generation

Generate CQL statements from existing schema:

- Export `CREATE KEYSPACE` statements
- Export `CREATE TABLE` statements with all options
- Export `CREATE INDEX` statements
- Export `CREATE TYPE` statements for UDTs
- Useful for schema documentation and migration

---

## Installation

### Download

Download the appropriate installer from the [GitHub releases page](https://github.com/axonops/axonops-workbench-cassandra/releases):

| Platform | File Type |
|----------|-----------|
| **Windows** | `.exe` installer |
| **macOS** | `.dmg` disk image |
| **Linux** | `.AppImage`, `.deb`, or `.rpm` |

### System Requirements

| Component | Minimum |
|-----------|---------|
| **OS** | Windows 10+, macOS 10.14+, Ubuntu 18.04+ |
| **Memory** | 4 GB RAM |
| **Disk** | 500 MB available space |
| **Display** | 1280x720 resolution |

### First Launch

1. Install the application using the platform-appropriate method
2. Launch AxonOps Workbench
3. Create a new connection by providing cluster details
4. Connect and begin exploring the schema

---

## Use Cases

### Schema Design and Prototyping

During the data modeling phase, use Workbench to:

- Create and modify keyspaces with different replication strategies
- Design table schemas and iterate on primary key choices
- Add and remove columns as the model evolves
- Create indexes and evaluate their impact
- Test queries against the schema before committing to the design

### Ad-Hoc Query Execution

Execute queries without writing application code:

- Investigate data issues reported by users
- Validate data after migrations or imports
- Test query patterns before implementing in application
- Run one-off data corrections (with appropriate care)

### Data Exploration

Understand data distribution and content:

- Browse table contents to verify data quality
- Examine partition structures and clustering order
- Identify data anomalies or unexpected values
- Validate application behavior by inspecting written data

### Development Workflow Integration

Complement the application development process:

1. Design schema in Workbench
2. Export DDL statements
3. Implement application code using drivers
4. Use Workbench to verify application writes
5. Debug issues by examining actual data

### Documentation and Knowledge Transfer

Generate schema documentation:

- Export complete schema definitions
- Share connection profiles with team members
- Document data model decisions
- Onboard new developers with visual schema exploration

---

## Connecting to Cassandra

### Basic Connection

Create a connection with minimal settings:

| Setting | Value |
|---------|-------|
| **Name** | Descriptive name (e.g., "Local Dev Cluster") |
| **Host** | Cassandra node address (e.g., `127.0.0.1`) |
| **Port** | Native transport port (default: `9042`) |

### Authenticated Connection

For clusters with authentication enabled:

| Setting | Value |
|---------|-------|
| **Username** | Cassandra user |
| **Password** | User password |
| **Auth Provider** | Password Authenticator |

### SSL/TLS Connection

For encrypted connections:

| Setting | Description |
|---------|-------------|
| **Enable SSL** | Toggle SSL connection |
| **Truststore** | Path to truststore file (if required) |
| **Keystore** | Path to keystore file (for client certificates) |

### Connection to Specific Keyspace

Optionally specify a default keyspace:

| Setting | Value |
|---------|-------|
| **Default Keyspace** | Keyspace to select on connection |

This avoids prefixing table names with keyspace in queries.

---

## Query Execution

### Running Queries

1. Select the target keyspace from the schema browser or use `USE keyspace_name;`
2. Write the CQL query in the editor
3. Execute using the Run button or keyboard shortcut
4. View results in the results panel

### Query Examples

**Select with filtering:**
```cql
SELECT * FROM users WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;
```

**Aggregation:**
```cql
SELECT COUNT(*) FROM orders WHERE status = 'pending' ALLOW FILTERING;
```

**Schema inspection:**
```cql
DESCRIBE TABLE users;
```

### Handling Large Results

For queries returning many rows:

- Results are paginated automatically
- Use `LIMIT` to restrict result size
- Export large result sets to files rather than viewing in UI

---

## Best Practices

### Connection Security

- Store connection credentials securely
- Use SSL/TLS for production cluster connections
- Create read-only users for exploration to prevent accidental modifications
- Do not share connection profiles containing passwords

### Query Safety

- Always include `WHERE` clauses for `UPDATE` and `DELETE` operations
- Use `LIMIT` when exploring unfamiliar tables
- Test destructive queries in development environments first
- Review generated CQL before executing DDL changes

### Performance Considerations

- Avoid `SELECT *` on tables with many columns
- Use `LIMIT` to prevent fetching excessive data
- Be cautious with `ALLOW FILTERING` on large tables
- Consider query impact on production clusters

---

## Comparison with Other Tools

| Feature | AxonOps Workbench | cqlsh | DataStax Studio |
|---------|-------------------|-------|-----------------|
| **Interface** | GUI | CLI | Web |
| **Installation** | Desktop app | Python package | Server deployment |
| **Schema Browser** | Visual tree | Text commands | Visual |
| **Query Editor** | Rich editor | Basic readline | Rich editor |
| **Open Source** | Yes (Apache 2.0) | Yes | No |
| **Offline Use** | Yes | Yes | Requires server |

---

## Troubleshooting

### Connection Failures

**Cannot connect to cluster:**

1. Verify the host address and port are correct
2. Check that the Cassandra node is running and accepting connections
3. Verify firewall rules allow traffic on port 9042
4. For remote clusters, ensure the node's `rpc_address` is accessible

**Authentication failures:**

1. Verify username and password are correct
2. Confirm the user exists in Cassandra (`SELECT * FROM system_auth.roles`)
3. Check that authentication is enabled on the cluster

**SSL/TLS errors:**

1. Verify truststore contains the cluster's CA certificate
2. Check that SSL is enabled on the cluster
3. Confirm certificate validity and expiration

### Query Errors

**Timeout errors:**

- The query may be too expensive; add restrictions or limits
- Check cluster health and node availability
- Consider increasing client timeout settings

**Consistency errors:**

- Verify sufficient replicas are available for the requested consistency level
- Check cluster status with `nodetool status`

---

## Resources

- **GitHub Repository**: [github.com/axonops/axonops-workbench-cassandra](https://github.com/axonops/axonops-workbench-cassandra)
- **Releases**: [github.com/axonops/axonops-workbench-cassandra/releases](https://github.com/axonops/axonops-workbench-cassandra/releases)
- **Issues**: [github.com/axonops/axonops-workbench-cassandra/issues](https://github.com/axonops/axonops-workbench-cassandra/issues)
- **License**: [Apache License 2.0](https://github.com/axonops/axonops-workbench-cassandra/blob/main/LICENSE)

---

## Related Documentation

| Topic | Description |
|-------|-------------|
| [CQLAI](cqlai.md) | AI-powered command-line CQL shell |
| [CQL Reference](../cql/index.md) | CQL syntax and commands |
| [Drivers](drivers/index.md) | Application driver configuration |
| [cqlsh](../tools/cqlsh/index.md) | Standard CQL shell |
