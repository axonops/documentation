---
description: "Cassandra repair scheduling. Automate repair with schedulers."
meta:
  - name: keywords
    content: "Cassandra repair scheduling, automated repair, repair scheduler"
---

# Repair Scheduling Guide

This page provides guidance on planning repair schedules to ensure completion within `gc_grace_seconds`, avoiding zombie data resurrection while minimizing operational impact.

## The gc_grace_seconds Constraint

### Understanding the Deadline

Every repair schedule must satisfy one fundamental requirement: **all nodes must complete repair within `gc_grace_seconds`**.

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title gc_grace_seconds Timeline

rectangle "Safe Zone (Day 1-7)" as safe #90EE90 {
    label "Repair should\ncomplete here" as safeL
}

rectangle "Warning Zone (Day 8-9)" as warn #FFB6C1 {
    label "Risk increasing" as warnL
}

rectangle "Danger Zone (Day 10+)" as danger #FF6347 {
    label "Tombstones\nGC eligible" as dangerL
}

safe --> warn
warn --> danger

note bottom of danger
  Default gc_grace_seconds = 10 days (864000 seconds)
  After this, tombstones can be garbage collected
end note
@enduml
```

### Why This Matters

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Zombie Data Resurrection Scenario

participant "Node A" as A
participant "Node B" as B
participant "Node C\n(DOWN)" as C

== T=0: DELETE row X ==
A -> A : Create tombstone
A -> B : Replicate tombstone
A ->x C : Node C is down

== T=10 days: gc_grace_seconds expires ==
A -> A : GC tombstone
B -> B : GC tombstone

== Node C recovers ==
C -> C : Still has row X\n(no tombstone)

note over A,C #FFAAAA
  ZOMBIE DATA!
  Row X was deleted but
  now exists again on Node C
end note
@enduml
```

**Prevention:** Complete repair on all nodes before `gc_grace_seconds` expires. This propagates tombstones to all replicas before they're garbage collected.

---

## Calculating Repair Schedules

### Variables

| Variable | Description | Example |
|----------|-------------|---------|
| N | Number of nodes | 12 |
| T | Time to repair one node | 4 hours |
| RF | Replication factor | 3 |
| G | gc_grace_seconds | 864000 (10 days) |
| B | Desired buffer time | 2 days |

### Sequential Repair Formula

```
Total repair cycle = N × T
Available time = G - B

Constraint: N × T ≤ G - B

Example:
- 12 nodes × 4 hours = 48 hours
- gc_grace = 10 days - 2 day buffer = 8 days available
- 48 hours << 8 days ✓ (plenty of margin)
```

### Parallel Repair Formula

```
Total repair cycle = (N ÷ RF) × T

Example:
- 12 nodes ÷ 3 RF = 4 rounds
- 4 rounds × 4 hours = 16 hours
- 4x faster than sequential
```

### Large Cluster Calculation

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Repair Timeline for 100-Node Cluster

rectangle "gc_grace_seconds: 10 days" as total {
    rectangle "Buffer: 2 days" as buffer #FFB6C1
    rectangle "Available: 8 days" as available #90EE90
}

note bottom of total
  100 nodes ÷ 8 days = 12.5 nodes/day required

  With 4 hours per node:
  - Sequential: 12.5 × 4 = 50 hours/day (IMPOSSIBLE)
  - Parallel (RF=3): 12.5 × 4 ÷ 3 = 16.7 hours/day
  - With 6 parallel groups: ~8 hours/day (FEASIBLE)
