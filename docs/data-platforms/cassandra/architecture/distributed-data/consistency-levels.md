---
title: "Cassandra Consistency Levels Reference"
description: "Quick reference for Cassandra consistency levels. Tables for read/write levels, quorum calculations, and multi-datacenter behavior."
meta:
  - name: keywords
    content: "consistency level reference, QUORUM, LOCAL_QUORUM, ONE, ALL, Cassandra"
search:
  boost: 3
---

# Consistency Levels Reference

This page provides quick-reference tables for Cassandra consistency levels. For detailed explanations of how consistency works, see [Consistency](consistency.md).

---

## Write Consistency Levels

| Level | Replicas Required | Description | Availability |
|-------|-------------------|-------------|--------------|
| `ANY` | 1 (including hints) | Write succeeds if any node (including coordinator) acknowledges. May store as hint only. | Highest |
| `ONE` | 1 | Single replica must acknowledge | High |
| `TWO` | 2 | Two replicas must acknowledge | Medium |
| `THREE` | 3 | Three replicas must acknowledge | Medium |
| `QUORUM` | ⌊RF/2⌋ + 1 (global) | Majority of all replicas across all datacenters | Medium |
| `LOCAL_ONE` | 1 (local DC) | Single replica in coordinator's datacenter | High |
| `LOCAL_QUORUM` | ⌊local_RF/2⌋ + 1 | Majority in coordinator's datacenter only | High |
| `EACH_QUORUM` | ⌊RF/2⌋ + 1 per DC | Majority in every datacenter | Low |
| `ALL` | RF (all replicas) | Every replica must acknowledge | Lowest |

---

## Read Consistency Levels

| Level | Replicas Contacted | Description | Availability |
|-------|-------------------|-------------|--------------|
| `ONE` | 1 | Single replica responds | Highest |
| `TWO` | 2 | Two replicas respond; newest returned | High |
| `THREE` | 3 | Three replicas respond; newest returned | Medium |
| `QUORUM` | ⌊RF/2⌋ + 1 (global) | Majority of all replicas; newest returned | Medium |
| `LOCAL_ONE` | 1 (local DC) | Single replica in coordinator's datacenter | Highest |
| `LOCAL_QUORUM` | ⌊local_RF/2⌋ + 1 | Majority in coordinator's datacenter; newest returned | High |
| `ALL` | RF (all replicas) | All replicas respond; newest returned | Lowest |

!!! note "EACH_QUORUM"
    `EACH_QUORUM` is **write-only**. It is not supported for read operations.

---

## Serial Consistency Levels (LWT)

Lightweight transactions use separate consistency levels for the Paxos consensus phase.

| Level | Scope | Description |
|-------|-------|-------------|
| `SERIAL` | All datacenters | Paxos consensus across all replicas globally |
| `LOCAL_SERIAL` | Local datacenter | Paxos consensus within coordinator's datacenter only |

See [Lightweight Transactions](../../cql/dml/lightweight-transactions.md) for CQL syntax and [Paxos](paxos.md) for architecture details.

---

## Quorum Calculation

**Formula:** `QUORUM = floor(RF / 2) + 1`

| Replication Factor | QUORUM | Can Tolerate Failures |
|-------------------|--------|----------------------|
| 1 | 1 | 0 |
| 2 | 2 | 0 |
| 3 | 2 | 1 |
| 4 | 3 | 1 |
| 5 | 3 | 2 |
| 6 | 4 | 2 |
| 7 | 4 | 3 |

---

## Multi-Datacenter Behavior

For a cluster with RF=3 per datacenter (total RF=6 across 2 DCs):

| Level | Replicas Required | Cross-DC Wait | DC Failure Tolerance |
|-------|-------------------|---------------|---------------------|
| `ONE` | 1 (any DC) | No | Yes |
| `LOCAL_ONE` | 1 (local DC) | No | Yes |
| `QUORUM` | 4 (any DCs) | Yes | No |
| `LOCAL_QUORUM` | 2 (local DC) | No | Yes |
| `EACH_QUORUM` | 2 per DC | Yes | No |
| `ALL` | 6 (all DCs) | Yes | No |

