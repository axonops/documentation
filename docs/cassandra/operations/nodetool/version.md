---
title: "nodetool version"
description: "Display Cassandra version information using nodetool version command."
meta:
  - name: keywords
    content: "nodetool version, Cassandra version, version info"
---

# nodetool version

Displays the Cassandra version running on the node.

---

## Synopsis

```bash
nodetool [connection_options] version
```

## Description

`nodetool version` returns the release version of the Cassandra instance running on the connected node. This is essential for:

- Verifying deployment consistency across nodes
- Confirming successful upgrades
- Troubleshooting compatibility issues
- Documentation and audit purposes

---

## Output

### Standard Output

```
ReleaseVersion: 4.1.3
```

The version follows semantic versioning: `MAJOR.MINOR.PATCH`

| Component | Meaning |
|-----------|---------|
| MAJOR | Significant changes, may include breaking changes |
| MINOR | New features, backward compatible |
| PATCH | Bug fixes, backward compatible |

---

## Examples

### Basic Usage

```bash
nodetool version
```

Output:
```
ReleaseVersion: 4.1.3
```

### Check Remote Node

```bash
nodetool -h 192.168.1.100 version
```

### Cluster-Wide Version Check

```bash
# Check all nodes
for node in node1 node2 node3 node4 node5; do
    echo -n "$node: "
    nodetool -h $node version
done
```

Output:
```
node1: ReleaseVersion: 4.1.3
node2: ReleaseVersion: 4.1.3
node3: ReleaseVersion: 4.1.3
node4: ReleaseVersion: 4.1.3
node5: ReleaseVersion: 4.1.3
```

### Version Only (Scripting)

```bash
nodetool version | awk '{print $2}'
```

Output:
```
4.1.3
```

---

## When to Use

### Pre-Upgrade Verification

Document current versions before upgrading:

```bash
echo "=== Pre-Upgrade Versions ==="
for node in $(nodetool status | grep -E "^UN|^DN" | awk '{print $2}'); do
    echo "$node: $(nodetool -h $node version | awk '{print $2}')"
done > pre_upgrade_versions.txt
```

### Post-Upgrade Verification

Confirm all nodes upgraded successfully:

```bash
echo "=== Post-Upgrade Verification ==="
expected="4.1.4"
for node in $(nodetool status | grep -E "^UN|^DN" | awk '{print $2}'); do
    actual=$(nodetool -h $node version | awk '{print $2}')
    if [ "$actual" = "$expected" ]; then
        echo "$node: $actual ✓"
    else
        echo "$node: $actual ✗ (expected $expected)"
    fi
done
```

### Mixed Version Detection

Identify nodes running different versions:

```bash
# Collect all versions
nodetool status | grep -E "^UN|^DN" | awk '{print $2}' | while read node; do
    nodetool -h $node version
done | sort | uniq -c
```

Output showing mixed versions:
```
      3 ReleaseVersion: 4.1.3
      2 ReleaseVersion: 4.1.2
```

### Compatibility Checking

Before connecting tools or drivers:

```bash
version=$(nodetool version | awk '{print $2}')
major=$(echo $version | cut -d. -f1)

if [ "$major" -ge 4 ]; then
    echo "Cassandra 4.x features available"
else
    echo "Running Cassandra 3.x or earlier"
fi
```

---

## Version Compatibility

### Major Version Features

| Version | Key Features |
|---------|--------------|
| 5.0 | Accord, Vector Search, Unified Compaction |
| 4.1 | Guardrails, Pluggable memtable |
| 4.0 | Virtual tables, Audit logging, Full query logging |
| 3.11 | Last 3.x release, LTS |
| 3.0 | Materialized views, SASI indexes |

### Upgrade Path Considerations

| From | To | Notes |
|------|------|-------|
| 3.11.x | 4.0.x | Supported direct upgrade |
| 3.0.x | 4.0.x | Upgrade to 3.11.x first |
| 4.0.x | 4.1.x | Supported direct upgrade |
| 4.1.x | 5.0.x | Supported direct upgrade |

!!! warning "Mixed Versions"
    Running mixed versions should only be temporary during rolling upgrades. All nodes should run the same version in steady state.

---

## Detailed Version Information

For more comprehensive version and build details:

```bash
# Version only
nodetool version

# Full node information including version
nodetool info | head -10
```

