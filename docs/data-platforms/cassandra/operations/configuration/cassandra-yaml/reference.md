# cassandra.yaml Reference

Comprehensive reference for cassandra.yaml configuration parameters, organized by category.

!!! note "Version Information"
    Covers Apache Cassandra 4.0, 4.1, and 5.0. "Not set" = commented out by default. "Auto" = calculated from system resources.

!!! info "Parameter Formats (4.1+)"
    Human-readable formats: `10s`, `500ms` (time); `256MiB`, `1GiB` (size)

## Table of Contents

- [Cluster Configuration](#cluster-configuration)
- [Network - Listen Addresses](#network---listen-addresses)
- [Network - RPC/Client](#network---rpcclient)
- [Network - Internode](#network---internode)
- [Seed Provider](#seed-provider)
- [Data Directories](#data-directories)
- [Hinted Handoff](#hinted-handoff)
- [Memtable Configuration](#memtable-configuration)
- [Commit Log](#commit-log)
- [Concurrent Operations](#concurrent-operations)
- [Compaction](#compaction)
- [Caching](#caching)
- [Snitch Configuration](#snitch-configuration)
- [Failure Detection](#failure-detection)
- [Request Timeouts](#request-timeouts)
- [Streaming](#streaming)
- [Security - Authentication](#security---authentication)
- [Security - Authorization](#security---authorization)
- [Security - Caching](#security---caching)
- [Security - Encryption](#security---encryption)
- [Disk Failure Policy](#disk-failure-policy)
- [Snapshots and Backups](#snapshots-and-backups)
- [Repair](#repair)
- [Change Data Capture (CDC)](#change-data-capture-cdc)
- [User Defined Functions](#user-defined-functions)
- [Garbage Collection Logging](#garbage-collection-logging)
- [Tombstones](#tombstones)
- [Batch Operations](#batch-operations)
- [Query Processing](#query-processing)
- [Indexing](#indexing)
- [Audit Logging](#audit-logging)
- [Tracing](#tracing)
- [Diagnostic Events](#diagnostic-events)
- [Index Summary](#index-summary)
- [Trickle Fsync](#trickle-fsync)
- [Windows](#windows)
- [Startup Checks](#startup-checks)
- [Client Error Reporting](#client-error-reporting)
- [Storage Compatibility](#storage-compatibility)
- [Dynamic Data Masking](#dynamic-data-masking)
- [Corrupted Tombstones](#corrupted-tombstones)
- [DNS](#dns)
- [Archive](#archive)
- [Heap Dump](#heap-dump)
- [Guardrails](#guardrails)

## Cluster Configuration

### cluster_name

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `'Test Cluster'` | 4.1: `'Test Cluster'` | 5.0: `'Test Cluster'`

The name of the cluster. This is mainly used to prevent machines in one logical cluster from joining another.

---

### num_tokens

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `16` | 4.1: `16` | 5.0: `16`

This defines the number of tokens randomly assigned to this node on the ring The more tokens, relative to other nodes, the larger the proportion of data that this node will store. You probably want all nodes to have the same number of tokens assuming they have equal hardware capability.

If you leave this unspecified, Cassandra will use the default of 1 token for legacy compatibility, and will use the initial_token as described below.

Specifying initial_token will override this setting on the node's initial start, on subsequent starts, this setting will apply even if initial token is set.

See https://cassandra.apache.org/doc/latest/getting_started/production.html#tokens for best practice information about num_tokens.

---

### allocate_tokens_for_keyspace

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `KEYSPACE` | 4.1: `KEYSPACE` | 5.0: `KEYSPACE`

Replica factor is determined via the replication strategy used by the specified keyspace.

---

### allocate_tokens_for_local_replication_factor

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `3` | 4.1: `3` | 5.0: `3`

Replica factor is explicitly set, regardless of keyspace or datacenter. This is the replica factor within the datacenter, like NTS.

---

### initial_token

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: Not set | 4.1: Not set | 5.0: Not set

initial_token allows you to specify tokens manually.  While you can use it with vnodes (num_tokens > 1, above) -- in which case you should provide a comma-separated list -- it's primarily used when adding nodes to legacy clusters that do not have vnodes enabled.

---

### partitioner

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `org.apache.cassandra.dht.Murmur3Partitioner` | 4.1: `org.apache.cassandra.dht.Murmur3Partitioner` | 5.0: `org.apache.cassandra.dht.Murmur3Partitioner`

The partitioner is responsible for distributing groups of rows (by partition key) across nodes in the cluster. The partitioner can NOT be changed without reloading all data.  If you are adding nodes or upgrading, you should set this to the same partitioner that you are currently using.

The default partitioner is the Murmur3Partitioner. Older partitioners such as the RandomPartitioner, ByteOrderedPartitioner, and OrderPreservingPartitioner have been included for backward compatibility only. For new clusters, you should NOT change this value.

---

### default_keyspace_rf

**Versions:** 4.1, 5.0

**Default:** 4.1: `1` | 5.0: `1`

**Impact on keyspace creation:** If replication factor is not mentioned as part of keyspace creation, default_keyspace_rf would apply. Changing this configuration would only take effect for keyspaces created after the change, but does not impact existing keyspaces created prior to the change.

**Impact on keyspace alter:** When altering a keyspace from NetworkTopologyStrategy to SimpleStrategy, default_keyspace_rf is applied if rf is not explicitly mentioned.

**Impact on system keyspaces:** This would also apply for any system keyspaces that need replication factor. A further note about system keyspaces - system_traces and system_distributed keyspaces take RF of 2 or default, whichever is higher, and system_auth keyspace takes RF of 1 or default, whichever is higher.

Suggested value for use in production: 3

---

## Network - Listen Addresses

### listen_address

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `localhost` | 4.1: `localhost` | 5.0: `localhost`

Address or interface to bind to and tell other Cassandra nodes to connect to. You _must_ change this if you want multiple nodes to be able to communicate!

Set listen_address OR listen_interface, not both.

Leaving it blank leaves it up to InetAddress.getLocalHost(). This will always do the Right Thing _if_ the node is properly configured (hostname, name resolution, etc), and the Right Thing is to use the address associated with the hostname (it might not be). If unresolvable it will fall back to InetAddress.getLoopbackAddress(), which is wrong for production systems.

Setting listen_address to 0.0.0.0 is always wrong.

---

### listen_interface

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `eth0` | 4.1: `eth0` | 5.0: `eth0`

Set listen_address OR listen_interface, not both. Interfaces must correspond to a single address, IP aliasing is not supported.

---

### listen_interface_prefer_ipv6

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `false` | 4.1: `false` | 5.0: `false`

If you choose to specify the interface by name and the interface has an ipv4 and an ipv6 address you can specify which should be chosen using listen_interface_prefer_ipv6. If false the first ipv4 address will be used. If true the first ipv6 address will be used. Defaults to false preferring ipv4. If there is only one address it will be selected regardless of ipv4/ipv6.

---

### broadcast_address

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `1.2.3.4` | 4.1: `1.2.3.4` | 5.0: `1.2.3.4`

Address to broadcast to other Cassandra nodes Leaving this blank will set it to the same value as listen_address

---

### listen_on_broadcast_address

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `false` | 4.1: `false` | 5.0: `false`

When using multiple physical network interfaces, set this to true to listen on broadcast_address in addition to the listen_address, allowing nodes to communicate in both interfaces. Ignore this property if the network configuration automatically routes  between the public and private networks such as EC2.

---

### storage_port

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `7000` | 4.1: `7000` | 5.0: `7000`

TCP port, for commands and data For security reasons, you should not expose this port to the internet.  Firewall it if needed.

---

### ssl_storage_port

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `7001` | 4.1: `7001` | 5.0: `7001`

SSL port, for legacy encrypted communication. This property is unused unless enabled in server_encryption_options (see below). As of cassandra 4.0, this property is deprecated as a single port can be used for either/both secure and insecure connections. For security reasons, you should not expose this port to the internet. Firewall it if needed.

---

## Network - RPC/Client

### rpc_address

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `localhost` | 4.1: `localhost` | 5.0: `localhost`

The address or interface to bind the native transport server to.

Set rpc_address OR rpc_interface, not both.

Leaving rpc_address blank has the same effect as on listen_address (i.e. it will be based on the configured hostname of the node).

Note that unlike listen_address, you can specify 0.0.0.0, but you must also set broadcast_rpc_address to a value other than 0.0.0.0.

For security reasons, you should not expose this port to the internet.  Firewall it if needed.

---

### rpc_interface

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `eth1` | 4.1: `eth0` | 5.0: `eth1`

Set rpc_address OR rpc_interface, not both. Interfaces must correspond to a single address, IP aliasing is not supported.

---

### rpc_interface_prefer_ipv6

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `false` | 4.1: `false` | 5.0: `false`

If you choose to specify the interface by name and the interface has an ipv4 and an ipv6 address you can specify which should be chosen using rpc_interface_prefer_ipv6. If false the first ipv4 address will be used. If true the first ipv6 address will be used. Defaults to false preferring ipv4. If there is only one address it will be selected regardless of ipv4/ipv6.

---

### broadcast_rpc_address

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `1.2.3.4` | 4.1: `1.2.3.4` | 5.0: `1.2.3.4`

RPC address to broadcast to drivers and other Cassandra nodes. This cannot be set to 0.0.0.0. If left blank, this will be set to the value of rpc_address. If rpc_address is set to 0.0.0.0, broadcast_rpc_address must be set.

---

### rpc_keepalive

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `true` | 4.1: `true` | 5.0: `true`

enable or disable keepalive on rpc/native connections

---

### start_native_transport

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `true` | 4.1: `true` | 5.0: `true`

Whether to start the native transport server. The address on which the native transport is bound is defined by rpc_address.

---

### native_transport_port

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `9042` | 4.1: `9042` | 5.0: `9042`

port for the CQL native transport to listen for clients on For security reasons, you should not expose this port to the internet.  Firewall it if needed.

---

### native_transport_port_ssl

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `9142` | 4.1: `9142` | 5.0: `9142`

Dedicated SSL port for native transport encryption.

Enabling encryption in `client_encryption_options` allows two modes:

- **Single port mode**: Keep `native_transport_port_ssl` disabled to use encryption on `native_transport_port`
- **Dual port mode**: Set `native_transport_port_ssl` to a different value to have encrypted and unencrypted ports

!!! warning "Deprecated"
    This feature is deprecated since Cassandra 5.0 and will be removed. See NEWS.txt deprecation section.

---

### native_transport_max_threads

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `128` | 4.1: `128` | 5.0: `128`

The maximum threads for handling requests (note that idle threads are stopped after 30 seconds so there is not corresponding minimum setting).

---

### native_transport_max_frame_size

**Versions:** 4.1, 5.0

**Default:** 4.1: `16MiB` | 5.0: `16MiB`

The maximum size of allowed frame. Frame (requests) larger than this will be rejected as invalid. The default is 16MiB. If you're changing this parameter, you may want to adjust max_value_size accordingly. This should be positive and less than 2048. Min unit: MiB

---

### native_transport_max_frame_size_in_mb

**Versions:** 4.0

**Default:** 4.0: `256`

The maximum size of allowed frame. Frame (requests) larger than this will be rejected as invalid. The default is 256MB. If you're changing this parameter, you may want to adjust max_value_size_in_mb accordingly. This should be positive and less than 2048.

---

### native_transport_max_concurrent_connections

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `-1` | 4.1: `-1` | 5.0: `-1`

The maximum number of concurrent client connections. The default is -1, which means unlimited.

---

### native_transport_max_concurrent_connections_per_ip

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `-1` | 4.1: `-1` | 5.0: `-1`

The maximum number of concurrent client connections per source ip. The default is -1, which means unlimited.

---

### native_transport_allow_older_protocols

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `true` | 4.1: `true` | 5.0: `true`

Controls whether Cassandra honors older, yet currently supported, protocol versions. The default is true, which means all supported protocols will be honored.

---

### native_transport_rate_limiting_enabled

**Versions:** 4.1, 5.0

**Default:** 4.1: `false` | 5.0: `false`

When enabled, limits the number of native transport requests dispatched for processing per second. Behavior once the limit has been breached depends on the value of THROW_ON_OVERLOAD specified in the STARTUP message sent by the client during connection establishment. (See section "4.1.1. STARTUP" in "CQL BINARY PROTOCOL v5".) With the THROW_ON_OVERLOAD flag enabled, messages that breach the limit are dropped, and an OverloadedException is thrown for the client to handle. When the flag is not enabled, the server will stop consuming messages from the channel/socket, putting backpressure on the client while already dispatched messages are processed.

---

### native_transport_max_requests_per_second

**Versions:** 4.1, 5.0

**Default:** 4.1: `1000000` | 5.0: `1000000`

No description available.

---

### native_transport_idle_timeout

**Versions:** 4.1, 5.0

**Default:** 4.1: `60000ms` | 5.0: `60000ms`

Controls when idle client connections are closed. Idle connections are ones that had neither reads nor writes for a time period.

Clients may implement heartbeats by sending OPTIONS native protocol message after a timeout, which will reset idle timeout timer on the server side. To close idle client connections, corresponding values for heartbeat intervals have to be set on the client side.

Idle connection timeouts are disabled by default. Min unit: ms

---

### native_transport_idle_timeout_in_ms

**Versions:** 4.0

**Default:** 4.0: `60000`

Controls when idle client connections are closed. Idle connections are ones that had neither reads nor writes for a time period.

Clients may implement heartbeats by sending OPTIONS native protocol message after a timeout, which will reset idle timeout timer on the server side. To close idle client connections, corresponding values for heartbeat intervals have to be set on the client side.

Idle connection timeouts are disabled by default.

---

### native_transport_flush_in_batches_legacy

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `false` | 4.1: `false` | 5.0: `false`

Use native transport TCP message coalescing. If on upgrade to 4.0 you found your throughput decreasing, and in particular you run an old kernel or have very fewer client connections, this option might be worth evaluating.

---

### native_transport_max_auth_threads

**Versions:** 5.0

**Default:** 5.0: `4`

The maximum threads for handling auth requests in a separate executor from main request executor. When set to 0, main executor for requests is used.

---

## Network - Internode

### internode_authenticator

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `org.apache.cassandra.auth.AllowAllInternodeAuthenticator` | 4.1: `org.apache.cassandra.auth.AllowAllInternodeAuthenticator` | 5.0: Not set

Internode authentication backend, implementing IInternodeAuthenticator; used to allow/disallow connections from peer nodes.

---

### internode_socket_send_buffer_size

**Versions:** 4.1, 5.0

**Default:** 4.1: Not set | 5.0: Not set

Uncomment to set socket buffer size for internode communication Note that when setting this, the buffer size is limited by net.core.wmem_max and when not setting it it is defined by net.ipv4.tcp_wmem See also: /proc/sys/net/core/wmem_max /proc/sys/net/core/rmem_max /proc/sys/net/ipv4/tcp_wmem /proc/sys/net/ipv4/tcp_wmem and 'man tcp' Min unit: B

---

### internode_socket_send_buffer_size_in_bytes

**Versions:** 4.0

**Default:** 4.0: Not set

Uncomment to set socket buffer size for internode communication Note that when setting this, the buffer size is limited by net.core.wmem_max and when not setting it it is defined by net.ipv4.tcp_wmem See also: /proc/sys/net/core/wmem_max /proc/sys/net/core/rmem_max /proc/sys/net/ipv4/tcp_wmem /proc/sys/net/ipv4/tcp_wmem and 'man tcp'

---

### internode_socket_receive_buffer_size

**Versions:** 4.1, 5.0

**Default:** 4.1: Not set | 5.0: Not set

Uncomment to set socket buffer size for internode communication Note that when setting this, the buffer size is limited by net.core.wmem_max and when not setting it it is defined by net.ipv4.tcp_wmem Min unit: B

---

### internode_socket_receive_buffer_size_in_bytes

**Versions:** 4.0

**Default:** 4.0: Not set

Uncomment to set socket buffer size for internode communication Note that when setting this, the buffer size is limited by net.core.wmem_max and when not setting it it is defined by net.ipv4.tcp_wmem

---

### internode_application_send_queue_capacity

**Versions:** 4.1, 5.0

**Default:** 4.1: `4MiB` | 5.0: `4MiB`

Global, per-endpoint and per-connection limits imposed on messages queued for delivery to other nodes and waiting to be processed on arrival from other nodes in the cluster.  These limits are applied to the on-wire size of the message being sent or received.

The basic per-link limit is consumed in isolation before any endpoint or global limit is imposed. Each node-pair has three links: urgent, small and large.  So any given node may have a maximum of N*3*(internode_application_send_queue_capacity+internode_application_receive_queue_capacity) messages queued without any coordination between them although in practice, with token-aware routing, only RF*tokens nodes should need to communicate with significant bandwidth.

The per-endpoint limit is imposed on all messages exceeding the per-link limit, simultaneously with the global limit, on all links to or from a single node in the cluster. The global limit is imposed on all messages exceeding the per-link limit, simultaneously with the per-endpoint limit, on all links to or from any node in the cluster.

Min unit: B

---

### internode_application_send_queue_capacity_in_bytes

**Versions:** 4.0

**Default:** 4.0: `4194304                       #4MiB`

Global, per-endpoint and per-connection limits imposed on messages queued for delivery to other nodes and waiting to be processed on arrival from other nodes in the cluster.  These limits are applied to the on-wire size of the message being sent or received.

The basic per-link limit is consumed in isolation before any endpoint or global limit is imposed. Each node-pair has three links: urgent, small and large.  So any given node may have a maximum of N*3*(internode_application_send_queue_capacity_in_bytes+internode_application_receive_queue_capacity_in_bytes) messages queued without any coordination between them although in practice, with token-aware routing, only RF*tokens nodes should need to communicate with significant bandwidth.

The per-endpoint limit is imposed on all messages exceeding the per-link limit, simultaneously with the global limit, on all links to or from a single node in the cluster. The global limit is imposed on all messages exceeding the per-link limit, simultaneously with the per-endpoint limit, on all links to or from any node in the cluster.

---

### internode_application_send_queue_reserve_endpoint_capacity

**Versions:** 4.1, 5.0

**Default:** 4.1: `128MiB` | 5.0: `128MiB`

No description available.

---

### internode_application_send_queue_reserve_endpoint_capacity_in_bytes

**Versions:** 4.0

**Default:** 4.0: `134217728    #128MiB`

No description available.

---

### internode_application_send_queue_reserve_global_capacity

**Versions:** 4.1, 5.0

**Default:** 4.1: `512MiB` | 5.0: `512MiB`

No description available.

---

### internode_application_send_queue_reserve_global_capacity_in_bytes

**Versions:** 4.0

**Default:** 4.0: `536870912      #512MiB`

No description available.

---

### internode_application_receive_queue_capacity

**Versions:** 4.1, 5.0

**Default:** 4.1: `4MiB` | 5.0: `4MiB`

No description available.

---

### internode_application_receive_queue_capacity_in_bytes

**Versions:** 4.0

**Default:** 4.0: `4194304                    #4MiB`

No description available.

---

### internode_application_receive_queue_reserve_endpoint_capacity

**Versions:** 4.1, 5.0

**Default:** 4.1: `128MiB` | 5.0: `128MiB`

No description available.

---

### internode_application_receive_queue_reserve_endpoint_capacity_in_bytes

**Versions:** 4.0

**Default:** 4.0: `134217728 #128MiB`

No description available.

---

### internode_application_receive_queue_reserve_global_capacity

**Versions:** 4.1, 5.0

**Default:** 4.1: `512MiB` | 5.0: `512MiB`

No description available.

---

### internode_application_receive_queue_reserve_global_capacity_in_bytes

**Versions:** 4.0

**Default:** 4.0: `536870912   #512MiB`

No description available.

---

### internode_tcp_connect_timeout

**Versions:** 4.1, 5.0

**Default:** 4.1: `2000ms` | 5.0: `2000ms`

Defensive settings for protecting Cassandra from true network partitions. See (CASSANDRA-14358) for details.

The amount of time to wait for internode tcp connections to establish. Min unit: ms

---

### internode_tcp_connect_timeout_in_ms

**Versions:** 4.0

**Default:** 4.0: `2000`

Defensive settings for protecting Cassandra from true network partitions. See (CASSANDRA-14358) for details.

The amount of time to wait for internode tcp connections to establish.

---

### internode_tcp_user_timeout

**Versions:** 4.1, 5.0

**Default:** 4.1: `30000ms` | 5.0: `30000ms`

The amount of time unacknowledged data is allowed on a connection before we throw out the connection Note this is only supported on Linux + epoll, and it appears to behave oddly above a setting of 30000 (it takes much longer than 30s) as of Linux 4.12. If you want something that high set this to 0 which picks up the OS default and configure the net.ipv4.tcp_retries2 sysctl to be ~8. Min unit: ms

---

### internode_tcp_user_timeout_in_ms

**Versions:** 4.0

**Default:** 4.0: `30000`

The amount of time unacknowledged data is allowed on a connection before we throw out the connection Note this is only supported on Linux + epoll, and it appears to behave oddly above a setting of 30000 (it takes much longer than 30s) as of Linux 4.12. If you want something that high set this to 0 which picks up the OS default and configure the net.ipv4.tcp_retries2 sysctl to be ~8.

---

### internode_streaming_tcp_user_timeout

**Versions:** 4.1, 5.0

**Default:** 4.1: `300000ms` | 5.0: `300000ms`

The amount of time unacknowledged data is allowed on a streaming connection. The default is 5 minutes. Increase it or set it to 0 in order to increase the timeout. Min unit: ms

---

### internode_streaming_tcp_user_timeout_in_ms

**Versions:** 4.0

**Default:** 4.0: `300000`

The amount of time unacknowledged data is allowed on a streaming connection. The default is 5 minutes. Increase it or set it to 0 in order to increase the timeout.

---

### internode_compression

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `dc` | 4.1: `dc` | 5.0: `dc`

internode_compression controls whether traffic between nodes is compressed. Can be:

all all traffic is compressed

dc traffic between different datacenters is compressed

none nothing is compressed.

---

### cross_node_timeout

**Versions:** 4.0

**Default:** 4.0: `true`

Enable operation timeout information exchange between nodes to accurately measure request timeouts.  If disabled, replicas will assume that requests were forwarded to them instantly by the coordinator, which means that under overload conditions we will waste that much extra time processing already-timed-out requests.

Warning: It is generally assumed that users have setup NTP on their clusters, and that clocks are modestly in sync, since this is a requirement for general correctness of last write wins.

---

### inter_dc_tcp_nodelay

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `false` | 4.1: `false` | 5.0: `false`

Enable or disable tcp_nodelay for inter-dc communication. Disabling it will result in larger (but fewer) network packets being sent, reducing overhead from the TCP protocol itself, at the cost of increasing latency if you block for cross-datacenter responses.

---

### internode_timeout

**Versions:** 4.1, 5.0

**Default:** 4.1: `true` | 5.0: `true`

Enable operation timeout information exchange between nodes to accurately measure request timeouts.  If disabled, replicas will assume that requests were forwarded to them instantly by the coordinator, which means that under overload conditions we will waste that much extra time processing already-timed-out requests.

Warning: It is generally assumed that users have setup NTP on their clusters, and that clocks are modestly in sync, since this is a requirement for general correctness of last write wins.

---

## Seed Provider

### seed_provider

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `(see below)` | 4.1: `(see below)` | 5.0: `(see below)`

Configures how the node discovers other nodes in the cluster.

```yaml
seed_provider:
  - class_name: org.apache.cassandra.locator.SimpleSeedProvider
    parameters:
      - seeds: "127.0.0.1:7000"
```

| Sub-parameter | Description |
|---------------|-------------|
| `class_name` | The seed provider class. Default: `SimpleSeedProvider` |
| `seeds` | Comma-separated list of seed node addresses (host:port) |

---

## Data Directories

### data_file_directories

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: Not set | 4.1: Not set | 5.0: Not set

Directories where Cassandra stores SSTable data files.

```yaml
data_file_directories:
  - /var/lib/cassandra/data
```

This is a list of directory paths. Cassandra will spread data evenly across all specified directories.

---

### commitlog_directory

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `/var/lib/cassandra/commitlog` | 4.1: `/var/lib/cassandra/commitlog` | 5.0: `/var/lib/cassandra/commitlog`

commit log.  when running on magnetic HDD, this should be a separate spindle than the data directories. If not set, the default directory is $CASSANDRA_HOME/data/commitlog.

---

### saved_caches_directory

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `/var/lib/cassandra/saved_caches` | 4.1: `/var/lib/cassandra/saved_caches` | 5.0: `/var/lib/cassandra/saved_caches`

saved caches If not set, the default directory is $CASSANDRA_HOME/data/saved_caches.

---

### hints_directory

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `/var/lib/cassandra/hints` | 4.1: `/var/lib/cassandra/hints` | 5.0: `/var/lib/cassandra/hints`

Directory where Cassandra should store hints. If not set, the default directory is $CASSANDRA_HOME/data/hints.

---

### cdc_raw_directory

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `/var/lib/cassandra/cdc_raw` | 4.1: `/var/lib/cassandra/cdc_raw` | 5.0: `/var/lib/cassandra/cdc_raw`

CommitLogSegments are moved to this directory on flush if cdc_enabled: true and the segment contains mutations for a CDC-enabled table. This should be placed on a separate spindle than the data directories. If not set, the default directory is $CASSANDRA_HOME/data/cdc_raw.

---

### local_system_data_file_directory

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: Not set | 4.1: Not set | 5.0: Not set

Directory were Cassandra should store the data of the local system keyspaces. By default Cassandra will store the data of the local system keyspaces in the first of the data directories specified by data_file_directories. This approach ensures that if one of the other disks is lost Cassandra can continue to operate. For extra security this setting allows to store those data on a different directory that provides redundancy.

---

## Hinted Handoff

### hinted_handoff_enabled

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `true` | 4.1: `true` | 5.0: `true`

May either be "true" or "false" to enable globally

---

### max_hint_window

**Versions:** 4.1, 5.0

**Default:** 4.1: `3h` | 5.0: `3h`

this defines the maximum amount of time a dead host will have hints generated.  After it has been dead this long, new hints for it will not be created until it has been seen alive and gone down again. Min unit: ms

---

### max_hint_window_in_ms

**Versions:** 4.0

**Default:** 4.0: `10800000`

this defines the maximum amount of time a dead host will have hints generated.  After it has been dead this long, new hints for it will not be created until it has been seen alive and gone down again.

---

### hinted_handoff_disabled_datacenters

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: Not set | 4.1: Not set | 5.0: Not set

When hinted_handoff_enabled is true, a black list of data centers that will not perform hinted handoff

---

### max_hints_delivery_threads

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `2` | 4.1: `2` | 5.0: `2`

Number of threads with which to deliver hints; Consider increasing this number when you have multi-dc deployments, since cross-dc handoff tends to be slower

---

### hints_flush_period

**Versions:** 4.1, 5.0

**Default:** 4.1: `10000ms` | 5.0: `10000ms`

How often hints should be flushed from the internal buffers to disk. Will *not* trigger fsync. Min unit: ms

---

### hints_flush_period_in_ms

**Versions:** 4.0

**Default:** 4.0: `10000`

How often hints should be flushed from the internal buffers to disk. Will *not* trigger fsync.

---

### max_hints_file_size

**Versions:** 4.1, 5.0

**Default:** 4.1: `128MiB` | 5.0: `128MiB`

Maximum size for a single hints file, in mebibytes. Min unit: MiB

---

### max_hints_file_size_in_mb

**Versions:** 4.0

**Default:** 4.0: `128`

Maximum size for a single hints file, in megabytes.

---

### hint_window_persistent_enabled

**Versions:** 4.1, 5.0

**Default:** 4.1: `true` | 5.0: `true`

Enable / disable persistent hint windows.

If set to false, a hint will be stored only in case a respective node that hint is for is down less than or equal to max_hint_window.

If set to true, a hint will be stored in case there is not any hint which was stored earlier than max_hint_window. This is for cases when a node keeps to restart and hints are not delivered yet, we would be saving hints for that node indefinitely.

Defaults to true.

---

### auto_hints_cleanup_enabled

**Versions:** 4.1, 5.0

**Default:** 4.1: `false` | 5.0: `false`

Enable / disable automatic cleanup for the expired and orphaned hints file. Disable the option in order to preserve those hints on the disk.

---

### hinted_handoff_throttle

**Versions:** 4.1, 5.0

**Default:** 4.1: `1024KiB` | 5.0: `1024KiB`

Maximum throttle in KiBs per second, per delivery thread.  This will be reduced proportionally to the number of nodes in the cluster.  (If there are two nodes in the cluster, each delivery thread will use the maximum rate; if there are three, each will throttle to half of the maximum, since we expect two nodes to be delivering hints simultaneously.) Min unit: KiB

---

### hinted_handoff_throttle_in_kb

**Versions:** 4.0

**Default:** 4.0: `1024`

Maximum throttle in KBs per second, per delivery thread.  This will be reduced proportionally to the number of nodes in the cluster.  (If there are two nodes in the cluster, each delivery thread will use the maximum rate; if there are three, each will throttle to half of the maximum, since we expect two nodes to be delivering hints simultaneously.)

---

### hints_compression

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: Not set | 4.1: Not set | 5.0: Not set

Configures compression for hint files.

```yaml
hints_compression:
  - class_name: LZ4Compressor
```

Same compression options as `commitlog_compression`.

---

### transfer_hints_on_decommission

**Versions:** 4.1, 5.0

**Default:** 4.1: `true` | 5.0: `true`

Enable/disable transfering hints to a peer during decommission. Even when enabled, this does not guarantee consistency for logged batches, and it may delay decommission when coupled with a strict hinted_handoff_throttle. Default: true

---

### max_hints_size_per_host

**Versions:** 4.1, 5.0

**Default:** 4.1: `0MiB` | 5.0: `0MiB`

The file size limit to store hints for an unreachable host, in mebibytes. Once the local hints files have reached the limit, no more new hints will be created. Set a non-positive value will disable the size limit.

---

## Memtable Configuration

### memtable_allocation_type

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `heap_buffers` | 4.1: `heap_buffers` | 5.0: `heap_buffers`

Specify the way Cassandra allocates and manages memtable memory. Options are:

heap_buffers on heap nio buffers

offheap_buffers off heap (direct) nio buffers

offheap_objects off heap objects

---

### memtable_heap_space

**Versions:** 4.1, 5.0

**Default:** 4.1: `2048MiB` | 5.0: `2048MiB`

Total permitted memory to use for memtables. Cassandra will stop accepting writes when the limit is exceeded until a flush completes, and will trigger a flush based on memtable_cleanup_threshold If omitted, Cassandra will set both to 1/4 the size of the heap. Min unit: MiB

---

### memtable_heap_space_in_mb

**Versions:** 4.0

**Default:** 4.0: `2048`

Total permitted memory to use for memtables. Cassandra will stop accepting writes when the limit is exceeded until a flush completes, and will trigger a flush based on memtable_cleanup_threshold If omitted, Cassandra will set both to 1/4 the size of the heap.

---

### memtable_offheap_space

**Versions:** 4.1, 5.0

**Default:** 4.1: `2048MiB` | 5.0: `2048MiB`

Min unit: MiB

---

### memtable_offheap_space_in_mb

**Versions:** 4.0

**Default:** 4.0: `2048`

No description available.

---

### memtable_cleanup_threshold

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `0.11` | 4.1: `0.11` | 5.0: `0.11`

memtable_cleanup_threshold is deprecated. The default calculation is the only reasonable choice. See the comments on  memtable_flush_writers for more information.

Ratio of occupied non-flushing memtable size to total permitted size that will trigger a flush of the largest memtable. Larger mct will mean larger flushes and hence less compaction, but also less concurrent flush activity which can make it difficult to keep your disks fed under heavy write load.

memtable_cleanup_threshold defaults to 1 / (memtable_flush_writers + 1)

---

### memtable_flush_writers

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `2` | 4.1: `2` | 5.0: `2`

This sets the number of memtable flush writer threads per disk as well as the total number of memtables that can be flushed concurrently. These are generally a combination of compute and IO bound.

Memtable flushing is more CPU efficient than memtable ingest and a single thread can keep up with the ingest rate of a whole server on a single fast disk until it temporarily becomes IO bound under contention typically with compaction. At that point you need multiple flush threads. At some point in the future it may become CPU bound all the time.

You can tell if flushing is falling behind using the MemtablePool.BlockedOnAllocation metric which should be 0, but will be non-zero if threads are blocked waiting on flushing to free memory.

memtable_flush_writers defaults to two for a single data directory. This means that two  memtables can be flushed concurrently to the single data directory. If you have multiple data directories the default is one memtable flushing at a time but the flush will use a thread per data directory so you will get two or more writers.

Two is generally enough to flush on a fast disk [array] mounted as a single data directory. Adding more flush writers will result in smaller more frequent flushes that introduce more compaction overhead.

There is a direct tradeoff between number of memtables that can be flushed concurrently and flush size and frequency. More is not better you just need enough flush writers to never stall waiting for flushing to free memory.

---

### flush_compression

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `fast` | 4.1: `fast` | 5.0: `fast`

was the pre 4.0 behavior.

---

### memtable

**Versions:** 5.0

**Default:** 5.0: `(see below)`

Configures memtable implementation.

```yaml
memtable:
  configurations:
    default:
      class_name: TrieMemtable
```

**Implementations:** `SkipListMemtable` (legacy), `TrieMemtable` (reduced GC, better throughput)

---

## Commit Log

### commitlog_sync

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `periodic` | 4.1: `periodic` | 5.0: `periodic`

the default option is "periodic" where writes may be acked immediately and the CommitLog is simply synced every commitlog_sync_period_in_ms milliseconds.

---

### commitlog_sync_batch_window_in_ms

**Versions:** 4.0, 4.1

**Default:** 4.0: `2` | 4.1: `2`

commitlog_sync may be either "periodic", "group", or "batch."

When in batch mode, Cassandra won't ack writes until the commit log has been flushed to disk.  Each incoming write will trigger the flush task. commitlog_sync_batch_window_in_ms is a deprecated value. Previously it had almost no value, and is being removed.

---

### commitlog_sync_group_window

**Versions:** 4.1, 5.0

**Default:** 4.1: `1000ms` | 5.0: `1000ms`

commitlog_sync may be either "periodic", "group", or "batch."

When in batch mode, Cassandra won't ack writes until the commit log has been flushed to disk.  Each incoming write will trigger the flush task.

group mode is similar to batch mode, where Cassandra will not ack writes until the commit log has been flushed to disk. The difference is group mode will wait up to commitlog_sync_group_window between flushes.

Min unit: ms

---

### commitlog_sync_group_window_in_ms

**Versions:** 4.0

**Default:** 4.0: `1000`

group mode is similar to batch mode, where Cassandra will not ack writes until the commit log has been flushed to disk. The difference is group mode will wait up to commitlog_sync_group_window_in_ms between flushes.

---

### commitlog_sync_period

**Versions:** 4.1, 5.0

**Default:** 4.1: `10000ms` | 5.0: `10000ms`

Min unit: ms

---

### commitlog_sync_period_in_ms

**Versions:** 4.0

**Default:** 4.0: `10000`

No description available.

---

### commitlog_segment_size

**Versions:** 4.1, 5.0

**Default:** 4.1: `32MiB` | 5.0: `32MiB`

The size of the individual commitlog file segments.  A commitlog segment may be archived, deleted, or recycled once all the data in it (potentially from each columnfamily in the system) has been flushed to sstables.

The default size is 32, which is almost always fine, but if you are archiving commitlog segments (see commitlog_archiving.properties), then you probably want a finer granularity of archiving; 8 or 16 MB is reasonable. Max mutation size is also configurable via max_mutation_size setting in cassandra.yaml. The default is half the size commitlog_segment_size in bytes. This should be positive and less than 2048.

NOTE: If max_mutation_size is set explicitly then commitlog_segment_size must be set to at least twice the size of max_mutation_size

Min unit: MiB

---

### commitlog_segment_size_in_mb

**Versions:** 4.0

**Default:** 4.0: `32`

The size of the individual commitlog file segments.  A commitlog segment may be archived, deleted, or recycled once all the data in it (potentially from each columnfamily in the system) has been flushed to sstables.

The default size is 32, which is almost always fine, but if you are archiving commitlog segments (see commitlog_archiving.properties), then you probably want a finer granularity of archiving; 8 or 16 MB is reasonable. Max mutation size is also configurable via max_mutation_size_in_kb setting in cassandra.yaml. The default is half the size commitlog_segment_size_in_mb * 1024. This should be positive and less than 2048.

NOTE: If max_mutation_size_in_kb is set explicitly then commitlog_segment_size_in_mb must be set to at least twice the size of max_mutation_size_in_kb / 1024

---

### commitlog_compression

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: Not set | 4.1: Not set | 5.0: Not set

Configures compression for commit log segments.

```yaml
commitlog_compression:
  - class_name: LZ4Compressor
    parameters:
```

| Sub-parameter | Description |
|---------------|-------------|
| `class_name` | `LZ4Compressor`, `SnappyCompressor`, `DeflateCompressor`, or `ZstdCompressor` |
| `parameters` | Algorithm-specific parameters (optional) |

---

### commitlog_total_space

**Versions:** 4.1, 5.0

**Default:** 4.1: `8192MiB` | 5.0: `8192MiB`

Total space to use for commit logs on disk.

If space gets above this value, Cassandra will flush every dirty CF in the oldest segment and remove it.  So a small total commitlog space will tend to cause more flush activity on less-active columnfamilies.

The default value is the smaller of 8192, and 1/4 of the total space of the commitlog volume.

---

### commitlog_total_space_in_mb

**Versions:** 4.0

**Default:** 4.0: `8192`

Total space to use for commit logs on disk.

If space gets above this value, Cassandra will flush every dirty CF in the oldest segment and remove it.  So a small total commitlog space will tend to cause more flush activity on less-active columnfamilies.

The default value is the smaller of 8192, and 1/4 of the total space of the commitlog volume.

---

### commitlog_disk_access_mode

**Versions:** 5.0

**Default:** 5.0: `legacy`

Set the disk access mode for writing commitlog segments. The allowed values are: - auto: version dependent optimal setting - legacy: the default mode as used in Cassandra 4.x and earlier (standard I/O when the commitlog is either compressed or encrypted or mmap otherwise) - mmap: use memory mapped I/O - available only when the commitlog is neither compressed nor encrypted - direct: use direct I/O - available only when the commitlog is neither compressed nor encrypted - standard: use standard I/O - available only when the commitlog is compressed or encrypted The default setting is legacy when the storage compatibility is set to 4 or auto otherwise.

---

### periodic_commitlog_sync_lag_block

**Versions:** 4.1, 5.0

**Default:** 4.1: Not set | 5.0: Not set

When in periodic commitlog mode, the number of milliseconds to block writes while waiting for a slow disk flush to complete. Min unit: ms

---

### periodic_commitlog_sync_lag_block_in_ms

**Versions:** 4.0

**Default:** 4.0: Not set

When in periodic commitlog mode, the number of milliseconds to block writes while waiting for a slow disk flush to complete.

---

## Concurrent Operations

### concurrent_reads

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `32` | 4.1: `32` | 5.0: `32`

For workloads with more data than can fit in memory, Cassandra's bottleneck will be reads that need to fetch data from disk. "concurrent_reads" should be set to (16 * number_of_drives) in order to allow the operations to enqueue low enough in the stack that the OS and drives can reorder them. Same applies to "concurrent_counter_writes", since counter writes read the current values before incrementing and writing them back.

On the other hand, since writes are almost never IO bound, the ideal number of "concurrent_writes" is dependent on the number of cores in your system; (8 * number_of_cores) is a good rule of thumb.

---

### concurrent_writes

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `32` | 4.1: `32` | 5.0: `32`

No description available.

---

### concurrent_counter_writes

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `32` | 4.1: `32` | 5.0: `32`

No description available.

---

### concurrent_materialized_view_writes

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `32` | 4.1: `32` | 5.0: `32`

For materialized view writes, as there is a read involved, so this should be limited by the less of concurrent reads or concurrent writes.

---

### concurrent_compactors

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `1` | 4.1: `1` | 5.0: `1`

Number of simultaneous compactions to allow, NOT including validation "compactions" for anti-entropy repair.  Simultaneous compactions can help preserve read performance in a mixed read/write workload, by mitigating the tendency of small sstables to accumulate during a single long running compactions. The default is usually fine and if you experience problems with compaction running too slowly or too fast, you should look at compaction_throughput_mb_per_sec first.

concurrent_compactors defaults to the smaller of (number of disks, number of cores), with a minimum of 2 and a maximum of 8.

If your data directories are backed by SSD, you should increase this to the number of cores.

---

### concurrent_validations

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `0` | 4.1: `0` | 5.0: `0`

Number of simultaneous repair validations to allow. If not set or set to a value less than 1, it defaults to the value of concurrent_compactors. To set a value greeater than concurrent_compactors at startup, the system property cassandra.allow_unlimited_concurrent_validations must be set to true. To dynamically resize to a value > concurrent_compactors on a running node, first call the bypassConcurrentValidatorsLimit method on the org.apache.cassandra.db:type=StorageService mbean

---

### concurrent_materialized_view_builders

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `1` | 4.1: `1` | 5.0: `1`

Number of simultaneous materialized view builder tasks to allow.

---

### concurrent_merkle_tree_requests

**Versions:** 4.1, 5.0

**Default:** 4.1: `0` | 5.0: `0`

The number of simultaneous Merkle tree requests during repairs that can be performed by a repair command. The size of each validation request is limited by the repair_session_space property, so setting this to 1 will make sure that a repair command doesn't exceed that limit, even if the repair command is repairing multiple tables or multiple virtual nodes.

There isn't a limit by default for backwards compatibility, but this can produce OOM for  commands repairing multiple tables or multiple virtual nodes. A limit of just 1 simultaneous Merkle tree request is generally recommended with no virtual nodes so repair_session_space, and thereof the Merkle tree resolution, can be high. For virtual nodes a value of 1 with the default repair_session_space value will produce higher resolution Merkle trees at the expense of speed. Alternatively, when working with virtual nodes it can make sense to reduce the repair_session_space and increase the value of concurrent_merkle_tree_requests because each range will contain fewer data.

For more details see https://issues.apache.org/jira/browse/CASSANDRA-19336.

A zero value means no limit.

---

## Compaction

### compaction_throughput

**Versions:** 4.1, 5.0

**Default:** 4.1: `64MiB/s` | 5.0: `64MiB/s`

Throttles compaction to the given total throughput across the entire system. The faster you insert data, the faster you need to compact in order to keep the sstable count down, but in general, setting this to 16 to 32 times the rate you are inserting data is more than sufficient. Setting this to 0 disables throttling. Note that this accounts for all types of compaction, including validation compaction (building Merkle trees for repairs).

---

### compaction_throughput_mb_per_sec

**Versions:** 4.0

**Default:** 4.0: `64`

Throttles compaction to the given total throughput across the entire system. The faster you insert data, the faster you need to compact in order to keep the sstable count down, but in general, setting this to 16 to 32 times the rate you are inserting data is more than sufficient. Setting this to 0 disables throttling. Note that this accounts for all types of compaction, including validation compaction (building Merkle trees for repairs).

---

### compaction_large_partition_warning_threshold

**Versions:** 4.1

**Default:** 4.1: `100MiB`

Log a warning when compacting partitions larger than this value

---

### compaction_large_partition_warning_threshold_mb

**Versions:** 4.0

**Default:** 4.0: `100`

Log a warning when compacting partitions larger than this value

---

### compaction_tombstone_warning_threshold

**Versions:** 4.1

**Default:** 4.1: `100000`

Log a warning when writing more tombstones than this value to a partition

---

### sstable_preemptive_open_interval

**Versions:** 4.1, 5.0

**Default:** 4.1: `50MiB` | 5.0: `50MiB`

When compacting, the replacement sstable(s) can be opened before they are completely written, and used in place of the prior sstables for any range that has been written. This helps to smoothly transfer reads between the sstables, reducing page cache churn and keeping hot rows hot Set sstable_preemptive_open_interval to null for disabled which is equivalent to sstable_preemptive_open_interval_in_mb being negative Min unit: MiB

---

### sstable_preemptive_open_interval_in_mb

**Versions:** 4.0

**Default:** 4.0: `50`

When compacting, the replacement sstable(s) can be opened before they are completely written, and used in place of the prior sstables for any range that has been written. This helps to smoothly transfer reads between the sstables, reducing page cache churn and keeping hot rows hot

---

### uuid_sstable_identifiers_enabled

**Versions:** 4.1, 5.0

**Default:** 4.1: `false` | 5.0: `false`

Starting from 4.1 sstables support UUID based generation identifiers. They are disabled by default because once enabled, there is no easy way to downgrade. When the node is restarted with this option set to true, each newly created sstable will have a UUID based generation identifier and such files are not readable by previous Cassandra versions. At some point, this option will become true by default and eventually get removed from the configuration.

---

### automatic_sstable_upgrade

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `false` | 4.1: `false` | 5.0: `false`

Automatically upgrade sstables after upgrade - if there is no ordinary compaction to do, the oldest non-upgraded sstable will get upgraded to the latest version

---

### default_compaction

**Versions:** 5.0

**Default:** 5.0: Not set

Default compaction strategy applied when a table doesn't specify compaction. Also applies to system tables.

```yaml
default_compaction:
  class_name: SizeTieredCompactionStrategy
  parameters:
    min_threshold: 4
    max_threshold: 32
```

| Sub-parameter | Description | Default |
|---------------|-------------|---------|
| `class_name` | Compaction strategy class | `SizeTieredCompactionStrategy` |
| `min_threshold` | Minimum SSTables to trigger compaction | `4` |
| `max_threshold` | Maximum SSTables to compact at once | `32` |

If not specified, defaults to `SizeTieredCompactionStrategy` with default parameters.

---

### max_concurrent_automatic_sstable_upgrades

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `1` | 4.1: `1` | 5.0: `1`

Limit the number of concurrent sstable upgrades

---

## Caching

### key_cache_size

**Versions:** 4.1, 5.0

**Default:** 4.1: `Auto` | 5.0: `Auto`

Maximum size of the key cache in memory.

Each key cache hit saves 1 seek and each row cache hit saves 2 seeks at the minimum, sometimes more. The key cache is fairly tiny for the amount of time it saves, so it's worthwhile to use it at large numbers. The row cache saves even more time, but must contain the entire row, so it is extremely space-intensive. It's best to only use the row cache if you have hot rows or static rows.

NOTE: if you reduce the size, you may not get you hottest keys loaded on startup.

Default value is empty to make it "auto" (min(5% of Heap (in MiB), 100MiB)). Set to 0 to disable key cache.

This is only relevant to SSTable formats that use key cache, e.g. BIG. Min unit: MiB

---

### key_cache_size_in_mb

**Versions:** 4.0

**Default:** 4.0: `Auto`

Maximum size of the key cache in memory.

Each key cache hit saves 1 seek and each row cache hit saves 2 seeks at the minimum, sometimes more. The key cache is fairly tiny for the amount of time it saves, so it's worthwhile to use it at large numbers. The row cache saves even more time, but must contain the entire row, so it is extremely space-intensive. It's best to only use the row cache if you have hot rows or static rows.

NOTE: if you reduce the size, you may not get you hottest keys loaded on startup.

Default value is empty to make it "auto" (min(5% of Heap (in MB), 100MB)). Set to 0 to disable key cache.

---

### key_cache_save_period

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `14400` | 4.1: `4h` | 5.0: `4h`

Duration in seconds after which Cassandra should save the key cache. Caches are saved to saved_caches_directory as specified in this configuration file.

Saved caches greatly improve cold-start speeds, and is relatively cheap in terms of I/O for the key cache. Row cache saving is much more expensive and has limited use.

This is only relevant to SSTable formats that use key cache, e.g. BIG. Default is 14400 or 4 hours. Min unit: s

---

### key_cache_keys_to_save

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `100` | 4.1: `100` | 5.0: `100`

Number of keys from the key cache to save Disabled by default, meaning all keys are going to be saved This is only relevant to SSTable formats that use key cache, e.g. BIG.

---

### row_cache_size

**Versions:** 4.1, 5.0

**Default:** 4.1: `0MiB` | 5.0: `0MiB`

Maximum size of the row cache in memory. Please note that OHC cache implementation requires some additional off-heap memory to manage the map structures and some in-flight memory during operations before/after cache entries can be accounted against the cache capacity. This overhead is usually small compared to the whole capacity. Do not specify more memory that the system can afford in the worst usual situation and leave some headroom for OS block level cache. Do never allow your system to swap.

Default value is 0, to disable row caching. Min unit: MiB

---

### row_cache_size_in_mb

**Versions:** 4.0

**Default:** 4.0: `0`

Maximum size of the row cache in memory. Please note that OHC cache implementation requires some additional off-heap memory to manage the map structures and some in-flight memory during operations before/after cache entries can be accounted against the cache capacity. This overhead is usually small compared to the whole capacity. Do not specify more memory that the system can afford in the worst usual situation and leave some headroom for OS block level cache. Do never allow your system to swap.

Default value is 0, to disable row caching.

---

### row_cache_save_period

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `0` | 4.1: `0s` | 5.0: `0s`

Duration in seconds after which Cassandra should save the row cache. Caches are saved to saved_caches_directory as specified in this configuration file.

Saved caches greatly improve cold-start speeds, and is relatively cheap in terms of I/O for the key cache. Row cache saving is much more expensive and has limited use.

Default is 0 to disable saving the row cache. Min unit: s

---

### row_cache_keys_to_save

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `100` | 4.1: `100` | 5.0: `100`

Number of keys from the row cache to save. Specify 0 (which is the default), meaning all keys are going to be saved

---

### row_cache_class_name

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `org.apache.cassandra.cache.OHCProvider` | 4.1: `org.apache.cassandra.cache.OHCProvider` | 5.0: `org.apache.cassandra.cache.OHCProvider`

Row cache implementation class name. Available implementations:

org.apache.cassandra.cache.OHCProvider Fully off-heap row cache implementation (default).

org.apache.cassandra.cache.SerializingCacheProvider This is the row cache implementation availabile in previous releases of Cassandra.

---

### counter_cache_size

**Versions:** 4.1, 5.0

**Default:** 4.1: `Auto` | 5.0: `Auto`

Maximum size of the counter cache in memory.

Counter cache helps to reduce counter locks' contention for hot counter cells. In case of RF = 1 a counter cache hit will cause Cassandra to skip the read before write entirely. With RF > 1 a counter cache hit will still help to reduce the duration of the lock hold, helping with hot counter cell updates, but will not allow skipping the read entirely. Only the local (clock, count) tuple of a counter cell is kept in memory, not the whole counter, so it's relatively cheap.

NOTE: if you reduce the size, you may not get you hottest keys loaded on startup.

Default value is empty to make it "auto" (min(2.5% of Heap (in MiB), 50MiB)). Set to 0 to disable counter cache. NOTE: if you perform counter deletes and rely on low gcgs, you should disable the counter cache. Min unit: MiB

---

### counter_cache_size_in_mb

**Versions:** 4.0

**Default:** 4.0: `Auto`

Maximum size of the counter cache in memory.

Counter cache helps to reduce counter locks' contention for hot counter cells. In case of RF = 1 a counter cache hit will cause Cassandra to skip the read before write entirely. With RF > 1 a counter cache hit will still help to reduce the duration of the lock hold, helping with hot counter cell updates, but will not allow skipping the read entirely. Only the local (clock, count) tuple of a counter cell is kept in memory, not the whole counter, so it's relatively cheap.

NOTE: if you reduce the size, you may not get you hottest keys loaded on startup.

Default value is empty to make it "auto" (min(2.5% of Heap (in MB), 50MB)). Set to 0 to disable counter cache. NOTE: if you perform counter deletes and rely on low gcgs, you should disable the counter cache.

---

### counter_cache_save_period

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `7200` | 4.1: `7200s` | 5.0: `7200s`

Duration in seconds after which Cassandra should save the counter cache (keys only). Caches are saved to saved_caches_directory as specified in this configuration file.

Default is 7200 or 2 hours. Min unit: s

---

### counter_cache_keys_to_save

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `100` | 4.1: `100` | 5.0: `100`

Number of keys from the counter cache to save Disabled by default, meaning all keys are going to be saved

---

### cache_load_timeout

**Versions:** 4.1, 5.0

**Default:** 4.1: `30s` | 5.0: `30s`

Number of seconds the server will wait for each cache (row, key, etc ...) to load while starting the Cassandra process. Setting this to zero is equivalent to disabling all cache loading on startup while still having the cache during runtime. Min unit: s

---

### cache_load_timeout_seconds

**Versions:** 4.0

**Default:** 4.0: `30`

Number of seconds the server will wait for each cache (row, key, etc ...) to load while starting the Cassandra process. Setting this to a negative value is equivalent to disabling all cache loading on startup while still having the cache during runtime.

---

### file_cache_enabled

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `false` | 4.1: `false` | 5.0: `false`

Enable the sstable chunk cache.  The chunk cache will store recently accessed sections of the sstable in-memory as uncompressed buffers.

---

### file_cache_size

**Versions:** 4.1, 5.0

**Default:** 4.1: `512MiB` | 5.0: `512MiB`

Maximum memory to use for sstable chunk cache and buffer pooling. 32MB of this are reserved for pooling buffers, the rest is used for chunk cache that holds uncompressed sstable chunks. Defaults to the smaller of 1/4 of heap or 512MB. This pool is allocated off-heap, so is in addition to the memory allocated for heap. The cache also has on-heap overhead which is roughly 128 bytes per chunk (i.e. 0.2% of the reserved size if the default 64k chunk size is used). Memory is only allocated when needed. Min unit: MiB

---

### file_cache_size_in_mb

**Versions:** 4.0

**Default:** 4.0: `512`

Maximum memory to use for sstable chunk cache and buffer pooling. 32MB of this are reserved for pooling buffers, the rest is used for chunk cache that holds uncompressed sstable chunks. Defaults to the smaller of 1/4 of heap or 512MB. This pool is allocated off-heap, so is in addition to the memory allocated for heap. The cache also has on-heap overhead which is roughly 128 bytes per chunk (i.e. 0.2% of the reserved size if the default 64k chunk size is used). Memory is only allocated when needed.

---

### buffer_pool_use_heap_if_exhausted

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `true` | 4.1: `true` | 5.0: `true`

No description available.

---

### prepared_statements_cache_size

**Versions:** 4.1, 5.0

**Default:** 4.1: `Auto` | 5.0: `Auto`

Maximum size of the native protocol prepared statement cache

Valid values are either "auto" (omitting the value) or a value greater 0.

Note that specifying a too large value will result in long running GCs and possbily out-of-memory errors. Keep the value at a small fraction of the heap.

If you constantly see "prepared statements discarded in the last minute because cache limit reached" messages, the first step is to investigate the root cause of these messages and check whether prepared statements are used correctly - i.e. use bind markers for variable parts.

Do only change the default value, if you really have more prepared statements than fit in the cache. In most cases it is not neccessary to change this value. Constantly re-preparing statements is a performance penalty.

Default value ("auto") is 1/256th of the heap or 10MiB, whichever is greater Min unit: MiB

---

### prepared_statements_cache_size_mb

**Versions:** 4.0

**Default:** 4.0: `Auto`

Maximum size of the native protocol prepared statement cache

Valid values are either "auto" (omitting the value) or a value greater 0.

Note that specifying a too large value will result in long running GCs and possbily out-of-memory errors. Keep the value at a small fraction of the heap.

If you constantly see "prepared statements discarded in the last minute because cache limit reached" messages, the first step is to investigate the root cause of these messages and check whether prepared statements are used correctly - i.e. use bind markers for variable parts.

Do only change the default value, if you really have more prepared statements than fit in the cache. In most cases it is not neccessary to change this value. Constantly re-preparing statements is a performance penalty.

Default value ("auto") is 1/256th of the heap or 10MB, whichever is greater

---

### networking_cache_size

**Versions:** 4.1, 5.0

**Default:** 4.1: `128MiB` | 5.0: `128MiB`

Maximum memory to use for inter-node and client-server networking buffers.

Defaults to the smaller of 1/16 of heap or 128MB. This pool is allocated off-heap, so is in addition to the memory allocated for heap. The cache also has on-heap overhead which is roughly 128 bytes per chunk (i.e. 0.2% of the reserved size if the default 64k chunk size is used). Memory is only allocated when needed. Min unit: MiB

---

### networking_cache_size_in_mb

**Versions:** 4.0

**Default:** 4.0: `128`

Maximum memory to use for inter-node and client-server networking buffers.

Defaults to the smaller of 1/16 of heap or 128MB. This pool is allocated off-heap, so is in addition to the memory allocated for heap. The cache also has on-heap overhead which is roughly 128 bytes per chunk (i.e. 0.2% of the reserved size if the default 64k chunk size is used). Memory is only allocated when needed.

---

### ip_cache_max_size

**Versions:** 5.0

**Default:** 5.0: Not set

Maximum number of entries an IP to CIDR groups cache can accommodate

---

## Snitch Configuration

### endpoint_snitch

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `SimpleSnitch` | 4.1: `SimpleSnitch` | 5.0: `SimpleSnitch`

The snitch determines network topology for request routing and replica placement.

!!! warning "Snitch Migration"
    Cannot switch to incompatible snitch after data insertion. Requires adding new nodes and decommissioning old ones.

**Available Snitches:**

| Snitch | Use Case | Description |
|--------|----------|-------------|
| `SimpleSnitch` | Development | All nodes in "datacenter1", "rack1" |
| `GossipingPropertyFileSnitch` | **Production** | Reads from `cassandra-rackdc.properties` |
| `Ec2Snitch` | AWS single-region | Region = DC, AZ = rack |
| `Ec2MultiRegionSnitch` | AWS multi-region | Uses public IPs |
| `GoogleCloudSnitch` | GCP | Region = DC, zone = rack |
| `AzureSnitch` | Azure | Location = DC, zone = rack |

---

### dynamic_snitch_update_interval

**Versions:** 4.1, 5.0

**Default:** 4.1: `100ms` | 5.0: `100ms`

controls how often to perform the more expensive part of host score calculation Min unit: ms

---

### dynamic_snitch_update_interval_in_ms

**Versions:** 4.0

**Default:** 4.0: `100`

controls how often to perform the more expensive part of host score calculation

---

### dynamic_snitch_reset_interval

**Versions:** 4.1, 5.0

**Default:** 4.1: `600000ms` | 5.0: `600000ms`

controls how often to reset all host scores, allowing a bad host to possibly recover Min unit: ms

---

### dynamic_snitch_reset_interval_in_ms

**Versions:** 4.0

**Default:** 4.0: `600000`

controls how often to reset all host scores, allowing a bad host to possibly recover

---

### dynamic_snitch_badness_threshold

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `1.0` | 4.1: `1.0` | 5.0: `1.0`

if set greater than zero, this will allow 'pinning' of replicas to hosts in order to increase cache capacity. The badness threshold will control how much worse the pinned host has to be before the dynamic snitch will prefer other replicas over it.  This is expressed as a double which represents a percentage.  Thus, a value of 0.2 means Cassandra would continue to prefer the static snitch values until the pinned host was 20% worse than the fastest.

---

## Failure Detection

### phi_convict_threshold

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `8` | 4.1: `8` | 5.0: `8`

phi value that must be reached for a host to be marked down. most users should never need to adjust this.

---

## Request Timeouts

### read_request_timeout

**Versions:** 4.1, 5.0

**Default:** 4.1: `5000ms` | 5.0: `5000ms`

How long the coordinator should wait for read operations to complete. Lowest acceptable value is 10 ms. Min unit: ms

---

### read_request_timeout_in_ms

**Versions:** 4.0

**Default:** 4.0: `5000`

How long the coordinator should wait for read operations to complete. Lowest acceptable value is 10 ms.

---

### range_request_timeout

**Versions:** 4.1, 5.0

**Default:** 4.1: `10000ms` | 5.0: `10000ms`

How long the coordinator should wait for seq or index scans to complete. Lowest acceptable value is 10 ms. Min unit: ms

---

### range_request_timeout_in_ms

**Versions:** 4.0

**Default:** 4.0: `10000`

How long the coordinator should wait for seq or index scans to complete. Lowest acceptable value is 10 ms.

---

### write_request_timeout

**Versions:** 4.1, 5.0

**Default:** 4.1: `2000ms` | 5.0: `2000ms`

How long the coordinator should wait for writes to complete. Lowest acceptable value is 10 ms. Min unit: ms

---

### write_request_timeout_in_ms

**Versions:** 4.0

**Default:** 4.0: `2000`

How long the coordinator should wait for writes to complete. Lowest acceptable value is 10 ms.

---

### counter_write_request_timeout

**Versions:** 4.1, 5.0

**Default:** 4.1: `5000ms` | 5.0: `5000ms`

How long the coordinator should wait for counter writes to complete. Lowest acceptable value is 10 ms. Min unit: ms

---

### counter_write_request_timeout_in_ms

**Versions:** 4.0

**Default:** 4.0: `5000`

How long the coordinator should wait for counter writes to complete. Lowest acceptable value is 10 ms.

---

### cas_contention_timeout

**Versions:** 4.1, 5.0

**Default:** 4.1: `1000ms` | 5.0: `1000ms`

How long a coordinator should continue to retry a CAS operation that contends with other proposals for the same row. Lowest acceptable value is 10 ms. Min unit: ms

---

### cas_contention_timeout_in_ms

**Versions:** 4.0

**Default:** 4.0: `1000`

How long a coordinator should continue to retry a CAS operation that contends with other proposals for the same row. Lowest acceptable value is 10 ms.

---

### truncate_request_timeout

**Versions:** 4.1, 5.0

**Default:** 4.1: `60000ms` | 5.0: `60000ms`

How long the coordinator should wait for truncates to complete (This can be much longer, because unless auto_snapshot is disabled we need to flush first so we can snapshot before removing the data.) Lowest acceptable value is 10 ms. Min unit: ms

---

### truncate_request_timeout_in_ms

**Versions:** 4.0

**Default:** 4.0: `60000`

How long the coordinator should wait for truncates to complete (This can be much longer, because unless auto_snapshot is disabled we need to flush first so we can snapshot before removing the data.) Lowest acceptable value is 10 ms.

---

### request_timeout

**Versions:** 4.1, 5.0

**Default:** 4.1: `10000ms` | 5.0: `10000ms`

The default timeout for other, miscellaneous operations. Lowest acceptable value is 10 ms. Min unit: ms

---

### request_timeout_in_ms

**Versions:** 4.0

**Default:** 4.0: `10000`

The default timeout for other, miscellaneous operations. Lowest acceptable value is 10 ms.

---

### slow_query_log_timeout

**Versions:** 4.1, 5.0

**Default:** 4.1: `500ms` | 5.0: `500ms`

How long before a node logs slow queries. Select queries that take longer than this timeout to execute, will generate an aggregated log message, so that slow queries can be identified. Set this value to zero to disable slow query logging. Min unit: ms

---

### slow_query_log_timeout_in_ms

**Versions:** 4.0

**Default:** 4.0: `500`

How long before a node logs slow queries. Select queries that take longer than this timeout to execute, will generate an aggregated log message, so that slow queries can be identified. Set this value to zero to disable slow query logging.

---

## Streaming

### streaming_keep_alive_period

**Versions:** 4.1, 5.0

**Default:** 4.1: `300s` | 5.0: `300s`

Set period for idle state control messages for earlier detection of failed streams This node will send a keep-alive message periodically on the streaming's control channel. This ensures that any eventual SocketTimeoutException will occur within 2 keep-alive cycles If the node cannot send, or timeouts sending, the keep-alive message on the netty control channel the stream session is closed. Default value is 300s (5 minutes), which means stalled streams are detected within 10 minutes Specify 0 to disable. Min unit: s

---

### streaming_keep_alive_period_in_secs

**Versions:** 4.0

**Default:** 4.0: `300`

Set keep-alive period for streaming This node will send a keep-alive message periodically with this period. If the node does not receive a keep-alive message from the peer for 2 keep-alive cycles the stream session times out and fail Default value is 300s (5 minutes), which means stalled stream times out in 10 minutes by default

---

### stream_throughput_outbound

**Versions:** 4.1, 5.0

**Default:** 4.1: `24MiB/s` | 5.0: `24MiB/s`

Throttles all outbound streaming file transfers on this node to the given total throughput in Mbps. This is necessary because Cassandra does mostly sequential IO when streaming data during bootstrap or repair, which can lead to saturating the network connection and degrading rpc performance. When unset, the default is 200 Mbps or 24 MiB/s.

---

### stream_throughput_outbound_megabits_per_sec

**Versions:** 4.0

**Default:** 4.0: `200`

Throttles all outbound streaming file transfers on this node to the given total throughput in Mbps. This is necessary because Cassandra does mostly sequential IO when streaming data during bootstrap or repair, which can lead to saturating the network connection and degrading rpc performance. When unset, the default is 200 Mbps or 25 MB/s.

---

### inter_dc_stream_throughput_outbound

**Versions:** 4.1, 5.0

**Default:** 4.1: `24MiB/s` | 5.0: `24MiB/s`

Throttles all streaming file transfer between the datacenters, this setting allows users to throttle inter dc stream throughput in addition to throttling all network stream traffic as configured with stream_throughput_outbound_megabits_per_sec When unset, the default is 200 Mbps or 24 MiB/s.

---

### inter_dc_stream_throughput_outbound_megabits_per_sec

**Versions:** 4.0

**Default:** 4.0: `200`

Throttles all streaming file transfer between the datacenters, this setting allows users to throttle inter dc stream throughput in addition to throttling all network stream traffic as configured with stream_throughput_outbound_megabits_per_sec When unset, the default is 200 Mbps or 25 MB/s

---

### stream_entire_sstables

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `true` | 4.1: `true` | 5.0: `true`

When enabled, permits Cassandra to zero-copy stream entire eligible SSTables between nodes, including every component. This speeds up the network transfer significantly subject to throttling specified by entire_sstable_stream_throughput_outbound, and entire_sstable_inter_dc_stream_throughput_outbound for inter-DC transfers. Enabling this will reduce the GC pressure on sending and receiving node. When unset, the default is enabled. While this feature tries to keep the disks balanced, it cannot guarantee it. This feature will be automatically disabled if internode encryption is enabled.

---

### streaming_connections_per_host

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `1` | 4.1: `1` | 5.0: `1`

Limit number of connections per host for streaming Increase this when you notice that joins are CPU-bound rather that network bound (for example a few nodes with big files).

---

### entire_sstable_stream_throughput_outbound

**Versions:** 4.1, 5.0

**Default:** 4.1: `24MiB/s` | 5.0: `24MiB/s`

Throttles entire SSTable outbound streaming file transfers on this node to the given total throughput in Mbps. Setting this value to 0 it disables throttling. When unset, the default is 200 Mbps or 24 MiB/s.

---

### entire_sstable_inter_dc_stream_throughput_outbound

**Versions:** 4.1, 5.0

**Default:** 4.1: `24MiB/s` | 5.0: `24MiB/s`

Throttles entire SSTable file streaming between datacenters. Setting this value to 0 disables throttling for entire SSTable inter-DC file streaming. When unset, the default is 200 Mbps or 24 MiB/s.

---

### streaming_state_expires

**Versions:** 4.1, 5.0

**Default:** 4.1: `3d` | 5.0: `3d`

Settings for stream stats tracking; used by system_views.streaming table How long before a stream is evicted from tracking; this impacts both historic and currently running streams.

---

### streaming_state_size

**Versions:** 4.1, 5.0

**Default:** 4.1: `40MiB` | 5.0: `40MiB`

How much memory may be used for tracking before evicting session from tracking; once crossed historic and currently running streams maybe impacted.

---

### streaming_stats_enabled

**Versions:** 4.1, 5.0

**Default:** 4.1: `true` | 5.0: `true`

Enable/Disable tracking of streaming stats

---

## Security - Authentication

### authenticator

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `AllowAllAuthenticator` | 4.1: `AllowAllAuthenticator` | 5.0: `AllowAllAuthenticator`

Authentication backend, implementing IAuthenticator; used to identify users Out of the box, Cassandra provides org.apache.cassandra.auth.{AllowAllAuthenticator, PasswordAuthenticator}.

- AllowAllAuthenticator performs no checks - set it to disable authentication. - PasswordAuthenticator relies on username/password pairs to authenticate users. It keeps usernames and hashed passwords in system_auth.roles table. Please increase system_auth keyspace replication factor if you use this authenticator. If using PasswordAuthenticator, CassandraRoleManager must also be used (see below)

---

### internode_authenticator

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `org.apache.cassandra.auth.AllowAllInternodeAuthenticator` | 4.1: `org.apache.cassandra.auth.AllowAllInternodeAuthenticator` | 5.0: Not set

Internode authentication backend, implementing IInternodeAuthenticator; used to allow/disallow connections from peer nodes.

---

## Security - Authorization

### authorizer

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `AllowAllAuthorizer` | 4.1: `AllowAllAuthorizer` | 5.0: `AllowAllAuthorizer`

Authorization backend, implementing IAuthorizer; used to limit access/provide permissions Out of the box, Cassandra provides org.apache.cassandra.auth.{AllowAllAuthorizer, CassandraAuthorizer}.

- AllowAllAuthorizer allows any action to any user - set it to disable authorization. - CassandraAuthorizer stores permissions in system_auth.role_permissions table. Please increase system_auth keyspace replication factor if you use this authorizer.

---

### role_manager

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `CassandraRoleManager` | 4.1: `CassandraRoleManager` | 5.0: `CassandraRoleManager`

Part of the Authentication & Authorization backend, implementing IRoleManager; used to maintain grants and memberships between roles. Out of the box, Cassandra provides org.apache.cassandra.auth.CassandraRoleManager, which stores role information in the system_auth keyspace. Most functions of the IRoleManager require an authenticated login, so unless the configured IAuthenticator actually implements authentication, most of this functionality will be unavailable.

- CassandraRoleManager stores role data in the system_auth keyspace. Please increase system_auth keyspace replication factor if you use this role manager.

---

### network_authorizer

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `AllowAllNetworkAuthorizer` | 4.1: `AllowAllNetworkAuthorizer` | 5.0: `AllowAllNetworkAuthorizer`

Network authorization backend, implementing INetworkAuthorizer; used to restrict user access to certain DCs Out of the box, Cassandra provides org.apache.cassandra.auth.{AllowAllNetworkAuthorizer, CassandraNetworkAuthorizer}.

- AllowAllNetworkAuthorizer allows access to any DC to any user - set it to disable authorization. - CassandraNetworkAuthorizer stores permissions in system_auth.network_permissions table. Please increase system_auth keyspace replication factor if you use this authorizer.

---

### cidr_authorizer

**Versions:** 5.0

**Default:** 5.0: `(see below)`

CIDR authorization backend, implementing ICIDRAuthorizer. Used to restrict user access from certain CIDRs.

```yaml
cidr_authorizer:
  class_name: AllowAllCIDRAuthorizer
  parameters:
    cidr_checks_for_superusers: false
    cidr_authorizer_mode: MONITOR
    cidr_groups_cache_refresh_interval: 5
    ip_cache_max_size: 100
```

| Sub-parameter | Description | Default |
|---------------|-------------|---------|
| `class_name` | Authorization implementation class | `AllowAllCIDRAuthorizer` |
| `cidr_checks_for_superusers` | Enable CIDR authorization for superusers (JMX calls excluded) | `false` |
| `cidr_authorizer_mode` | `MONITOR` (log only) or `ENFORCE` (reject unauthorized) | `MONITOR` |
| `cidr_groups_cache_refresh_interval` | Refresh interval for CIDR groups cache (minutes) | `5` |
| `ip_cache_max_size` | Maximum entries in IP to CIDR groups cache | `100` |

**Implementations:**

- **AllowAllCIDRAuthorizer**: Allows access from any CIDR to any user. Set this to disable CIDR authorization.
- **CassandraCIDRAuthorizer**: Stores user CIDR permissions in `system_auth.cidr_permissions` table. Increase system_auth keyspace replication factor when using this authorizer.

**Modes:**

- **MONITOR**: CIDR checks are not enforced. Unauthorized access attempts are logged as warnings but not rejected.
- **ENFORCE**: CIDR checks are enforced. Users accessing from unauthorized CIDR groups are rejected.

---

### cidr_authorizer_mode

**Versions:** 5.0

**Default:** 5.0: `MONITOR`

CIDR authorizer when enabled, supports MONITOR and ENFORCE modes. Default mode is MONITOR In MONITOR mode, CIDR checks are NOT enforced. Instead, CIDR groups of users accesses are logged using nospamlogger. A warning message would be logged if a user accesses from unauthorized CIDR group (but access won't be rejected). An info message would be logged otherwise. In ENFORCE mode, CIDR checks are enforced, i.e, users accesses would be rejected if attempted from unauthorized CIDR groups.


---

## Security - Caching

### permissions_validity

**Versions:** 4.1, 5.0

**Default:** 4.1: `2000ms` | 5.0: `2000ms`

Validity period for permissions cache (fetching permissions can be an expensive operation depending on the authorizer, CassandraAuthorizer is one example). Defaults to 2000, set to 0 to disable. Will be disabled automatically for AllowAllAuthorizer. For a long-running cache using permissions_cache_active_update, consider setting to something longer such as a daily validation: 86400000ms Min unit: ms

---

### permissions_validity_in_ms

**Versions:** 4.0

**Default:** 4.0: `2000`

Validity period for permissions cache (fetching permissions can be an expensive operation depending on the authorizer, CassandraAuthorizer is one example). Defaults to 2000, set to 0 to disable. Will be disabled automatically for AllowAllAuthorizer.

---

### permissions_update_interval

**Versions:** 4.1, 5.0

**Default:** 4.1: `2000ms` | 5.0: `2000ms`

Refresh interval for permissions cache (if enabled). After this interval, cache entries become eligible for refresh. Upon next access, an async reload is scheduled and the old value returned until it completes. If permissions_validity is non-zero, then this must be also. This setting is also used to inform the interval of auto-updating if using permissions_cache_active_update. Defaults to the same value as permissions_validity. For a longer-running permissions cache, consider setting to update hourly (60000) Min unit: ms

---

### permissions_update_interval_in_ms

**Versions:** 4.0

**Default:** 4.0: `2000`

Refresh interval for permissions cache (if enabled). After this interval, cache entries become eligible for refresh. Upon next access, an async reload is scheduled and the old value returned until it completes. If permissions_validity_in_ms is non-zero, then this must be also. Defaults to the same value as permissions_validity_in_ms.

---

### permissions_cache_active_update

**Versions:** 4.1, 5.0

**Default:** 4.1: `false` | 5.0: `false`

If true, cache contents are actively updated by a background task at the interval set by permissions_update_interval. If false, cache entries become eligible for refresh after their update interval. Upon next access, an async reload is scheduled and the old value returned until it completes.

---

### roles_validity

**Versions:** 4.1, 5.0

**Default:** 4.1: `2000ms` | 5.0: `2000ms`

Validity period for roles cache (fetching granted roles can be an expensive operation depending on the role manager, CassandraRoleManager is one example) Granted roles are cached for authenticated sessions in AuthenticatedUser and after the period specified here, become eligible for (async) reload. Defaults to 2000, set to 0 to disable caching entirely. Will be disabled automatically for AllowAllAuthenticator. For a long-running cache using roles_cache_active_update, consider setting to something longer such as a daily validation: 86400000 Min unit: ms

---

### roles_validity_in_ms

**Versions:** 4.0

**Default:** 4.0: `2000`

Validity period for roles cache (fetching granted roles can be an expensive operation depending on the role manager, CassandraRoleManager is one example) Granted roles are cached for authenticated sessions in AuthenticatedUser and after the period specified here, become eligible for (async) reload. Defaults to 2000, set to 0 to disable caching entirely. Will be disabled automatically for AllowAllAuthenticator.

---

### roles_update_interval

**Versions:** 4.1, 5.0

**Default:** 4.1: `2000ms` | 5.0: `2000ms`

Refresh interval for roles cache (if enabled). After this interval, cache entries become eligible for refresh. Upon next access, an async reload is scheduled and the old value returned until it completes. If roles_validity is non-zero, then this must be also. This setting is also used to inform the interval of auto-updating if using roles_cache_active_update. Defaults to the same value as roles_validity. For a long-running cache, consider setting this to 60000 (1 hour) etc. Min unit: ms

---

### roles_update_interval_in_ms

**Versions:** 4.0

**Default:** 4.0: `2000`

Refresh interval for roles cache (if enabled). After this interval, cache entries become eligible for refresh. Upon next access, an async reload is scheduled and the old value returned until it completes. If roles_validity_in_ms is non-zero, then this must be also. Defaults to the same value as roles_validity_in_ms.

---

### roles_cache_active_update

**Versions:** 4.1, 5.0

**Default:** 4.1: `false` | 5.0: `false`

If true, cache contents are actively updated by a background task at the interval set by roles_update_interval. If false, cache entries become eligible for refresh after their update interval. Upon next access, an async reload is scheduled and the old value returned until it completes.

---

### credentials_validity

**Versions:** 4.1, 5.0

**Default:** 4.1: `2000ms` | 5.0: `2000ms`

Validity period for credentials cache. This cache is tightly coupled to the provided PasswordAuthenticator implementation of IAuthenticator. If another IAuthenticator implementation is configured, this cache will not be automatically used and so the following settings will have no effect. Please note, credentials are cached in their encrypted form, so while activating this cache may reduce the number of queries made to the underlying table, it may not  bring a significant reduction in the latency of individual authentication attempts. Defaults to 2000, set to 0 to disable credentials caching. For a long-running cache using credentials_cache_active_update, consider setting to something longer such as a daily validation: 86400000 Min unit: ms

---

### credentials_validity_in_ms

**Versions:** 4.0

**Default:** 4.0: `2000`

Validity period for credentials cache. This cache is tightly coupled to the provided PasswordAuthenticator implementation of IAuthenticator. If another IAuthenticator implementation is configured, this cache will not be automatically used and so the following settings will have no effect. Please note, credentials are cached in their encrypted form, so while activating this cache may reduce the number of queries made to the underlying table, it may not  bring a significant reduction in the latency of individual authentication attempts. Defaults to 2000, set to 0 to disable credentials caching.

---

### credentials_update_interval

**Versions:** 4.1, 5.0

**Default:** 4.1: `2000ms` | 5.0: `2000ms`

Refresh interval for credentials cache (if enabled). After this interval, cache entries become eligible for refresh. Upon next access, an async reload is scheduled and the old value returned until it completes. If credentials_validity is non-zero, then this must be also. This setting is also used to inform the interval of auto-updating if using credentials_cache_active_update. Defaults to the same value as credentials_validity. For a longer-running permissions cache, consider setting to update hourly (60000) Min unit: ms

---

### credentials_update_interval_in_ms

**Versions:** 4.0

**Default:** 4.0: `2000`

Refresh interval for credentials cache (if enabled). After this interval, cache entries become eligible for refresh. Upon next access, an async reload is scheduled and the old value returned until it completes. If credentials_validity_in_ms is non-zero, then this must be also. Defaults to the same value as credentials_validity_in_ms.

---

### credentials_cache_active_update

**Versions:** 4.1, 5.0

**Default:** 4.1: `false` | 5.0: `false`

If true, cache contents are actively updated by a background task at the interval set by credentials_update_interval. If false (default), cache entries become eligible for refresh after their update interval. Upon next access, an async reload is scheduled and the old value returned until it completes.

---

### auth_cache_warming_enabled

**Versions:** 4.1, 5.0

**Default:** 4.1: `false` | 5.0: `false`

Delays on auth resolution can lead to a thundering herd problem on reconnects; this option will enable warming of auth caches prior to node completing startup. See CASSANDRA-16958

---

### auth_read_consistency_level

**Versions:** 4.1, 5.0

**Default:** 4.1: `LOCAL_QUORUM` | 5.0: `LOCAL_QUORUM`

configure the read and write consistency levels for modifications to auth tables

---

### auth_write_consistency_level

**Versions:** 4.1, 5.0

**Default:** 4.1: `EACH_QUORUM` | 5.0: `EACH_QUORUM`

No description available.

---

## Security - Encryption

### server_encryption_options

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `(see below)` | 4.1: `(see below)` | 5.0: `(see below)`

Configures server-to-server internode encryption.

!!! warning "Default Configuration"
    The default configuration is insecure. See [Encryption](../../../security/encryption/index.md) for setup instructions.

```yaml
server_encryption_options:
  internode_encryption: none
  legacy_ssl_storage_port_enabled: false
  keystore: conf/.keystore
  keystore_password: cassandra
  truststore: conf/.truststore
  truststore_password: cassandra
  require_client_auth: false
  require_endpoint_verification: false
  # For mTLS (optional)
  outbound_keystore: conf/.keystore
  outbound_keystore_password: cassandra
  # Advanced options
  protocol: TLS
  store_type: JKS
  cipher_suites: [
    TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384, TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,
    TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256, TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA,
    TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA, TLS_RSA_WITH_AES_128_GCM_SHA256, TLS_RSA_WITH_AES_128_CBC_SHA,
    TLS_RSA_WITH_AES_256_CBC_SHA
  ]
```

| Sub-parameter | Description | Default |
|---------------|-------------|---------|
| `internode_encryption` | Encryption scope: `none`, `dc`, `rack`, or `all` | `none` |
| `optional` | Allow mixed encrypted/unencrypted connections on storage_port | `true` if `none` |
| `legacy_ssl_storage_port_enabled` | Open encrypted socket on ssl_storage_port (upgrade to 4.0 only) | `false` |
| `keystore` | Path to keystore file | `conf/.keystore` |
| `keystore_password` | Keystore password | - |
| `outbound_keystore` | Client keystore for mTLS outbound connections | same as `keystore` |
| `outbound_keystore_password` | Outbound keystore password | - |
| `truststore` | Path to truststore (required if `require_client_auth: true`) | `conf/.truststore` |
| `truststore_password` | Truststore password | - |
| `require_client_auth` | Require client certificates (mTLS) | `false` |
| `require_endpoint_verification` | Verify hostname in certificate matches connected host | `false` |
| `protocol` | SSL/TLS protocol | `TLS` |
| `store_type` | Keystore/truststore format | `JKS` |
| `cipher_suites` | Allowed cipher suites (list) | JVM defaults |
| `ssl_context_factory.class_name` | Custom SSL context factory class | `DefaultSslContextFactory` |

**Internode Encryption Values:**

- **none**: Do not encrypt outgoing connections
- **dc**: Encrypt connections to peers in other datacenters but not within datacenters
- **rack**: Encrypt connections to peers in other racks but not within racks
- **all**: Always use encrypted connections

**Enabling Encryption (Two-Step Process):**

1. Set `internode_encryption=<dc|rack|all>` and `optional=true`. Restart all nodes.
2. Set `optional=false` and optionally `require_client_auth=true` for mutual auth. Restart all nodes.

---

### client_encryption_options

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `(see below)` | 4.1: `(see below)` | 5.0: `(see below)`

Configures client-to-server encryption.

!!! warning "Default Configuration"
    The default configuration is insecure. See [Encryption](../../../security/encryption/index.md) for setup instructions.

```yaml
client_encryption_options:
  enabled: false
  keystore: conf/.keystore
  keystore_password: cassandra
  truststore: conf/.truststore
  truststore_password: cassandra
  require_client_auth: false
  require_endpoint_verification: false
  # Advanced options
  protocol: TLS
  store_type: JKS
  cipher_suites: [
    TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384, TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,
    TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256, TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA,
    TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA, TLS_RSA_WITH_AES_128_GCM_SHA256, TLS_RSA_WITH_AES_128_CBC_SHA,
    TLS_RSA_WITH_AES_256_CBC_SHA
  ]
```

| Sub-parameter | Description | Default |
|---------------|-------------|---------|
| `enabled` | Enable client-to-server encryption | `false` |
| `optional` | Allow mixed encrypted/unencrypted on native_transport_port | `true` if disabled, `false` if enabled |
| `keystore` | Path to keystore file | `conf/.keystore` |
| `keystore_password` | Keystore password | - |
| `truststore` | Path to truststore (required if `require_client_auth: true`) | `conf/.truststore` |
| `truststore_password` | Truststore password | - |
| `require_client_auth` | Require client certificates (mTLS) | `false` |
| `require_endpoint_verification` | Verify hostname in certificate | `false` |
| `protocol` | SSL/TLS protocol | `TLS` |
| `store_type` | Keystore/truststore format | `JKS` |
| `cipher_suites` | Allowed cipher suites (list) | JVM defaults |
| `ssl_context_factory.class_name` | Custom SSL context factory class | `DefaultSslContextFactory` |

**Enabling Encryption (Two-Step Process):**

1. Set `enabled=true` and `optional=true`. Restart all nodes.
2. Set `optional=false` and optionally `require_client_auth=true` for mutual auth. Restart all nodes.

---

### transparent_data_encryption_options

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `(see below)` | 4.1: `(see below)` | 5.0: `(see below)`

Configures encryption for data at rest.

```yaml
transparent_data_encryption_options:
  enabled: false
  chunk_length_kb: 64
  cipher: AES/CBC/PKCS5Padding
  key_alias: testing:1
  key_provider:
    - class_name: org.apache.cassandra.security.JKSKeyProvider
      parameters:
        - keystore: conf/.keystore
          keystore_password: cassandra
```

| Sub-parameter | Description | Default |
|---------------|-------------|---------|
| `enabled` | Enable TDE | `false` |
| `chunk_length_kb` | Encryption chunk size | `64` |
| `cipher` | Cipher algorithm | `AES/CBC/PKCS5Padding` |
| `key_alias` | Key alias in keystore | - |

---

### crypto_provider

**Versions:** 5.0

**Default:** 5.0: `(see below)`

Configures Java cryptography provider.

```yaml
crypto_provider:
  class_name: org.apache.cassandra.security.DefaultCryptoProvider
```

Default installs Amazon Corretto Crypto Provider (ACCP).

---

### ssl_context_factory

**Versions:** 4.1, 5.0

**Default:** 4.1: Not set | 5.0: Not set

Configure the way Cassandra creates SSL contexts. To use PEM-based key material, see org.apache.cassandra.security.PEMBasedSslContextFactory

---

## Disk Failure Policy

### disk_failure_policy

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `stop` | 4.1: `stop` | 5.0: `stop`

Policy for data disk failures:

die shut down gossip and client transports and kill the JVM for any fs errors or single-sstable errors, so the node can be replaced.

stop_paranoid shut down gossip and client transports even for single-sstable errors, kill the JVM for errors during startup.

stop shut down gossip and client transports, leaving the node effectively dead, but can still be inspected via JMX, kill the JVM for errors during startup.

best_effort stop using the failed disk and respond to requests based on remaining available sstables.  This means you WILL see obsolete data at CL.ONE!

ignore ignore fatal errors and let requests fail, as in pre-1.2 Cassandra

---

### commit_failure_policy

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `stop` | 4.1: `stop` | 5.0: `stop`

Policy for commit disk failures:

die shut down the node and kill the JVM, so the node can be replaced.

stop shut down the node, leaving the node effectively dead, but can still be inspected via JMX.

stop_commit shutdown the commit log, letting writes collect but continuing to service reads, as in pre-2.0.5 Cassandra

ignore ignore fatal errors and let the batches fail

---

### disk_optimization_strategy

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `ssd` | 4.1: `ssd` | 5.0: `ssd`

The strategy for optimizing disk read Possible values are: ssd (for solid state disks, the default) spinning (for spinning disks)

---

### disk_access_mode

**Versions:** 5.0

**Default:** 5.0: `mmap_index_only`

Policy for accessing disk:

auto Enable mmap on both data and index files on a 64-bit JVM.

standard Disable mmap entirely.

mmap Map index and data files. mmap can cause excessive paging if all actively read SSTables do not fit into RAM.

mmap_index_only Similar to mmap but maps only index files. Using this setting might also help if you observe high number of page faults or steals along with increased latencies. This setting is default.

---

## Snapshots and Backups

### incremental_backups

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `false` | 4.1: `false` | 5.0: `false`

Set to true to have Cassandra create a hard link to each sstable flushed or streamed locally in a backups/ subdirectory of all the keyspace data in this node.  Removing these links is the operator's responsibility. The operator can also turn off incremental backups for specified table by setting table parameter incremental_backups to false, which is set to true by default. See CASSANDRA-15402

---

### snapshot_before_compaction

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `false` | 4.1: `false` | 5.0: `false`

Whether or not to take a snapshot before each compaction.  Be careful using this option, since Cassandra won't clean up the snapshots for you.  Mostly useful if you're paranoid when there is a data format change.

---

### auto_snapshot

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `true` | 4.1: `true` | 5.0: `true`

Whether or not a snapshot is taken of the data before keyspace truncation or dropping of column families. The STRONGLY advised default of true should be used to provide data safety. If you set this flag to false, you will lose data on truncation or drop.

---

### auto_snapshot_ttl

**Versions:** 4.1, 5.0

**Default:** 4.1: `30d` | 5.0: `30d`

Adds a time-to-live (TTL) to auto snapshots generated by table truncation or drop (when enabled). After the TTL is elapsed, the snapshot is automatically cleared. By default, auto snapshots *do not* have TTL, uncomment the property below to enable TTL on auto snapshots. Accepted units: d (days), h (hours) or m (minutes)

---

### snapshot_links_per_second

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `0` | 4.1: `0` | 5.0: `0`

The act of creating or clearing a snapshot involves creating or removing potentially tens of thousands of links, which can cause significant performance impact, especially on consumer grade SSDs. A non-zero value here can be used to throttle these links to avoid negative performance impact of taking and clearing snapshots

---

## Repair

### repair_session_space

**Versions:** 4.1, 5.0

**Default:** 4.1: Not set | 5.0: Not set

Limit memory usage for Merkle tree calculations during repairs of a certain table and common token range. Repair commands targetting multiple tables or virtual nodes can exceed this limit depending on concurrent_merkle_tree_requests.

The default is 1/16th of the available heap. The main tradeoff is that smaller trees have less resolution, which can lead to over-streaming data. If you see heap pressure during repairs, consider lowering this, but you cannot go below one mebibyte. If you see lots of over-streaming, consider raising this or using subrange repair.

For more details see https://issues.apache.org/jira/browse/CASSANDRA-14096.

Min unit: MiB

---

### repair_session_space_in_mb

**Versions:** 4.0

**Default:** 4.0: Not set

Limit memory usage for Merkle tree calculations during repairs. The default is 1/16th of the available heap. The main tradeoff is that smaller trees have less resolution, which can lead to over-streaming data. If you see heap pressure during repairs, consider lowering this, but you cannot go below one megabyte. If you see lots of over-streaming, consider raising this or using subrange repair.

For more details see https://issues.apache.org/jira/browse/CASSANDRA-14096.

---

### repaired_data_tracking_for_range_reads_enabled

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `false` | 4.1: `false` | 5.0: `false`

Enable tracking of repaired state of data during reads and comparison between replicas Mismatches between the repaired sets of replicas can be characterized as either confirmed or unconfirmed. In this context, unconfirmed indicates that the presence of pending repair sessions, unrepaired partition tombstones, or some other condition means that the disparity cannot be considered conclusive. Confirmed mismatches should be a trigger for investigation as they may be indicative of corruption or data loss. There are separate flags for range vs partition reads as single partition reads are only tracked when CL > 1 and a digest mismatch occurs. Currently, range queries don't use digests so if enabled for range reads, all range reads will include repaired data tracking. As this adds some overhead, operators may wish to disable it whilst still enabling it for partition reads

---

### repaired_data_tracking_for_partition_reads_enabled

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `false` | 4.1: `false` | 5.0: `false`

No description available.

---

### report_unconfirmed_repaired_data_mismatches

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `false` | 4.1: `false` | 5.0: `false`

If false, only confirmed mismatches will be reported. If true, a separate metric for unconfirmed mismatches will also be recorded. This is to avoid potential signal:noise issues are unconfirmed mismatches are less actionable than confirmed ones.

---

## Change Data Capture (CDC)

### cdc_enabled

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `false` | 4.1: `false` | 5.0: `false`

Enable / disable CDC functionality on a per-node basis. This modifies the logic used for write path allocation rejection (standard: never reject. cdc: reject Mutation containing a CDC-enabled table if at space limit in cdc_raw_directory).

---

### cdc_raw_directory

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `/var/lib/cassandra/cdc_raw` | 4.1: `/var/lib/cassandra/cdc_raw` | 5.0: `/var/lib/cassandra/cdc_raw`

CommitLogSegments are moved to this directory on flush if cdc_enabled: true and the segment contains mutations for a CDC-enabled table. This should be placed on a separate spindle than the data directories. If not set, the default directory is $CASSANDRA_HOME/data/cdc_raw.

---

### cdc_total_space

**Versions:** 4.1, 5.0

**Default:** 4.1: `4096MiB` | 5.0: `4096MiB`

Total space to use for change-data-capture logs on disk.

If space gets above this value, Cassandra will throw WriteTimeoutException on Mutations including tables with CDC enabled. A CDCCompactor is responsible for parsing the raw CDC logs and deleting them when parsing is completed.

The default value is the min of 4096 MiB and 1/8th of the total space of the drive where cdc_raw_directory resides. Min unit: MiB

---

### cdc_total_space_in_mb

**Versions:** 4.0

**Default:** 4.0: `4096`

Total space to use for change-data-capture logs on disk.

If space gets above this value, Cassandra will throw WriteTimeoutException on Mutations including tables with CDC enabled. A CDCCompactor is responsible for parsing the raw CDC logs and deleting them when parsing is completed.

The default value is the min of 4096 mb and 1/8th of the total space of the drive where cdc_raw_directory resides.

---

### cdc_free_space_check_interval

**Versions:** 4.1, 5.0

**Default:** 4.1: `250ms` | 5.0: `250ms`

When we hit our cdc_raw limit and the CDCCompactor is either running behind or experiencing backpressure, we check at the following interval to see if any new space for cdc-tracked tables has been made available. Default to 250ms Min unit: ms

---

### cdc_free_space_check_interval_ms

**Versions:** 4.0

**Default:** 4.0: `250`

When we hit our cdc_raw limit and the CDCCompactor is either running behind or experiencing backpressure, we check at the following interval to see if any new space for cdc-tracked tables has been made available. Default to 250ms

---

### cdc_block_writes

**Versions:** 5.0

**Default:** 5.0: `true`

Specify whether writes to the CDC-enabled tables should be blocked when CDC data on disk has reached to the limit. When setting to false, the writes will not be blocked and the oldest CDC data on disk will be deleted to ensure the size constraint. The default is true.

---

### cdc_on_repair_enabled

**Versions:** 5.0

**Default:** 5.0: `true`

Specify whether CDC mutations are replayed through the write path on streaming, e.g. repair. When enabled, CDC data streamed to the destination node will be written into commit log first. When setting to false, the streamed CDC data is written into SSTables just the same as normal streaming. The default is true. If this is set to false, streaming will be considerably faster however it's possible that, in extreme situations (losing > quorum # nodes in a replica set), you may have data in your SSTables that never makes it to the CDC log.

---

## User Defined Functions

### user_defined_functions_enabled

**Versions:** 4.1, 5.0

**Default:** 4.1: `false` | 5.0: `false`

If unset, all GC Pauses greater than gc_log_threshold will log at INFO level UDFs (user defined functions) are disabled by default. As of Cassandra 3.0 there is a sandbox in place that should prevent execution of evil code.

---

### scripted_user_defined_functions_enabled

**Versions:** 4.1

**Default:** 4.1: `false`

Enables scripted UDFs (JavaScript UDFs). Java UDFs are always enabled, if user_defined_functions_enabled is true. Enable this option to be able to use UDFs with "language javascript" or any custom JSR-223 provider. This option has no effect, if user_defined_functions_enabled is false.

---

### enable_user_defined_functions

**Versions:** 4.0

**Default:** 4.0: `false`

If unset, all GC Pauses greater than gc_log_threshold_in_ms will log at INFO level UDFs (user defined functions) are disabled by default. As of Cassandra 3.0 there is a sandbox in place that should prevent execution of evil code.

---

### enable_scripted_user_defined_functions

**Versions:** 4.0

**Default:** 4.0: `false`

Enables scripted UDFs (JavaScript UDFs). Java UDFs are always enabled, if enable_user_defined_functions is true. Enable this option to be able to use UDFs with "language javascript" or any custom JSR-223 provider. This option has no effect, if enable_user_defined_functions is false.

---

## Garbage Collection Logging

### gc_log_threshold

**Versions:** 4.1, 5.0

**Default:** 4.1: `200ms` | 5.0: `200ms`

GC Pauses greater than 200 ms will be logged at INFO level This threshold can be adjusted to minimize logging if necessary Min unit: ms

---

### gc_log_threshold_in_ms

**Versions:** 4.0

**Default:** 4.0: `200`

GC Pauses greater than 200 ms will be logged at INFO level This threshold can be adjusted to minimize logging if necessary

---

### gc_warn_threshold

**Versions:** 4.1, 5.0

**Default:** 4.1: `1000ms` | 5.0: `1000ms`

GC Pauses greater than gc_warn_threshold will be logged at WARN level Adjust the threshold based on your application throughput requirement. Setting to 0 will deactivate the feature. Min unit: ms

---

### gc_warn_threshold_in_ms

**Versions:** 4.0

**Default:** 4.0: `1000`

GC Pauses greater than gc_warn_threshold_in_ms will be logged at WARN level Adjust the threshold based on your application throughput requirement. Setting to 0 will deactivate the feature.

---

## Tombstones

### tombstone_warn_threshold

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `1000` | 4.1: `1000` | 5.0: `1000`

When executing a scan, within or across a partition, we need to keep the tombstones seen in memory so we can return them to the coordinator, which will use them to make sure other replicas also know about the deleted rows. With workloads that generate a lot of tombstones, this can cause performance problems and even exaust the server heap. (http://www.datastax.com/dev/blog/cassandra-anti-patterns-queues-and-queue-like-datasets) Adjust the thresholds here if you understand the dangers and want to scan more tombstones anyway.  These thresholds may also be adjusted at runtime using the StorageService mbean.

---

### tombstone_failure_threshold

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `100000` | 4.1: `100000` | 5.0: `100000`

No description available.

---

## Batch Operations

### batch_size_warn_threshold

**Versions:** 4.1, 5.0

**Default:** 4.1: `5KiB` | 5.0: `5KiB`

Log WARN on any multiple-partition batch size exceeding this value. 5KiB per batch by default. Caution should be taken on increasing the size of this threshold as it can lead to node instability. Min unit: KiB

---

### batch_size_warn_threshold_in_kb

**Versions:** 4.0

**Default:** 4.0: `5`

Log WARN on any multiple-partition batch size exceeding this value. 5kb per batch by default. Caution should be taken on increasing the size of this threshold as it can lead to node instability.

---

### batch_size_fail_threshold

**Versions:** 4.1, 5.0

**Default:** 4.1: `50KiB` | 5.0: `50KiB`

Fail any multiple-partition batch exceeding this value. 50KiB (10x warn threshold) by default. Min unit: KiB

---

### batch_size_fail_threshold_in_kb

**Versions:** 4.0

**Default:** 4.0: `50`

Fail any multiple-partition batch exceeding this value. 50kb (10x warn threshold) by default.

---

### unlogged_batch_across_partitions_warn_threshold

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `10` | 4.1: `10` | 5.0: `10`

Log WARN on any batches not of type LOGGED than span across more partitions than this limit

---

### batchlog_replay_throttle

**Versions:** 4.1, 5.0

**Default:** 4.1: `1024KiB` | 5.0: `1024KiB`

Maximum throttle in KiBs per second, total. This will be reduced proportionally to the number of nodes in the cluster. Min unit: KiB

---

### batchlog_replay_throttle_in_kb

**Versions:** 4.0

**Default:** 4.0: `1024`

Maximum throttle in KBs per second, total. This will be reduced proportionally to the number of nodes in the cluster.

---

### batchlog_endpoint_strategy

**Versions:** 5.0

**Default:** 5.0: `random_remote`

Strategy to choose the batchlog storage endpoints.

Available options:

- random_remote Default, purely random, prevents the local rack, if possible.

- prefer_local Similar to random_remote. Random, except that one of the replications will go to the local rack, which mean it offers lower availability guarantee than random_remote or dynamic_remote.

- dynamic_remote Using DynamicEndpointSnitch to select batchlog storage endpoints, prevents the local rack, if possible. This strategy offers the same availability guarantees as random_remote but selects the fastest endpoints according to the DynamicEndpointSnitch. (DynamicEndpointSnitch currently only tracks reads and not writes - i.e. write-only (or mostly-write) workloads might not benefit from this strategy.) Note: this strategy will fall back to random_remote, if dynamic_snitch is not enabled.

- dynamic Mostly the same as dynamic_remote, except that local rack is not excluded, which mean it offers lower availability guarantee than random_remote or dynamic_remote. Note: this strategy will fall back to random_remote, if dynamic_snitch is not enabled.

---

## Query Processing

### column_index_size

**Versions:** 4.1, 5.0

**Default:** 4.1: `64KiB` | 5.0: `4KiB`

Granularity of the collation index of rows within a partition. Applies to both BIG and BTI SSTable formats. In both formats, a smaller granularity results in faster lookup of rows within a partition, but a bigger index file size. Using smaller granularities with the BIG format is not recommended because bigger collation indexes cannot be cached efficiently or at all if they become sufficiently large. Further, if large rows, or a very large number of rows per partition are present, it is recommended to increase the index granularity or switch to the BTI SSTable format.

Leave undefined to use a default suitable for the SSTable format in use (64 KiB for BIG, 16KiB for BTI). Min unit: KiB

---

### column_index_size_in_kb

**Versions:** 4.0

**Default:** 4.0: `64`

Granularity of the collation index of rows within a partition. Increase if your rows are large, or if you have a very large number of rows per partition.  The competing goals are these:

- a smaller granularity means more index entries are generated and looking up rows withing the partition by collation column is faster - but, Cassandra will keep the collation index in memory for hot rows (as part of the key cache), so a larger granularity means you can cache more hot rows

---

### column_index_cache_size

**Versions:** 4.1, 5.0

**Default:** 4.1: `2KiB` | 5.0: `2KiB`

Per sstable indexed key cache entries (the collation index in memory mentioned above) exceeding this size will not be held on heap. This means that only partition information is held on heap and the index entries are read from disk.

Note that this size refers to the size of the serialized index information and not the size of the partition.

This is only relevant to SSTable formats that use key cache, e.g. BIG. Min unit: KiB

---

### column_index_cache_size_in_kb

**Versions:** 4.0

**Default:** 4.0: `2`

Per sstable indexed key cache entries (the collation index in memory mentioned above) exceeding this size will not be held on heap. This means that only partition information is held on heap and the index entries are read from disk.

Note that this size refers to the size of the serialized index information and not the size of the partition.

---

### enable_materialized_views

**Versions:** 4.0

**Default:** 4.0: `false`

Enables materialized view creation on this node. Materialized views are considered experimental and are not recommended for production use.

---

### enable_sasi_indexes

**Versions:** 4.0

**Default:** 4.0: `false`

Enables SASI index creation on this node. SASI indexes are considered experimental and are not recommended for production use.

---

### sasi_indexes_enabled

**Versions:** 4.1, 5.0

**Default:** 4.1: `false` | 5.0: `false`

Enables SASI index creation on this node. SASI indexes are considered experimental and are not recommended for production use.

---

### enable_transient_replication

**Versions:** 4.0

**Default:** 4.0: `false`

Enables creation of transiently replicated keyspaces on this node. Transient replication is experimental and is not recommended for production use.

---

### transient_replication_enabled

**Versions:** 4.1, 5.0

**Default:** 4.1: `false` | 5.0: `false`

Enables creation of transiently replicated keyspaces on this node. Transient replication is experimental and is not recommended for production use.

---

### enable_drop_compact_storage

**Versions:** 4.0

**Default:** 4.0: `false`

Enables the used of 'ALTER ... DROP COMPACT STORAGE' statements on this node. 'ALTER ... DROP COMPACT STORAGE' is considered experimental and is not recommended for production use.

---

### drop_compact_storage_enabled

**Versions:** 4.1, 5.0

**Default:** 4.1: `false` | 5.0: `false`

Enables the used of 'ALTER ... DROP COMPACT STORAGE' statements on this node. 'ALTER ... DROP COMPACT STORAGE' is considered experimental and is not recommended for production use.

---

### ideal_consistency_level

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `EACH_QUORUM` | 4.1: `EACH_QUORUM` | 5.0: `EACH_QUORUM`

Track a metric per keyspace indicating whether replication achieved the ideal consistency level for writes without timing out. This is different from the consistency level requested by each write which may be lower in order to facilitate availability.

---

### traverse_auth_from_root

**Versions:** 4.1, 5.0

**Default:** 4.1: `false` | 5.0: `false`

Depending on the auth strategy of the cluster, it can be beneficial to iterate from root to table (root -> ks -> table) instead of table to root (table -> ks -> root). As the auth entries are whitelisting, once a permission is found you know it to be valid. We default to false as the legacy behavior is to query at the table level then move back up to the root. See CASSANDRA-17016 for details.

---

### use_statements_enabled

**Versions:** 4.1, 5.0

**Default:** 4.1: `true` | 5.0: `true`

Whether or not USE <keyspace> is allowed. This is enabled by default to avoid failure on upgrade.

---

### read_before_write_list_operations_enabled

**Versions:** 4.1, 5.0

**Default:** 4.1: `true` | 5.0: `true`

Guardrail to allow/disallow list operations that require read before write, i.e. setting list element by index and removing list elements by either index or value. Defaults to true.

---

### replica_filtering_protection

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `(see below)` | 4.1: `(see below)` | 5.0: `(see below)`

Protects against out-of-date replicas causing memory issues.

```yaml
replica_filtering_protection:
  cached_rows_warn_threshold: 2000
  cached_rows_fail_threshold: 32000
```

| Sub-parameter | Description | Default |
|---------------|-------------|---------|
| `cached_rows_warn_threshold` | Warning threshold | `2000` |
| `cached_rows_fail_threshold` | Failure threshold | `32000` |

---

### materialized_views_enabled

**Versions:** 4.1, 5.0

**Default:** 4.1: `false` | 5.0: `false`

Enables materialized view creation on this node. Materialized views are considered experimental and are not recommended for production use.

---

## Indexing

### default_secondary_index

**Versions:** 5.0

**Default:** 5.0: `legacy_local_table`

The default secondary index implementation when CREATE INDEX does not specify one via USING. ex. "legacy_local_table" - (default) legacy secondary index, implemented as a hidden table ex. "sai" - "storage-attched" index, implemented via optimized SSTable/Memtable-attached indexes

---

### default_secondary_index_enabled

**Versions:** 5.0

**Default:** 5.0: `true`

Whether a default secondary index implementation is allowed. If this is "false", CREATE INDEX must specify an index implementation via USING.

---

### sai_options

**Versions:** 5.0

**Default:** 5.0: Not set

Configures Storage Attached Indexing (SAI).

```yaml
sai_options:
  segment_write_buffer_size: 1024MiB
```

| Sub-parameter | Description | Default |
|---------------|-------------|---------|
| `segment_write_buffer_size` | Memory for SAI segments | `1024MiB` |
| `prioritize_over_legacy_index` | Prefer SAI over legacy | `false` |

---

## Audit Logging

### audit_logging_options

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `(see below)` | 4.1: `(see below)` | 5.0: `(see below)`

Configures audit logging for tracking database operations.

```yaml
audit_logging_options:
  enabled: false
  logger:
    - class_name: BinAuditLogger
  audit_logs_dir: /var/log/cassandra/audit
  roll_cycle: HOURLY
  block: true
  max_queue_weight: 268435456
  max_log_size: 17179869184
  max_archive_retries: 10
```

| Sub-parameter | Description | Default |
|---------------|-------------|---------|
| `enabled` | Enable audit logging | `false` |
| `logger.class_name` | Logger implementation: `BinAuditLogger` or `FileAuditLogger` | `BinAuditLogger` |
| `audit_logs_dir` | Directory for audit log files | - |
| `included_keyspaces` | Keyspaces to include (empty = all) | - |
| `excluded_keyspaces` | Keyspaces to exclude | `system, system_schema, system_virtual_schema` |
| `included_categories` | Categories to include (empty = all) | - |
| `excluded_categories` | Categories to exclude | - |
| `included_users` | Users to include (empty = all) | - |
| `excluded_users` | Users to exclude | - |
| `roll_cycle` | Log rotation: `MINUTELY`, `HOURLY`, `DAILY` | `HOURLY` |
| `block` | Block writes when queue is full | `true` |
| `max_queue_weight` | Maximum queue size in bytes | `268435456` (256 MiB) |
| `max_log_size` | Maximum total log size in bytes | `17179869184` (16 GiB) |
| `archive_command` | Script to run on log rotation (`%path` = file path) | - |
| `max_archive_retries` | Maximum archive command retries | `10` |

!!! note "Archiving Behavior"
    If `archive_command` is empty, Cassandra uses a built-in DeletingArchiver that deletes oldest files when `max_log_size` is reached. If set, the script is responsible for cleanup.

---

### full_query_logging_options

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: Not set | 4.1: Not set | 5.0: Not set

Configures full query logging. These defaults can be overridden via `nodetool enablefullquerylog`.

```yaml
full_query_logging_options:
  log_dir: /var/log/cassandra/fql
  roll_cycle: HOURLY
  block: true
  max_queue_weight: 268435456
  max_log_size: 17179869184
  max_archive_retries: 10
```

| Sub-parameter | Description | Default |
|---------------|-------------|---------|
| `log_dir` | Directory for query log files | - |
| `roll_cycle` | Log rotation: `MINUTELY`, `HOURLY`, `DAILY` | `HOURLY` |
| `block` | Block writes when queue is full | `true` |
| `max_queue_weight` | Maximum queue size in bytes | `268435456` (256 MiB) |
| `max_log_size` | Maximum total log size in bytes | `17179869184` (16 GiB) |
| `archive_command` | Script to run on log rotation (`%path` = file path) | - |
| `allow_nodetool_archive_command` | Allow nodetool to set archive_command (security risk) | `false` |
| `max_archive_retries` | Maximum archive command retries | `10` |

!!! warning "Security"
    Enabling `allow_nodetool_archive_command` allows anyone with JMX/nodetool access to run local shell commands as the Cassandra user.

---

## Tracing

### trace_type_query_ttl

**Versions:** 4.1, 5.0

**Default:** 4.1: `1d` | 5.0: `1d`

TTL for different trace types used during logging of the repair process. Min unit: s

---

### trace_type_repair_ttl

**Versions:** 4.1, 5.0

**Default:** 4.1: `7d` | 5.0: `7d`

Min unit: s

---

### tracetype_query_ttl

**Versions:** 4.0

**Default:** 4.0: `86400`

TTL for different trace types used during logging of the repair process.

---

### tracetype_repair_ttl

**Versions:** 4.0

**Default:** 4.0: `604800`

No description available.

---

## Diagnostic Events

### diagnostic_events_enabled

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `false` | 4.1: `false` | 5.0: `false`

Diagnostic Events # If enabled, diagnostic events can be helpful for troubleshooting operational issues. Emitted events contain details on internal state and temporal relationships across events, accessible by clients via JMX.

---

## Index Summary

### index_summary_capacity

**Versions:** 4.1, 5.0

**Default:** 4.1: `Auto` | 5.0: `Auto`

A fixed memory pool size in MB for for SSTable index summaries. If left empty, this will default to 5% of the heap size. If the memory usage of all index summaries exceeds this limit, SSTables with low read rates will shrink their index summaries in order to meet this limit.  However, this is a best-effort process. In extreme conditions Cassandra may need to use more than this amount of memory. Only relevant to formats that use an index summary, e.g. BIG. Min unit: KiB

---

### index_summary_capacity_in_mb

**Versions:** 4.0

**Default:** 4.0: `Auto`

A fixed memory pool size in MB for for SSTable index summaries. If left empty, this will default to 5% of the heap size. If the memory usage of all index summaries exceeds this limit, SSTables with low read rates will shrink their index summaries in order to meet this limit.  However, this is a best-effort process. In extreme conditions Cassandra may need to use more than this amount of memory.

---

### index_summary_resize_interval

**Versions:** 4.1, 5.0

**Default:** 4.1: `60m` | 5.0: `60m`

How frequently index summaries should be resampled.  This is done periodically to redistribute memory from the fixed-size pool to sstables proportional their recent read rates.  Setting to null value will disable this process, leaving existing index summaries at their current sampling level. Only relevant to formats that use an index summary, e.g. BIG. Min unit: m

---

### index_summary_resize_interval_in_minutes

**Versions:** 4.0

**Default:** 4.0: `60`

How frequently index summaries should be resampled.  This is done periodically to redistribute memory from the fixed-size pool to sstables proportional their recent read rates.  Setting to -1 will disable this process, leaving existing index summaries at their current sampling level.

---

## Trickle Fsync

### trickle_fsync

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `false` | 4.1: `false` | 5.0: `false`

Whether to, when doing sequential writing, fsync() at intervals in order to force the operating system to flush the dirty buffers. Enable this to avoid sudden dirty buffer flushing from impacting read latencies. Almost always a good idea on SSDs; not necessarily on platters.

---

### trickle_fsync_interval

**Versions:** 4.1, 5.0

**Default:** 4.1: `10240KiB` | 5.0: `10240KiB`

Min unit: KiB

---

### trickle_fsync_interval_in_kb

**Versions:** 4.0

**Default:** 4.0: `10240`

No description available.

---

## Windows

### windows_timer_interval

**Versions:** 4.0

**Default:** 4.0: `1`

The default Windows kernel timer and scheduling resolution is 15.6ms for power conservation. Lowering this value on Windows can provide much tighter latency and better throughput, however some virtualized environments may see a negative performance impact from changing this setting below their system default. The sysinternals 'clockres' tool can confirm your system's default setting.

---

## Startup Checks

### startup_checks

**Versions:** 4.1, 5.0

**Default:** 4.1: Not set | 5.0: Not set

Controls startup validation checks.

```yaml
startup_checks:
  enabled: true
  check_dc: true
  check_rack: true
```

| Sub-parameter | Description | Default |
|---------------|-------------|---------|
| `enabled` | Enable checks | `true` |
| `check_dc` | Verify datacenter | `true` |
| `check_rack` | Verify rack | `true` |

---

### check_filesystem_ownership

**Versions:** 4.1, 5.0

**Default:** 4.1: Not set | 5.0: Not set

Verifies correct ownership of attached locations on disk at startup. See CASSANDRA-16879 for more details.

---

### check_data_resurrection

**Versions:** 4.1, 5.0

**Default:** 4.1: Not set | 5.0: Not set

Enable this property to fail startup if the node is down for longer than gc_grace_seconds, to potentially prevent data resurrection on tables with deletes. By default, this will run against all keyspaces and tables except the ones specified on excluded_keyspaces and excluded_tables.

---

## Client Error Reporting

### client_error_reporting_exclusions

**Versions:** 4.1, 5.0

**Default:** 4.1: Not set | 5.0: Not set

When the client triggers a protocol exception or unknown issue (Cassandra bug) we increment a client metric showing this; this logic will exclude specific subnets from updating these metrics

---

## Storage Compatibility

### storage_compatibility_mode

**Versions:** 5.0

**Default:** 5.0: `CASSANDRA_4`

This property indicates with what Cassandra major version the storage format will be compatible with.

The chosen storage compatibility mode will determine the versions of the written sstables, commitlogs, hints, etc. For example, if we're going to remain compatible with Cassandra 4.x, the value of this property should be 4, which will make us use sstables in the latest N version of the BIG format.

This will also determine if certain features that depend on newer formats are available. For example, extended TTL (up to 2106) depends on the sstable, commit-log, hints, and messaging versions introduced by Cassandra 5.0, so that feature won't be available if this property is set to CASSANDRA_4. See the upgrade guide for more details.

Possible values are:

- **CASSANDRA_4**: Stays compatible with the 4.x line in features, formats and component versions.
- **UPGRADING**: The cluster monitors the version of each node during this interim stage. This has a cost but ensures all new features, formats, versions, etc. are enabled safely.
- **NONE**: Start with all the new features and formats enabled.

A typical upgrade would be:

1. Do a rolling upgrade, starting all nodes in CASSANDRA_X compatibility mode.
2. Once the new binary is rendered stable, do a rolling restart with the UPGRADING mode. The cluster will keep new features disabled until all nodes are started in the UPGRADING mode; when that happens, new features controlled by the storage compatibility mode are enabled.
3. Do a rolling restart with all nodes starting with the NONE mode. This eliminates the cost of checking node versions and ensures stability. If Cassandra was started at the previous version by accident, a node with disabled compatibility mode would no longer toggle behaviors as when it was running in the UPGRADING mode.

---

## Dynamic Data Masking

### dynamic_data_masking_enabled

**Versions:** 5.0

**Default:** 5.0: `false`

If enabled, dynamic data masking allows to attach CQL masking functions to the columns of a table. Users without the UNMASK permission will see an obscured version of the values of the columns with an attached mask. If dynamic data masking is disabled it won't be allowed to create new column masks, although it will still be possible to drop any previously existing masks. Also, any existing mask will be ignored at query time, so all users will see the clear values of the masked columns. Defaults to false to disable dynamic data masking.

---

## Corrupted Tombstones

### corrupted_tombstone_strategy

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: `disabled` | 4.1: `disabled` | 5.0: `disabled`

validate tombstones on reads and compaction can be either "disabled", "warn" or "exception"

---

## DNS

### resolve_multiple_ip_addresses_per_dns_record

**Versions:** 5.0

**Default:** 5.0: Not set

If set to "true", SimpleSeedProvider will return all IP addresses for a DNS name, based on the configured name service on the system. Defaults to "false".

---

## Archive

### archive_command

**Versions:** 4.0, 4.1, 5.0

**Default:** 4.0: Not set | 4.1: Not set | 5.0: Not set

If archive_command is empty or unset, Cassandra uses a built-in DeletingArchiver that deletes the oldest files if ``max_log_size`` is reached. If archive_command is set, Cassandra does not use DeletingArchiver, so it is the responsibility of the script to make any required cleanup. Example: "/path/to/script.sh %path" where %path is replaced with the file being rolled.

---

### allow_nodetool_archive_command

**Versions:** 4.1, 5.0

**Default:** 4.1: Not set | 5.0: Not set

note that enabling this allows anyone with JMX/nodetool access to run local shell commands as the user running cassandra

---

## Heap Dump

### dump_heap_on_uncaught_exception

**Versions:** 5.0

**Default:** 5.0: `true`

Enable / disable automatic dump of heap on first uncaught exception If not set, the default value is false

---

### heap_dump_path

**Versions:** 5.0

**Default:** 5.0: `/var/lib/cassandra/heapdump`

Directory where Cassandra should store results of a One-Shot troubleshooting heapdump for uncaught exceptions. Note: this value can be overridden by the -XX:HeapDumpPath JVM env param with a relative local path for testing if so desired. If not set, the default directory is $CASSANDRA_HOME/heapdump

---

## Guardrails

Guardrails protect the cluster by warning or failing operations that exceed configured thresholds.
Most guardrails were introduced in Cassandra 4.1 with additional ones added in 5.0.

!!! note "Guardrail Types"
    - **warn_threshold**: Logs a warning but allows the operation
    - **fail_threshold**: Rejects the operation with an error
    - **_enabled**: Toggles the feature on/off
    - **_warned**: Warns on specific values
    - **_disallowed**: Rejects specific values

### Schema Guardrails

| Parameter | Description | Versions |
|-----------|-------------|----------|
| `keyspaces_warn_threshold` | Warn when creating more keyspaces than threshold | 4.1, 5.0 |
| `keyspaces_fail_threshold` | Fail when creating more keyspaces than threshold | 4.1, 5.0 |
| `tables_warn_threshold` | Warn when creating more tables than threshold | 4.1, 5.0 |
| `tables_fail_threshold` | Fail when creating more tables than threshold | 4.1, 5.0 |
| `columns_per_table_warn_threshold` | Warn when table has more columns than threshold | 4.1, 5.0 |
| `columns_per_table_fail_threshold` | Fail when table has more columns than threshold | 4.1, 5.0 |
| `fields_per_udt_warn_threshold` | Warn when UDT has more fields than threshold | 4.1, 5.0 |
| `fields_per_udt_fail_threshold` | Fail when UDT has more fields than threshold | 4.1, 5.0 |

### Index Guardrails

| Parameter | Description | Versions |
|-----------|-------------|----------|
| `secondary_indexes_enabled` | Enable/disable secondary index creation | 4.1, 5.0 |
| `secondary_indexes_per_table_warn_threshold` | Warn when table has more secondary indexes than threshold | 4.1, 5.0 |
| `secondary_indexes_per_table_fail_threshold` | Fail when table has more secondary indexes than threshold | 4.1, 5.0 |
| `materialized_views_per_table_warn_threshold` | Warn when table has more MVs than threshold | 4.1, 5.0 |
| `materialized_views_per_table_fail_threshold` | Fail when table has more MVs than threshold | 4.1, 5.0 |
| `non_partition_restricted_index_query_enabled` | Enable/disable non-partition-restricted index queries | 5.0 |

### SAI Guardrails (5.0+)

| Parameter | Description | Versions |
|-----------|-------------|----------|
| `sai_string_term_size_warn_threshold` | Warn on large SAI string terms | 5.0 |
| `sai_string_term_size_fail_threshold` | Fail on large SAI string terms | 5.0 |
| `sai_frozen_term_size_warn_threshold` | Warn on large SAI frozen terms | 5.0 |
| `sai_frozen_term_size_fail_threshold` | Fail on large SAI frozen terms | 5.0 |
| `sai_vector_term_size_warn_threshold` | Warn on large SAI vector terms | 5.0 |
| `sai_vector_term_size_fail_threshold` | Fail on large SAI vector terms | 5.0 |
| `sai_sstable_indexes_per_query_warn_threshold` | Warn when query touches many SAI indexes | 5.0 |
| `sai_sstable_indexes_per_query_fail_threshold` | Fail when query touches many SAI indexes | 5.0 |

### Data Size Guardrails

| Parameter | Description | Versions |
|-----------|-------------|----------|
| `partition_size_warn_threshold` | Warn on partitions larger than threshold | 5.0 |
| `partition_size_fail_threshold` | Fail on partitions larger than threshold | 5.0 |
| `partition_tombstones_warn_threshold` | Warn on partitions with too many tombstones | 5.0 |
| `partition_tombstones_fail_threshold` | Fail on partitions with too many tombstones | 5.0 |
| `collection_size_warn_threshold` | Warn on collections larger than threshold | 4.1, 5.0 |
| `collection_size_fail_threshold` | Fail on collections larger than threshold | 4.1, 5.0 |
| `items_per_collection_warn_threshold` | Warn on collections with too many items | 4.1, 5.0 |
| `items_per_collection_fail_threshold` | Fail on collections with too many items | 4.1, 5.0 |
| `column_value_size_warn_threshold` | Warn on column values larger than threshold | 5.0 |
| `column_value_size_fail_threshold` | Fail on column values larger than threshold | 5.0 |

### Query Guardrails

| Parameter | Description | Versions |
|-----------|-------------|----------|
| `page_size_warn_threshold` | Warn on queries with page size larger than threshold | 4.1, 5.0 |
| `page_size_fail_threshold` | Fail on queries with page size larger than threshold | 4.1, 5.0 |
| `partition_keys_in_select_warn_threshold` | Warn when IN restriction has too many partition keys | 4.1, 5.0 |
| `partition_keys_in_select_fail_threshold` | Fail when IN restriction has too many partition keys | 4.1, 5.0 |
| `in_select_cartesian_product_warn_threshold` | Warn when IN creates large cartesian product | 4.1, 5.0 |
| `in_select_cartesian_product_fail_threshold` | Fail when IN creates large cartesian product | 4.1, 5.0 |
| `allow_filtering_enabled` | Enable/disable ALLOW FILTERING queries | 4.1, 5.0 |
| `group_by_enabled` | Enable/disable GROUP BY functionality | 4.1, 5.0 |

### Read Size Guardrails

| Parameter | Description | Versions |
|-----------|-------------|----------|
| `local_read_size_warn_threshold` | Warn on reads larger than threshold at local node | 4.1, 5.0 |
| `local_read_size_fail_threshold` | Fail on reads larger than threshold at local node | 4.1, 5.0 |
| `coordinator_read_size_warn_threshold` | Warn on reads larger than threshold at coordinator | 4.1, 5.0 |
| `coordinator_read_size_fail_threshold` | Fail on reads larger than threshold at coordinator | 4.1, 5.0 |
| `row_index_read_size_warn_threshold` | Warn on row index reads larger than threshold | 4.1, 5.0 |
| `row_index_read_size_fail_threshold` | Fail on row index reads larger than threshold | 4.1, 5.0 |
| `read_thresholds_enabled` | Enable/disable read size thresholds | 4.1, 5.0 |

### Consistency Level Guardrails

| Parameter | Description | Versions |
|-----------|-------------|----------|
| `read_consistency_levels_warned` | Warn on these read consistency levels | 4.1, 5.0 |
| `read_consistency_levels_disallowed` | Disallow these read consistency levels | 4.1, 5.0 |
| `write_consistency_levels_warned` | Warn on these write consistency levels | 4.1, 5.0 |
| `write_consistency_levels_disallowed` | Disallow these write consistency levels | 4.1, 5.0 |

### Replication Guardrails

| Parameter | Description | Versions |
|-----------|-------------|----------|
| `minimum_replication_factor_warn_threshold` | Warn when RF below threshold | 4.1, 5.0 |
| `minimum_replication_factor_fail_threshold` | Fail when RF below threshold | 4.1, 5.0 |
| `maximum_replication_factor_warn_threshold` | Warn when RF above threshold | 5.0 |
| `maximum_replication_factor_fail_threshold` | Fail when RF above threshold | 5.0 |
| `simplestrategy_enabled` | Enable/disable SimpleStrategy | 5.0 |

### Timestamp Guardrails

| Parameter | Description | Versions |
|-----------|-------------|----------|
| `user_timestamps_enabled` | Enable/disable user-provided timestamps | 4.1, 5.0 |
| `minimum_timestamp_warn_threshold` | Warn on timestamps below threshold | 5.0 |
| `minimum_timestamp_fail_threshold` | Fail on timestamps below threshold | 5.0 |
| `maximum_timestamp_warn_threshold` | Warn on timestamps above threshold | 5.0 |
| `maximum_timestamp_fail_threshold` | Fail on timestamps above threshold | 5.0 |

### DDL Guardrails

| Parameter | Description | Versions |
|-----------|-------------|----------|
| `drop_truncate_table_enabled` | Enable/disable DROP/TRUNCATE table | 4.1, 5.0 |
| `drop_keyspace_enabled` | Enable/disable DROP KEYSPACE | 5.0 |
| `alter_table_enabled` | Enable/disable ALTER TABLE | 5.0 |
| `uncompressed_tables_enabled` | Enable/disable uncompressed tables | 4.1, 5.0 |
| `table_properties_warned` | Warn on these table properties | 4.1, 5.0 |
| `table_properties_disallowed` | Disallow these table properties | 4.1, 5.0 |

### Partition Denylist

| Parameter | Description | Versions |
|-----------|-------------|----------|
| `partition_denylist_enabled` | Enable partition denylist feature | 4.1, 5.0 |
| `denylist_reads_enabled` | Enable read operations on denylisted partitions | 4.1, 5.0 |
| `denylist_writes_enabled` | Enable write operations on denylisted partitions | 4.1, 5.0 |
| `denylist_range_reads_enabled` | Enable range reads on denylisted partitions | 4.1, 5.0 |

### TWCS Guardrails

| Parameter | Description | Versions |
|-----------|-------------|----------|
| `zero_ttl_on_twcs_enabled` | Enable/disable zero TTL on TWCS tables | 5.0 |
| `zero_ttl_on_twcs_warned` | Warn on zero TTL on TWCS tables | 5.0 |

### Vector Guardrails (5.0+)

| Parameter | Description | Versions |
|-----------|-------------|----------|
| `vector_dimensions_warn_threshold` | Warn on vectors with too many dimensions | 5.0 |
| `vector_dimensions_fail_threshold` | Fail on vectors with too many dimensions | 5.0 |

### Disk Usage Guardrails

| Parameter | Description | Versions |
|-----------|-------------|----------|
| `data_disk_usage_percentage_warn_threshold` | Warn when disk usage exceeds percentage | 4.1, 5.0 |
| `data_disk_usage_percentage_fail_threshold` | Fail when disk usage exceeds percentage | 4.1, 5.0 |
