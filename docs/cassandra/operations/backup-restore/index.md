---
description: "Cassandra backup and restore overview. Strategies and tools for data protection."
meta:
  - name: keywords
    content: "Cassandra backup restore, data protection, backup strategies"
---

# Backup and Restore Overview

## Why Backups Are Necessary

A common misconception persists in distributed database operations: "Cassandra replicates data across nodes, so backups are unnecessary." This reasoning conflates two fundamentally different concepts—high availability and data protection.

Replication provides **high availability**: if one node fails, other replicas serve requests without interruption. However, replication faithfully propagates *all* changes to all replicas, including destructive ones. When an application bug deletes data, that deletion replicates. When an operator runs `DROP TABLE`, the table disappears from all nodes simultaneously. Replication ensures consistency—it ensures all replicas reflect the same state, whether that state is correct or catastrophically wrong.

Backups provide **data protection**: the ability to recover to a known good state after data loss, corruption, or disaster. Backups exist outside the replication system, immune to changes propagating through the cluster.

---

## Disaster Scenarios

Understanding the range of potential disasters helps define appropriate backup strategies. Disasters fall into three broad categories: infrastructure failures, human errors, and external threats.

### Infrastructure Failures

**Single Node Failure**

The most common failure mode. Causes include:

- Disk failure (SSDs have finite write endurance; HDDs have mechanical failures)
- Memory errors (ECC can correct some; others cause crashes)
- Power supply failure
- Motherboard or CPU failure
- Operating system corruption
- Network interface failure (node appears down to cluster)

With RF=3, single node failures are non-events for availability—other replicas serve requests. However, the failed node's data must be rebuilt, either from backup or by streaming from other replicas.

**Rack Failure**

Multiple nodes fail simultaneously due to shared infrastructure:

- Top-of-rack switch failure (all nodes in rack lose network)
- PDU (Power Distribution Unit) failure (all nodes lose power)
- Cooling failure in rack zone (thermal shutdown)
- Shared storage failure (if using SAN/NAS)
- Cable tray damage (fire, water, physical impact)

Rack-aware replication (`NetworkTopologyStrategy` with rack configuration) ensures replicas span racks. A rack failure should not cause data unavailability, but rebuilding an entire rack strains cluster resources.

**Datacenter Failure**

Complete loss of a datacenter:

- Power grid failure affecting the facility
- Network connectivity loss (upstream provider failure, fiber cut)
- Natural disasters (earthquake, flood, hurricane, fire)
- Cooling system failure (facility-wide thermal event)
- Building access restrictions (civil unrest, pandemic, legal action)

Multi-datacenter deployments with `NetworkTopologyStrategy` survive DC failures. Single-DC deployments face complete outage until the datacenter recovers or data is restored elsewhere.

**Region Failure**

Geographic-scale events affecting multiple datacenters:

- Regional power grid failure
- Major natural disaster (earthquake affecting multiple facilities)
- Regional network backbone failure
- Political or regulatory action affecting a jurisdiction

Multi-region deployments provide protection, but most organizations run Cassandra within a single region for latency reasons.

### Human Errors

Human error causes more data loss incidents than hardware failures. Unlike hardware failures, human errors typically affect all replicas simultaneously—replication provides no protection.

**Accidental Data Deletion**

```sql
-- Intended: Delete inactive users from staging
DELETE FROM staging.users WHERE active = false;

-- Actual: Connected to production
DELETE FROM production.users WHERE active = false;
```

The deletion replicates to all nodes. By the time the error is discovered, all replicas consistently reflect the data loss.

**Accidental Schema Changes**

```sql
-- Intended: Drop unused table in development
DROP TABLE dev_keyspace.temp_analytics;

-- Actual: Dropped production table
DROP TABLE prod_keyspace.analytics;
```

Schema changes are immediate and cluster-wide. The `auto_snapshot` feature (enabled by default) creates a snapshot before DROP operations, providing a recovery path—but only if the operator knows it exists and acts before the snapshot is cleared.

**Destructive Maintenance Operations**