!!! tip "Recommended for Multi-DC"
    `LOCAL_QUORUM` is recommended for most multi-datacenter deployments. It provides strong consistency within each datacenter while tolerating complete datacenter failure.

---

## Strong Consistency Formula

**Rule:** `R + W > RF` guarantees strong consistency (reads see latest writes).

| Write CL | Read CL | RF=3 | Strong? | Notes |
|----------|---------|------|---------|-------|
| `QUORUM` | `QUORUM` | 2+2=4 > 3 | Yes | Standard strong consistency |
| `ONE` | `ALL` | 1+3=4 > 3 | Yes | Write-heavy workloads |
| `ALL` | `ONE` | 3+1=4 > 3 | Yes | Read-heavy workloads |
| `LOCAL_QUORUM` | `LOCAL_QUORUM` | 2+2=4 > 3 | Yes | Per-datacenter strong consistency |
| `ONE` | `ONE` | 1+1=2 < 3 | No | Eventual consistency |
| `ONE` | `QUORUM` | 1+2=3 = 3 | No | Not strictly greater |

---

## Failure Tolerance

### Single Datacenter (RF=3)

| Nodes Down | `ONE` | `QUORUM` | `ALL` |
|------------|-------|----------|-------|
| 0 | ✅ | ✅ | ✅ |
| 1 | ✅ | ✅ | ❌ |
| 2 | ✅ | ❌ | ❌ |

### Multi-Datacenter (RF=3 per DC)

| Failure Scenario | `LOCAL_QUORUM` | `QUORUM` | `EACH_QUORUM` |
|------------------|----------------|----------|---------------|
| 1 node in local DC | ✅ | ✅ | ✅ |
| 2 nodes in local DC | ❌ | ✅* | ❌ |
| Entire remote DC down | ✅ | ❌ | ❌ |

*QUORUM may succeed if remote DC nodes compensate.

---

## Latency Comparison

| Level | Single DC | Multi-DC | Notes |
|-------|-----------|----------|-------|
| `ONE` | ~1-2ms | ~1-2ms | Fastest |
| `LOCAL_ONE` | ~1-2ms | ~1-2ms | Same as ONE for local |
| `QUORUM` | ~2-5ms | ~50-200ms | Cross-DC round trip in multi-DC |
| `LOCAL_QUORUM` | ~2-5ms | ~2-5ms | No cross-DC wait |
| `EACH_QUORUM` | N/A | ~50-200ms | Waits for slowest DC |
| `ALL` | ~3-10ms | ~50-200ms | Waits for slowest replica |

---

## Quick Decision Guide

| Requirement | Recommended Write CL | Recommended Read CL |
|-------------|---------------------|---------------------|
| Strong consistency, single DC | `QUORUM` | `QUORUM` |
| Strong consistency, multi-DC | `LOCAL_QUORUM` | `LOCAL_QUORUM` |
| Global strong consistency | `QUORUM` | `QUORUM` |
| Maximum throughput | `ONE` | `ONE` |
| Write-heavy, strong reads | `ONE` | `ALL` |
| Read-heavy, strong writes | `ALL` | `ONE` |
| Time-series / metrics | `LOCAL_ONE` | `LOCAL_ONE` |
| Compare-and-set (LWT) | N/A (use IF clause) | N/A |

---

## Related Documentation

- [Consistency (Concepts)](consistency.md) - How consistency works in detail
- [Replication](replication.md) - How replicas are placed
- [Lightweight Transactions](../../cql/dml/lightweight-transactions.md) - CQL syntax for LWT
- [Paxos](paxos.md) - Consensus algorithm for LWT
