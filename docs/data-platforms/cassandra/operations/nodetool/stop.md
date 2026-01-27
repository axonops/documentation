---
title: "nodetool stop"
description: "Stop compaction operations in Cassandra using nodetool stop command."
meta:
  - name: keywords
    content: "nodetool stop, stop compaction, cancel compaction, Cassandra"
---

# nodetool stop

Stops compaction operations.

---

## Synopsis

```bash
nodetool [connection_options] stop [options] <compaction_type>
```

## Description

`nodetool stop` interrupts running compaction operations. This is useful when compaction is impacting cluster performance or when emergency intervention is needed.

---

## Arguments

| Argument | Description |
|----------|-------------|
| `compaction_type` | Type of compaction to stop |

---

## Options

| Option | Description |
|--------|-------------|
| `-id, --compaction-id <id>` | Stop a specific compaction by its ID (from `compactionstats`) |

### Compaction Types

| Type | Description |
|------|-------------|
| `COMPACTION` | Regular compaction |
| `VALIDATION` | Repair validation (Merkle tree) |
| `CLEANUP` | Cleanup after topology change |
| `SCRUB` | Scrub operation |
| `UPGRADE_SSTABLES` | SSTable upgrade |
| `INDEX_BUILD` | Secondary index builds |
| `VIEW_BUILD` | Materialized view builds |
| `INDEX_SUMMARY` | Index summary redistribution |
| `TOMBSTONE_COMPACTION` | Tombstone-only compaction |
| `ANTICOMPACTION` | Post-repair anticompaction |
| `VERIFY` | Verification operations |
| `RELOCATE` | SSTable relocation |
| `GARBAGE_COLLECT` | Garbage collection compaction |

---

## Examples

### Stop Regular Compaction

```bash
nodetool stop COMPACTION
```

### Stop Validation (During Repair)

```bash
nodetool stop VALIDATION
```

### Stop Cleanup

```bash
nodetool stop CLEANUP
```

### Stop Index Build

```bash
nodetool stop INDEX_BUILD
```

### Stop View Build

```bash
nodetool stop VIEW_BUILD
```

### Stop Specific Compaction by ID

```bash
# First, get the compaction ID from compactionstats
nodetool compactionstats

# Stop specific compaction by ID
nodetool stop -id 12345678-1234-1234-1234-123456789abc COMPACTION
```

### Stop All Types

```bash
nodetool stop COMPACTION
nodetool stop VALIDATION
nodetool stop CLEANUP
```

---

## When to Use

### Emergency: High Latency

When compaction is causing unacceptable latency:

```bash
# Check if compaction is the cause
nodetool compactionstats

# Stop compaction
nodetool stop COMPACTION
```

### Disk Full

When disk is critically low:

```bash
# Stop compaction immediately
nodetool stop COMPACTION

# Free space
nodetool clearsnapshot

# Consider reducing compaction throughput before resuming
nodetool setcompactionthroughput 32
```

### Slow Repair

When repair validation is taking too long:

```bash
# Check repair status
nodetool repair_admin list

# Stop the validation
nodetool stop VALIDATION

# Cancel the repair
nodetool repair_admin cancel <id>
```

---

## Behavior

!!! info "Stop Behavior"
    When stopped:

    - Current compaction is interrupted
    - Partial work is discarded
    - Compaction will restart automatically
    - Manual compaction needs to be re-run

### Auto-Resume

Automatic compactions resume based on the compaction strategy. To prevent immediate restart:

```bash
# Stop compaction
nodetool stop COMPACTION

# Disable auto-compaction for specific table
nodetool disableautocompaction my_keyspace my_table
```

---

## Verification

### Before Stop

```bash
# See what's running
nodetool compactionstats
```

### After Stop

```bash
# Verify stopped
nodetool compactionstats
# Should show fewer or no active compactions
```

---

## Impact

| Stop Type | Impact |
|-----------|--------|
| COMPACTION | SSTable count may grow |
| VALIDATION | Repair incomplete |
| CLEANUP | Extra data remains temporarily |
| INDEX_BUILD | Index incomplete |
| VIEW_BUILD | Materialized view incomplete |
| GARBAGE_COLLECT | Garbage not collected |

---

## Workflow: Performance Issue

```bash
# 1. Identify compaction causing issues
nodetool compactionstats

# 2. Stop the compaction type
nodetool stop COMPACTION

# 3. Reduce throughput
nodetool setcompactionthroughput 32

# 4. Allow compaction to resume at lower rate
# (auto-compaction restarts automatically)

# 5. Monitor
watch nodetool compactionstats
```

---

## Common Scenarios

### Scenario: Large Compaction Blocking Operations

```bash
# Stop the compaction
nodetool stop COMPACTION

# Reduce compaction impact
nodetool setcompactionthroughput 32
nodetool setconcurrentcompactors 1
```

### Scenario: Repair Taking Too Long

```bash
# Stop validation
nodetool stop VALIDATION

# Wait for current segment to finish
sleep 30

# Restart with smaller scope
nodetool repair -pr my_keyspace
```

---

## Important Considerations

!!! warning "Stopping Compaction"
    - Does not prevent future compactions
    - SSTable count will grow
    - Read performance may degrade
    - Disk usage may increase
    - Should be temporary

### Don't Use For

- Routine operations (use throughput tuning instead)
- Long-term compaction control (use strategy tuning)
- Disk space issues (will make worse long-term)

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [compactionstats](compactionstats.md) | View running compactions |
| [setcompactionthroughput](setcompactionthroughput.md) | Control compaction speed |
| [compact](compact.md) | Force compaction |
| [repair_admin](repair_admin.md) | Manage repair sessions |