end note
@enduml
```

---

## Schedule Planning

### Step 1: Measure Repair Duration

Before planning a schedule, measure the actual repair duration on a representative node:

```bash
nodetool repair -pr my_keyspace
```

Record the duration from start to completion. This varies significantly based on data volume, disk speed, and network bandwidth.

### Step 2: Calculate Total Cycle Time

| Strategy | Formula | Example (12 nodes, 4 hrs/node, RF=3) |
|----------|---------|--------------------------------------|
| Sequential | Nodes × Time per node | 12 × 4 = 48 hours |
| Parallel | (Nodes ÷ RF) × Time per node | (12 ÷ 3) × 4 = 16 hours |

Ensure the total cycle time plus a 2-day buffer fits within `gc_grace_seconds`.

### Step 3: Choose Schedule

**Recommended schedules by cluster size:**

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Recommended Schedules by Cluster Size

rectangle "Small Cluster (3-6 nodes)" as small {
    label "Strategy: Sequential\nFrequency: Weekly\nDay: Sunday 02:00\nDuration: < 24 hours" as smallL
}

rectangle "Medium Cluster (6-20 nodes)" as medium {
    label "Strategy: Parallel or Sequential\nFrequency: Every 3-5 days\nDays: Rotate through week\nDuration: 24-48 hours" as mediumL
}

rectangle "Large Cluster (20-50 nodes)" as large {
    label "Strategy: Parallel with segments\nFrequency: Every 2-3 days\nDays: Continuous rotation\nDuration: 48-72 hours" as largeL
}

rectangle "Very Large Cluster (50+ nodes)" as vlarge {
    label "Strategy: Continuous\nFrequency: Always running\nDays: 24/7 operation\nTool: AxonOps or Reaper" as vlargeL
}
@enduml
```

---

## Adjusting gc_grace_seconds

### When to Consider Adjusting

| Scenario | Recommended gc_grace_seconds |
|----------|------------------------------|
| Very large cluster, slow repairs | Increase (14-21 days) |
| Fast SSDs, quick repairs | Keep default (10 days) |
| High delete rate, storage concerns | Decrease (7 days) with faster repairs |
| Frequently offline nodes | Increase significantly |

### How to Change gc_grace_seconds

```sql
-- Check current value
SELECT gc_grace_seconds FROM system_schema.tables
WHERE keyspace_name = 'my_keyspace' AND table_name = 'my_table';

-- Modify per table
ALTER TABLE my_keyspace.my_table
WITH gc_grace_seconds = 1209600;  -- 14 days

-- Verify change
DESCRIBE TABLE my_keyspace.my_table;
```

**Warning:** Reducing `gc_grace_seconds` requires faster repair cycles. Ensure repair can complete within the new window before making changes.

---

## Scheduling Best Practices

### Off-Peak Timing

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Traffic Pattern and Repair Windows

rectangle "Low Traffic (22:00-06:00)" as low #90EE90 {
    label "Ideal repair window" as lowL
}

rectangle "Medium Traffic (06:00-09:00, 18:00-22:00)" as med #FFB6C1 {
    label "Avoid if possible" as medL
}

rectangle "High Traffic (09:00-18:00)" as high #FF6347 {
    label "Do not run repairs" as highL
}

low --> med
med --> high
high --> med
med --> low
@enduml
```

### Staggered Node Schedules

For manual scheduling, stagger repairs across the week so only one node repairs at a time:

| Node | Day | Time (UTC) |
|------|-----|------------|
| Node 1 | Sunday | 02:00 |
| Node 2 | Monday | 02:00 |
| Node 3 | Tuesday | 02:00 |
| Node 4 | Wednesday | 02:00 |
| Node 5 | Thursday | 02:00 |
| Node 6 | Friday | 02:00 |

Use cron or systemd timers to automate execution. For clusters larger than 6 nodes, or where manual scheduling becomes error-prone, consider using AxonOps to automate repair scheduling with adaptive timing and failure handling.

### Avoiding Conflicts

Operations that should NOT run concurrently with repair:

| Operation | Reason |
|-----------|--------|
| Major compaction | Competes for disk I/O |
| Backup | Network and disk contention |
| Schema changes | Can interfere with repair validation |
| Node addition/removal | Topology changes invalidate ranges |
| Bulk loading | High write load |

---

## Monitoring Schedule Compliance

### Tracking Repair History

Monitor repair completion using:

| Method | Command/Source |
|--------|----------------|
| System logs | Search for "Repair completed" in `system.log` |
| Metrics | `percent_repaired` metric per table |
| nodetool | `nodetool tablestats my_keyspace` shows percent repaired |

### Alerting on Missed Repairs

Configure alerts based on time since last successful repair:

| Threshold | Condition | Action |
|-----------|-----------|--------|
| Warning | > 70% of `gc_grace_seconds` | Investigate, schedule makeup repair |
| Critical | > 90% of `gc_grace_seconds` | Immediate action required |

AxonOps provides built-in repair compliance tracking with dashboards showing repair status across all nodes and automatic alerting when repairs fall behind schedule.

---

## Handling Schedule Disruptions

### Repair Failure Recovery

```plantuml
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontName Arial