```bash
# Intended: Clean up old snapshots on staging node
nodetool clearsnapshot -t old_backup

# Actual: Ran on production, cleared critical backup
```

```bash
# Intended: Remove test keyspace data
rm -rf /var/lib/cassandra/data/test_keyspace

# Actual: Typo removed production data
rm -rf /var/lib/cassandra/data/prod_keyspace
```

**Application Bugs**

- Code deploying to production with incorrect DELETE or UPDATE logic
- Migration scripts with bugs affecting production data
- Race conditions causing data corruption
- Serialization bugs writing malformed data

Application-level corruption is particularly insidious: the bad data replicates normally, and the problem may not be detected until significant damage has occurred.

**Configuration Errors**

- Incorrect `gc_grace_seconds` causing premature tombstone removal
- Wrong replication factor leaving data under-replicated
- Misconfigured compaction causing data loss during cleanup
- Authentication changes locking out all users

### External Threats

**Ransomware and Malware**

Malicious software encrypting or deleting database files. Ransomware specifically targets backup systems to prevent recovery, making off-site, air-gapped backups essential.

**Security Breaches**

Attackers with database access may:

- Delete data to cover tracks
- Corrupt data as sabotage
- Exfiltrate and then delete data
- Modify data for fraud

**Insider Threats**

Malicious actions by employees or contractors with legitimate access:

- Deliberate data destruction (disgruntled employee)
- Data theft followed by deletion
- Sabotage during organizational disputes

---

## Backup and Recovery Theory

Enterprise backup strategies are defined by measurable objectives that align technical capabilities with business requirements.

### Recovery Point Objective (RPO)

**RPO defines the maximum acceptable data loss, measured in time.**

If RPO is 4 hours, the organization accepts losing up to 4 hours of data in a disaster. This drives backup frequency:

| RPO Target | Backup Strategy Required |
|------------|--------------------------|
| 24 hours | Daily snapshots |
| 4 hours | Snapshots every 4 hours, or continuous incremental |
| 1 hour | Hourly snapshots or incremental backup |
| 15 minutes | Continuous incremental with frequent sync |
| Near-zero | Commit log archiving (PITR capability) |
| Zero | Synchronous replication to secondary site |

**Determining RPO:**

Business stakeholders must answer: "If we lose the last N hours of data, what is the business impact?"

Considerations include:
- Transaction value (financial systems may require near-zero RPO)
- Data recreation cost (can lost data be re-entered or regenerated?)
- Regulatory requirements (some industries mandate specific retention)
- Customer impact (SLA commitments, reputation damage)

### Recovery Time Objective (RTO)

**RTO defines the maximum acceptable downtime, measured in time.**

If RTO is 2 hours, the system must be operational within 2 hours of a disaster declaration. This drives recovery infrastructure:

| RTO Target | Infrastructure Required |
|------------|------------------------|
| Days | Off-site tape storage, manual recovery |
| Hours | Remote disk backup, documented procedures |
| 1 hour | Hot standby or rapid restore capability |
| Minutes | Active-active multi-DC, automated failover |
| Seconds | Synchronous replication, instant failover |

**Factors affecting actual recovery time:**

| Factor | Impact on Recovery Time |
|--------|------------------------|
| Backup location | Remote storage adds transfer time |
| Data volume | 10TB takes longer to restore than 100GB |
| Network bandwidth | Limits data transfer rate |
| Restore method | `sstableloader` slower than direct file copy |
| Cluster size | More nodes = more work, but parallelizable |
| Staff availability | Off-hours incidents take longer |
| Documentation quality | Poor runbooks slow recovery |
| Testing frequency | Untested procedures fail under pressure |

**The RTO/RPO Trade-off:**

Shorter RTO and RPO require greater investment in infrastructure, tooling, and operational processes. Organizations must balance protection level against cost:

```
                        Cost
                          ↑
                          │                    ╱
                          │                  ╱
                          │                ╱
                          │              ╱
                          │            ╱
                          │          ╱
                          │        ╱
                          │      ╱
                          │    ╱
                          │  ╱
                          │╱
                          └─────────────────────→ RPO/RTO (shorter)

Approaching zero RPO/RTO requires exponentially increasing investment.
```

