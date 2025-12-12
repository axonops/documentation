---
description: "Cassandra application dashboard metrics mapping. Client request and latency metrics."
meta:
  - name: keywords
    content: "application metrics, client requests, latency metrics, Cassandra"
---

# AxonOps Application Dashboard Metrics Mapping

This document maps the metrics used in the AxonOps Application dashboard to their corresponding sources.

## Dashboard Overview

The Application dashboard provides visibility into client application interactions with Cassandra, including throughput metrics (reads, writes, batches) and connection information. It helps monitor application-level performance and usage patterns.

## Metrics Mapping

### Throughput Metrics

| Dashboard Metric | Source | Description | Attributes |
|-----------------|--------|-------------|------------|
| `client_throughput_read` | Client metrics | Read operations throughput | `username`, `remoteIP`, `keyspace`, `table`, `dc`, `rack`, `host_id` |
| `client_throughput_write` | Client metrics | Write operations throughput | `username`, `remoteIP`, `keyspace`, `table`, `dc`, `rack`, `host_id` |
| `client_throughput_batch_logged` | Client metrics | Logged batch operations | `username`, `remoteIP`, `keyspace`, `table`, `dc`, `rack`, `host_id` |
| `client_throughput_batch_counter` | Client metrics | Counter batch operations | `username`, `remoteIP`, `keyspace`, `table`, `dc`, `rack`, `host_id` |
| `client_throughput_batch_unlogged` | Client metrics | Unlogged batch operations | `username`, `remoteIP`, `keyspace`, `table`, `dc`, `rack`, `host_id` |

### Connection Metrics

| Dashboard Metric | Description | Attributes |
|-----------------|-------------|------------|
| `cas_Client_connectedNativeClients` | Number of connected native protocol clients | `dc`, `rack`, `host_id` |
| `cas_authentication_success` | Successful authentication attempts | `username`, `dc`, `rack`, `host_id` |

## Query Examples

### Reads per Second
```promql
sum by(remoteIP, username, keyspace, table) (client_throughput_read{axonfunction='rate',dc=~'$dc',rack=~'$rack',host_id=~'$host_id',keyspace=~'$keyspace', table=~'$scope'})
```

### Writes per Second
```promql
sum by (remoteIP, username, keyspace, table) (client_throughput_write{axonfunction='rate',dc=~'$dc',rack=~'$rack',host_id=~'$host_id',keyspace=~'$keyspace', table=~'$scope'})
```

### Logged Batches per Second
```promql
client_throughput_batch_logged{axonfunction='rate',dc=~'$dc',rack=~'$rack',host_id=~'$host_id',keyspace=~'$keyspace', table=~'$scope'}
```

### Native Connections
```promql
ceil(cas_Client_connectedNativeClients{dc=~'$dc',rack=~'$rack',host_id=~'$host_id'})
```

### Successful Authentications Rate
```promql
sum(cas_authentication_success{axonfunction='rate',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}) by (username)
```

## Panel Types and Descriptions

### Throughput Section
- **Reads/sec** - Line chart showing read operations per second by user, IP, keyspace, and table

- **Writes/sec** - Line chart showing write operations per second by user, IP, keyspace, and table

- **Batches/sec (logged)** - Line chart showing logged batch operations per second

- **Batches/sec (counter)** - Line chart showing counter batch operations per second

- **Batches/sec (unlogged)** - Line chart showing unlogged batch operations per second

### Connections Section
- **Native connections** - Line chart showing number of connected native protocol clients

- **Successful Authentications by user (rate)** - Line chart showing authentication success rate by username

## Filters

- **data center** (`dc`) - Filter by data center

- **rack** - Filter by rack

- **node** (`host_id`) - Filter by specific node

- **username** - Filter by client username

- **keyspace** - Filter by keyspace

- **table** (`scope`) - Filter by table

## Metric Details

### Client Throughput Metrics
- Track operations at the application level
- Include client identity (username, IP address)
- Provide keyspace and table level granularity
- Use `axonfunction='rate'` to calculate per-second rates

### Connection Metrics
- `connectedNativeClients` shows current connection count
- `authentication_success` tracks login attempts
- Both metrics help monitor client access patterns

## Legend Format

The dashboard uses descriptive legends combining multiple attributes:

- Throughput: `$username @ $remoteIP $keyspace $table`
- Connections: `$dc - $host_id`
- Authentication: `$username`

## Notes

1. Client throughput metrics provide application-level visibility not available in standard Cassandra metrics
2. These metrics help identify heavy users, problematic applications, or unusual access patterns
3. The `ceil()` function is used for connection counts to ensure whole numbers
4. Batch type separation (logged/unlogged/counter) helps monitor different write patterns
5. Remote IP tracking enables geographic or network-based analysis of client access