title Repair Failure Recovery

start

:Repair fails on node X;

if (Time to gc_grace < 2 days?) then (yes)
  #FF6347:CRITICAL - Immediate action;
  :Investigate and fix root cause;
  :Retry repair immediately;
  if (Retry succeeds?) then (yes)
    :Resume normal schedule;
  else (no)
    :Escalate - manual intervention;
    :Consider full repair (-full);
  endif
else (no)
  :Investigate failure cause;
  if (Transient issue?) then (yes)
    :Wait for next scheduled slot;
    :Monitor closely;
  else (no)
    :Fix underlying issue;
    :Schedule makeup repair;
  endif
endif

stop
@enduml
```

### Maintenance Window Changes

When normal repair windows are unavailable:

1. **Calculate remaining time:** Determine days until `gc_grace_seconds` deadline
2. **Identify alternative windows:** Find off-peak periods even if non-standard
3. **Adjust parallelism:** Use parallel strategy to compress timeline
4. **Communicate:** Notify team of temporary schedule change
5. **Resume normal:** Return to standard schedule once resolved

---

## Automated Repair with AxonOps

Manual repair scheduling becomes increasingly difficult as clusters grow. AxonOps offers two approaches to automated repair:

### Scheduled Repair

Configure repair to run at specific times with:

- Automatic distribution across nodes
- Configurable parallelism and throttling
- Failure detection and retry
- Compliance tracking against `gc_grace_seconds`

### Adaptive Repair

Continuously monitors cluster state and adjusts repair execution based on:

- Current cluster load and latency
- Time remaining until `gc_grace_seconds` deadline
- Node health and availability
- Repair progress across the cluster

Adaptive repair automatically throttles during high-traffic periods and accelerates when the cluster is idle, ensuring repairs complete on time without impacting production workloads.

### Benefits Over Manual Scheduling

| Aspect | Manual | AxonOps |
|--------|--------|---------|
| Schedule calculation | Manual spreadsheets | Automatic |
| Failure handling | Manual intervention | Auto-retry |
| Load awareness | Fixed schedules | Dynamic throttling |
| Compliance tracking | Log parsing | Built-in dashboards |
| Multi-cluster | Per-cluster setup | Centralized management |

---

## Quick Reference

### Minimum Repair Frequency by Cluster Size

| Nodes | RF=3 Sequential | RF=3 Parallel | Recommendation |
|-------|-----------------|---------------|----------------|
| 3 | 1x per week | 1x per week | Weekly |
| 6 | 1x per week | 1x per week | Weekly |
| 12 | 2x per week | 1x per week | Every 3-4 days |
| 24 | 3x per week | 2x per week | Every 2-3 days |
| 50 | Daily | 3x per week | Every 2 days |
| 100+ | Continuous | Daily | Continuous |

### Checklist Before Changing Schedule

- [ ] Current repair duration measured per node
- [ ] Total cycle time calculated
- [ ] Buffer time included (minimum 2 days)
- [ ] Off-peak windows identified
- [ ] Conflict operations scheduled around repair
- [ ] Alerting configured for missed repairs
- [ ] Runbook updated with new schedule

## Next Steps

- **[Repair Concepts](concepts.md)** - Understanding repair fundamentals
- **[Options Reference](options-reference.md)** - Command options explained
- **[Repair Strategies](strategies.md)** - Implementation approaches