### Operational Acceptance Testing (OAT)

**A backup that has never been tested is not a backup.**

OAT validates that backup and recovery procedures work as designed, under realistic conditions, and within required time constraints.

**OAT Components for Backup/Restore:**

| Test Type | Description | Frequency |
|-----------|-------------|-----------|
| Backup verification | Confirm backups complete successfully | Daily (automated) |
| Integrity check | Validate backup files are not corrupted | Weekly (automated) |
| Partial restore | Restore single table to staging | Monthly |
| Full restore | Restore entire cluster to DR site | Quarterly |
| Disaster simulation | Unannounced DR exercise with time measurement | Annually |

**What OAT Should Validate:**

1. **Backup completeness**: All required data is captured
2. **Backup integrity**: Files are not corrupted and can be read
3. **Restore procedure**: Documented steps actually work
4. **Recovery time**: Actual time meets RTO requirement
5. **Data correctness**: Restored data matches expected state
6. **Application functionality**: Applications work with restored data
7. **Staff capability**: Team can execute procedures under pressure

**Common OAT Failures:**

| Failure Mode | Cause | Prevention |
|--------------|-------|------------|
| Backup files corrupted | Storage failure, incomplete transfer | Checksums, verification |
| Restore procedure fails | Undocumented dependencies, environment changes | Regular testing |
| RTO exceeded | Underestimated data volume, slow network | Realistic testing |
| Wrong data restored | Incorrect backup selected, timestamp confusion | Clear naming, automation |
| Missing schema | Schema not included in backup | Include schema in every backup |
| Application incompatibility | Schema drift, version mismatch | End-to-end testing |

### Business Continuity Planning

Backup and restore is one component of broader business continuity:

| Component | Purpose |
|-----------|---------|
| Backup & Restore | Recover data after loss |
| Disaster Recovery (DR) | Recover systems after site failure |
| High Availability (HA) | Prevent outages through redundancy |
| Business Continuity (BC) | Maintain business operations during disruption |

These components complement each other:

```
                    ┌─────────────────────────────────────┐
                    │       Business Continuity           │
                    │  ┌───────────────────────────────┐  │
                    │  │      Disaster Recovery        │  │
                    │  │  ┌─────────────────────────┐  │  │
                    │  │  │   High Availability     │  │  │
                    │  │  │  ┌───────────────────┐  │  │  │
                    │  │  │  │  Backup/Restore   │  │  │  │
                    │  │  │  └───────────────────┘  │  │  │
                    │  │  └─────────────────────────┘  │  │
                    │  └───────────────────────────────┘  │
                    └─────────────────────────────────────┘
```

---

## Replication vs Backup

Understanding what replication does and does not protect against:

| Failure Type | Replication Protects? | Backups Protect? |
|--------------|----------------------|------------------|
| Single node failure | Yes | Yes |
| Multiple node failures (within RF) | Yes | Yes |
| Simultaneous failures exceeding RF | No | Yes |
| Rack failure (with rack-aware placement) | Yes | Yes |
| Datacenter failure (with multi-DC) | Yes | Yes |
| `DROP TABLE` or `DROP KEYSPACE` | No | Yes |
| `TRUNCATE` command | No | Yes |
| Accidental DELETE statements | No | Yes |
| Application bug corrupting data | No | Yes |
| Malicious insider deleting data | No | Yes |
| Ransomware encryption | No | Yes (if offline) |
| Regulatory data retention | No | Yes |
| Point-in-time audit requirements | No | Yes |

### The gc_grace_seconds Constraint

Even with backups, restoration has a time limit determined by `gc_grace_seconds` (default: 10 days).

Cassandra uses tombstones (deletion markers) rather than immediately removing data. Tombstones propagate to all replicas, ensuring deletions are consistent. After `gc_grace_seconds`, tombstones are eligible for removal during compaction.

**The resurrection problem:**

