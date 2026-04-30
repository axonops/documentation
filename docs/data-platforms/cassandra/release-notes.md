---
title: "Apache Cassandra Release Notes"
description: "Apache Cassandra release notes for 5.0.x, 4.1.x, and 4.0.x. Patch release highlights and major version features."
meta:
  - name: keywords
    content: "Cassandra release notes, Cassandra 5.0.8, Cassandra 4.1.11, Cassandra 4.0.20, Cassandra changelog, Cassandra patch releases"
---

# Apache Cassandra Release Notes

Highlights from current and recent Apache Cassandra releases. For complete patch-level changes, see the upstream `CHANGES.txt` files linked at the bottom of each version stream.

---

## 5.0.x

### Cassandra 5.0.8 (April 2026) - Current Release

- Backport Automated Repair Inside Cassandra for CEP-37 (CASSANDRA-21138)
- Update cassandra-stress to support TLS 1.3 by default by auto-negotiation (CASSANDRA-21007)
- Ensure schema created before 2.1 without tableId in folder name can be loaded in SnapshotLoader (CASSANDRA-21173)
- Harden data resurrection startup check with atomic heartbeat file write with fallback (CASSANDRA-21290) — backported from 4.1
- Improved observability in AutoRepair to report both expected vs. actual repair bytes and expected vs. actual keyspaces (CASSANDRA-20581) — backported from 6.0
- Stop repair scheduler if two major versions are detected (CASSANDRA-20048) — backported from 6.0
- AutoRepair: Safeguard Full repair against disk protection (CASSANDRA-20045) — backported from 6.0
- Stop AutoRepair monitoring thread upon Cassandra shutdown (CASSANDRA-20623) — backported from 6.0
- Fix race condition in auto-repair scheduler (CASSANDRA-20265) — backported from 6.0
- Implement minimum repair task duration setting for auto-repair scheduler (CASSANDRA-20160) — backported from 6.0
- Implement preview_repaired auto-repair type (CASSANDRA-20046) — backported from 6.0
- Automated Repair Inside Cassandra for CEP-37 (CASSANDRA-19918) — backported from 6.0

### Cassandra 5.0.7 (March 2026)

- Refactor SAI ANN query execution to use score ordered iterators for correctness and speed (CASSANDRA-20086)
- Fix ConcurrentModificationException in compaction garbagecollect (CASSANDRA-21065)
- Dynamically skip sharding L0 when SAI Vector index present (CASSANDRA-19661)
- Automatically disable zero-copy streaming for legacy sstables with old bloom filter format (CASSANDRA-21092)
- Correctly calculate default for FailureDetector max interval (CASSANDRA-21025)
- Rate limit password changes (CASSANDRA-21202)
- Obsolete expired SSTables before compaction starts (CASSANDRA-19776)
- Switch lz4-java to at.yawk.lz4 version due to CVE (CASSANDRA-21052)
- Fix memory leak in BufferPoolAllocator when capacity needs to be extended (CASSANDRA-20753)

For previous 5.0.x patch release details, see the [Apache Cassandra changelog](https://gitbox.apache.org/repos/asf?p=cassandra.git;a=blob_plain;f=CHANGES.txt;hb=cassandra-5.0).

### Cassandra 5.0.0 (September 2024) - Major Release

- **Storage-Attached Indexes (SAI)** (CEP-7) - Efficient secondary indexing (experimental in 4.0+, production-ready in 5.0)
- **Vector data type and search** (CEP-30) - Approximate nearest neighbor searching via SAI
- **Unified Compaction Strategy (UCS)** (CEP-26) - Adaptive compaction replacing multiple strategies
- **Trie memtables** (CEP-19) - Trie-based in-memory data structures
- **Trie SSTables** (CEP-25) - Trie-indexed SSTable format
- **Dynamic Data Masking** (CEP-20) - Selective redaction of sensitive data at query time
- **Java 17 support** - recommended for Cassandra 5.0
- **TTL and writetime on collections/UDTs** - Extended metadata for complex types
- **CIDR-based authorizer** (CEP-33) - Network-based access control
- **New math functions**: `abs`, `exp`, `log`, `log10`, `round`

---

## 4.1.x

### Cassandra 4.1.11 (March 2026) - Current 4.1 Release

- Disk usage guardrail cannot be disabled when failure threshold is reached (CASSANDRA-21057)
- ReadCommandController should close fast to avoid deadlock when building secondary index (CASSANDRA-19564)
- Redact security-sensitive information in system_views.settings (CASSANDRA-20856)
- Rate limit password changes (CASSANDRA-21202)
- Obsolete expired SSTables before compaction starts (CASSANDRA-19776)
- Switch lz4-java to at.yawk.lz4 version due to CVE (CASSANDRA-21052)
- Fix memory leak in BufferPoolAllocator when capacity needs to be extended (CASSANDRA-20753)
- Add option to disable cqlsh history (CASSANDRA-21180)

### Cassandra 4.1.0 (December 2022) - Major Release

- **Paxos v2** - Enhanced lightweight transaction protocol
- **Guardrails** - Operational safety boundaries and limits
- **Partition denylist** - Block access to problematic partitions
- **Top partition tracking** - Per-table monitoring of hot partitions
- **Native transport rate limiting** - Request throughput controls
- **Client-side password hashing** - Enhanced authentication security
- **Pluggable memtables** - Custom memtable implementations

For previous 4.1.x patch release details, see the [Apache Cassandra changelog](https://github.com/apache/cassandra/blob/cassandra-4.1.11/CHANGES.txt).

---

## 4.0.x

### Cassandra 4.0.20 (March 2026) - Current 4.0 Release

- Rate limit password changes (CASSANDRA-21202)
- Obsolete expired SSTables before compaction starts (CASSANDRA-19776)
- Switch lz4-java to at.yawk.lz4 version due to CVE (CASSANDRA-21052)
- Fix memory leak in BufferPoolAllocator when capacity needs to be extended (CASSANDRA-20753)
- Fix cleanup of old incremental repair sessions on token range changes or table deletion (CASSANDRA-20877)
- ArrayIndexOutOfBoundsException with repaired data tracking and counters (CASSANDRA-20871)
- Add option to disable cqlsh history (CASSANDRA-21180)
- Restrict BytesType compatibility to scalar types only (CASSANDRA-20982)

### Cassandra 4.0.0 (July 2021) - Major Release

- **Virtual tables** - System information via CQL queries
- **Audit logging** - Comprehensive query audit trail
- **Full query logging** - Capture all queries for replay
- **Incremental repair improvements** - More efficient anti-entropy
- **Zero-copy streaming** - Faster data transfer between nodes
- **Java 11 support** - Modern JVM compatibility

For previous 4.0.x patch release details, see the [Apache Cassandra changelog](https://github.com/apache/cassandra/blob/cassandra-4.0.20/CHANGES.txt).

---

## Version Compatibility

| Version | Release Date | End of Support | Status |
|---------|--------------|----------------|--------|
| 5.0.x | September 2024 | Until 5.3.0 release | **Current** |
| 4.1.x | December 2022 | Until 5.2.0 release | Supported |
| 4.0.x | July 2021 | Until 5.1.0 release | Supported |
| 3.11.x | June 2017 | Unmaintained | Legacy |

!!! warning "Upgrade Path"
    Direct upgrades skipping major versions are not supported. To upgrade from 3.11.x to 5.0.x:

    1. Upgrade 3.11.x → 4.0.x
    2. Upgrade 4.0.x → 4.1.x
    3. Upgrade 4.1.x → 5.0.x