### Additional Version Details from info

```bash
nodetool info
```

Shows:
```
ID                     : 12345678-1234-1234-1234-123456789012
Gossip active          : true
Native Transport active: true
Load                   : 256.5 GiB
Generation No          : 1699876543
Uptime (seconds)       : 864000
Heap Memory (MB)       : 4096.00 / 8192.00
...
```

---

## Version Verification Script

```bash
#!/bin/bash
# check_cluster_versions.sh - Verify all nodes run expected version

EXPECTED_VERSION="${1:-}"

if [ -z "$EXPECTED_VERSION" ]; then
    echo "Usage: $0 <expected_version>"
    echo "Example: $0 4.1.3"
    exit 1
fi

echo "Checking cluster for version: $EXPECTED_VERSION"
echo "============================================="

# Get all nodes from status
nodes=$(nodetool status | grep -E "^UN|^DN|^UJ|^UL" | awk '{print $2}')
mismatch=0
unreachable=0

for node in $nodes; do
    actual=$(nodetool -h $node version 2>/dev/null | awk '{print $2}')

    if [ -z "$actual" ]; then
        echo "$node: UNREACHABLE"
        ((unreachable++))
    elif [ "$actual" = "$EXPECTED_VERSION" ]; then
        echo "$node: $actual ✓"
    else
        echo "$node: $actual ✗ (expected $EXPECTED_VERSION)"
        ((mismatch++))
    fi
done

echo "============================================="
echo "Summary:"
echo "  Expected version: $EXPECTED_VERSION"
echo "  Version mismatches: $mismatch"
echo "  Unreachable nodes: $unreachable"

if [ $mismatch -gt 0 ] || [ $unreachable -gt 0 ]; then
    exit 1
fi
echo "All nodes running expected version"
```

---

## Monitoring Integration

### Prometheus/Metrics

```bash
# Export version as metric
version=$(nodetool version | awk '{print $2}')
echo "cassandra_version{version=\"$version\"} 1"
```

### Health Check Script

```bash
#!/bin/bash
# Include version in health check output

health_check() {
    local node=$1
    local version=$(nodetool -h $node version 2>/dev/null | awk '{print $2}')
    local status=$(nodetool -h $node status 2>/dev/null | grep "$(hostname -i)" | awk '{print $1}')

    echo "{\"node\": \"$node\", \"version\": \"$version\", \"status\": \"$status\"}"
}

health_check localhost
```

---

## Troubleshooting

### Cannot Connect to Node

```bash
nodetool version
# Error: Failed to connect to '127.0.0.1:7199'
```

**Causes:**
- Cassandra not running
- JMX not enabled
- Firewall blocking JMX port

**Resolution:**
```bash
# Check if Cassandra is running
pgrep -f CassandraDaemon

# Check JMX port
netstat -tlnp | grep 7199

# Check logs
tail /var/log/cassandra/system.log
```

### Version Mismatch After Upgrade

If nodes show different versions after upgrade:

```bash
# Verify package version
dpkg -l | grep cassandra  # Debian/Ubuntu
rpm -qa | grep cassandra  # RHEL/CentOS

# Verify running version
nodetool version

# If mismatch, may need restart
systemctl restart cassandra
```

---

## Related Information

### Version in Logs

Cassandra logs the version on startup:

```bash
grep -i "cassandra version" /var/log/cassandra/system.log | tail -1
```

### Version in System Tables

```sql
-- CQL query for version
SELECT release_version FROM system.local;
```

### Build Information

For detailed build info:

```bash
# Check build info in logs
grep -i "build" /var/log/cassandra/system.log | head -5

# Or from cassandra binary
cassandra -v
```

---

## Best Practices

!!! tip "Version Management Guidelines"

    1. **Document versions** - Maintain records of deployed versions
    2. **Verify after upgrades** - Always check all nodes post-upgrade
    3. **Minimize mixed time** - Complete rolling upgrades promptly
    4. **Monitor for drift** - Include version in monitoring
    5. **Test compatibility** - Verify driver/tool compatibility with version
    6. **Follow upgrade paths** - Don't skip major versions

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [info](info.md) | Detailed node information |
| [describecluster](describecluster.md) | Cluster-wide information |
| [status](status.md) | Cluster status overview |
| [upgradesstables](upgradesstables.md) | Upgrade SSTable format |