```
Timeline:
Day 0:  Full backup taken (contains Row X)
Day 3:  Row X deleted (tombstone created)
Day 11: Tombstone expires, removed by compaction
Day 15: Restore Day 0 backup to one node

State after restore:
- Restored node: Has Row X (from backup)
- Other nodes: No Row X, no tombstone (tombstone was removed)

Result:
- Anti-entropy repair sees Row X on restored node
- No tombstone exists to indicate deletion
- Row X replicates back to other nodes
- Deleted data "resurrects"
```

**Implications:**

| Backup Age | Restore Scope | Safe? |
|------------|---------------|-------|
| < gc_grace_seconds | Single node | Yes |
| < gc_grace_seconds | Full cluster | Yes |
| > gc_grace_seconds | Single node | No (resurrection risk) |
| > gc_grace_seconds | Full cluster | Yes (all nodes same state) |

---

## Backup Components

A complete Cassandra backup includes:

| Component | Description | Required | Notes |
|-----------|-------------|----------|-------|
| SSTables | Immutable data files | Yes | The actual data |
| Schema | Keyspace and table definitions | Yes | Must restore before data |
| Commit logs | Write-ahead log | For PITR | Enables point-in-time recovery |
| Configuration | cassandra.yaml, JVM settings | Recommended | Cluster settings, tuning |
| Topology | Token assignments, DC/rack layout | Recommended | For disaster recovery |

### SSTables

SSTables are immutable—once written, they never change. This immutability makes them ideal for backup:

- No risk of partial writes or mid-file corruption during backup
- Can be safely copied while Cassandra is running (after flush)
- Hard links enable instant, zero-space local snapshots

### Schema

The schema must be restored before data. Without table definitions, SSTables cannot be loaded.

```bash
# Export complete schema
cqlsh -e "DESC SCHEMA" > schema.cql

# Include with every backup
```

### Commit Logs

Commit logs enable point-in-time recovery (PITR). Combined with a base snapshot, archived commit logs can restore to any point in time:

```
|───────|─────────────────────────|───────|
     Snapshot                         Failure
             <─── Commit logs ───>

Recovery = Restore snapshot + replay commit logs to target time
```

---

## Backup Methods Summary

| Method | Type | RPO | Complexity | Use Case |
|--------|------|-----|------------|----------|
| Snapshots | Full point-in-time | Hours-days | Low | Primary backup method |
| Incremental | Changed SSTables | Hours | Medium | Reduce storage between snapshots |
| Commit log archiving | Continuous | Minutes | High | Point-in-time recovery |

See **[Backup Procedures](backup.md)** for implementation details.

---

## Restore Scenarios Summary

| Scenario | Complexity | Typical Approach |
|----------|------------|------------------|
| Single table, single node | Low | Copy files + `nodetool refresh` |
| Single node failure | Medium | Rebuild from replicas or restore + repair |
| Rack failure | Medium | Restore nodes + repair |
| Datacenter failure | High | Restore all DC nodes + cross-DC repair |
| Point-in-time recovery | High | Snapshot + commit log replay |
| Migration to new cluster | Medium | `sstableloader` |

See **[Restore Procedures](restore.md)** for detailed procedures.

---

## Managed Backup with AxonOps

Implementing enterprise-grade backup and restore requires significant operational investment:

- Scheduling and orchestration across all nodes
- Off-site storage with appropriate retention
- Monitoring and alerting for backup failures
- Regular restore testing and validation
- Documentation and runbook maintenance

AxonOps provides a fully managed backup solution:

- **Automated scheduling** with configurable retention policies
- **Remote storage integration** (S3, GCS, Azure Blob)
- **Point-in-time recovery** with commit log archiving
- **Backup monitoring and alerting**
- **One-click restore** through the dashboard
- **Compliance reporting** for audit requirements

See **[AxonOps Backup](/operations/backup/)** for configuration and usage.

---

## Next Steps

- **[Backup Procedures](backup.md)** - Snapshots, incremental backups, commit log archiving
- **[Restore Guide](restore.md)** - Failure scenarios and recovery approaches
