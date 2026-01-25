---
title: "nodetool describering"
description: "Show token ring information for a keyspace using nodetool describering command."
meta:
  - name: keywords
    content: "nodetool describering, token ring, Cassandra ring, keyspace tokens"
---

# nodetool describering

Displays detailed token range information for a keyspace.

---

## Synopsis

```bash
nodetool [connection_options] describering <keyspace>
```

## Description

`nodetool describering` shows the token ranges for a keyspace, including the start and end tokens for each range and which nodes are responsible for each range. This provides more detail than `ring` by showing the actual replica endpoints for each token range.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `keyspace` | Required. The keyspace to describe |

---

## Output Format

```
Schema Version:a1b2c3d4-e5f6-7890-abcd-ef1234567890
TokenRange:
TokenRange(start_token:-9223372036854775808, end_token:-6148914691236517206, endpoints:[192.168.1.101, 192.168.1.102, 192.168.1.103], rpc_endpoints:[192.168.1.101, 192.168.1.102, 192.168.1.103], endpoint_details:[EndpointDetails(host:192.168.1.101, datacenter:dc1, rack:rack1), ...])
TokenRange(start_token:-6148914691236517206, end_token:-3074457345618258604, endpoints:[192.168.1.102, 192.168.1.103, 192.168.1.101], ...)
...
```

Note: The command prints a single `Schema Version:` line (the local node's schema version), followed by a `TokenRange:` header and the list of token ranges.

---

## Output Fields

| Field | Description |
|-------|-------------|
| `start_token` | Beginning of the token range (exclusive) |
| `end_token` | End of the token range (inclusive) |
| `endpoints` | IP addresses of replica nodes |
| `rpc_endpoints` | Client-facing addresses |
| `endpoint_details` | Datacenter and rack for each endpoint |

---

## Examples

### Describe Keyspace Token Ranges

```bash
nodetool describering my_keyspace
```

### Filter TokenRange Lines

```bash
nodetool describering my_keyspace | grep TokenRange
```

Note: The command does not support JSON or YAML output formats.

### Count Token Ranges

```bash
nodetool describering my_keyspace | grep -c "TokenRange"
```

---

## Use Cases

### Find Replicas for Token Range

```bash
# Find which nodes own a specific token range
nodetool describering my_keyspace | grep "start_token:-614891"
```

### Verify Replication Factor

```bash
# Count endpoints per range (should equal RF)
nodetool describering my_keyspace | head -1 | grep -o "192.168" | wc -l
```

### Check Datacenter Distribution

```bash
# See datacenter placement for each range
nodetool describering my_keyspace | grep "datacenter:"
```

---

## Understanding Token Ranges

### Range Ownership

```
TokenRange(start_token:-9223372036854775808, end_token:-6148914691236517206, ...)
```

This means:
- Data with tokens from -9223372036854775808 to -6148914691236517206
- Is stored on the listed endpoints

### Wrap-Around Range

The token ring is circular. The last range wraps around:

```
TokenRange(start_token:6148914691236517204, end_token:-9223372036854775808, ...)
```

This range covers from the highest token back to the lowest (wrap-around).

---

## Comparing with nodetool ring

| Command | Shows | Best For |
|---------|-------|----------|
| `nodetool ring` | All tokens for all nodes | Overall token distribution |
| `nodetool describering` | Token ranges with replicas | Finding replicas for ranges |
| `nodetool getendpoints` | Replicas for specific key | Finding replicas for a key |

---

## Multi-Datacenter Output

With NetworkTopologyStrategy:

```
TokenRange(
  start_token:-9223372036854775808,
  end_token:-6148914691236517206,
  endpoints:[
    192.168.1.101,  # DC1
    192.168.1.102,  # DC1
    192.168.1.103,  # DC1
    192.168.2.101,  # DC2
    192.168.2.102,  # DC2
    192.168.2.103   # DC2
  ],
  endpoint_details:[
    EndpointDetails(host:192.168.1.101, datacenter:dc1, rack:rack1),
    EndpointDetails(host:192.168.1.102, datacenter:dc1, rack:rack2),
    ...
  ]
)
```

---

## Troubleshooting with Describering

### Verify Rack Awareness

```bash
# Check that replicas are spread across racks
nodetool describering my_keyspace | grep -A10 "TokenRange" | head -20
```

Each range should have replicas in different racks.

### Check for Missing Replicas

```bash
# Count endpoints per range
nodetool describering my_keyspace | grep "endpoints:" | head -5
```

If count doesn't match RF, investigate topology issues.

### Verify Datacenter Coverage

```bash
# Ensure both DCs have replicas
nodetool describering my_keyspace | grep "datacenter:" | sort | uniq -c
```

---

## Scripting Example

### Extract All Endpoints for a Keyspace

```bash
#!/bin/bash
# List all unique endpoints for a keyspace

nodetool describering $1 | \
  grep -oP '(?<=endpoints:\[)[^\]]+' | \
  tr ',' '\n' | \
  sort -u
```

### Validate Replication

```bash
#!/bin/bash
# Verify RF matches expected value

KS=$1
EXPECTED_RF=$2

ACTUAL_RF=$(nodetool describering $KS | \
  head -1 | \
  grep -oP '(?<=endpoints:\[)[^\]]+' | \
  tr ',' '\n' | wc -l)

if [ "$ACTUAL_RF" -eq "$EXPECTED_RF" ]; then
  echo "RF is correct: $ACTUAL_RF"
else
  echo "WARNING: Expected RF $EXPECTED_RF but found $ACTUAL_RF"
fi
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [ring](ring.md) | Simpler token distribution view |
| [status](status.md) | Node status overview |
| [getendpoints](getendpoints.md) | Find replicas for specific key |
| [gossipinfo](gossipinfo.md) | Detailed node information |
