---
title: "Cassandra SSTable Compression"
description: "SSTable compression in Apache Cassandra. Chunk-based architecture, algorithm comparison (LZ4, Zstd, Snappy, Deflate), configuration, chunk size tuning, and operational guidance."
meta:
  - name: keywords
    content: "Cassandra compression, SSTable compression, LZ4, Zstd, Snappy, Deflate, chunk_length_in_kb, compression ratio"
---

# SSTable Compression

Cassandra compresses SSTable data at the file level using a chunk-based scheme. Each SSTable's data file is divided into fixed-size blocks, each compressed independently. This reduces disk I/O and storage consumption at the cost of CPU cycles during reads (decompression) and writes (compression).

Compression is enabled by default on all tables using `LZ4Compressor`.

!!! info "SSTable Compression vs Protocol Compression"
    This page covers **SSTable compression**—compression of data at rest on disk. For compression of CQL protocol frames in transit between clients and nodes, see [Protocol Compression](../client-connections/compression.md).

---

## How SSTable Compression Works

### Chunk-Based Architecture

SSTable data is divided into fixed-size uncompressed chunks (controlled by `chunk_length_in_kb`, default 16 KB in Cassandra 4.0+). Each chunk is compressed independently and followed by a 4-byte Adler32 checksum.

```
Uncompressed data:   [Chunk 0: 16 KB][Chunk 1: 16 KB][Chunk 2: 16 KB][Chunk 3: 16 KB]
                          ↓                ↓                ↓                ↓
Compressed on disk:  [~6 KB + CRC]   [~7 KB + CRC]   [~5 KB + CRC]   [~8 KB + CRC]
```

The `CompressionInfo.db` component file stores the byte offset of each compressed chunk within the `Data.db` file. This offset table enables random access: to read data at a given uncompressed position, Cassandra calculates the chunk number and looks up its compressed offset. For details on the CompressionInfo.db file format, see [SSTable Components](sstables.md#compression-info-compressioninfodb).

Independent chunk compression means:

- Any single chunk can be decompressed without reading or decompressing adjacent chunks
- Writes append compressed chunks sequentially—there is no need to rewrite the entire file
- Corruption in one chunk does not affect decompression of other chunks

### Read Path Behavior

When a read request requires data from a compressed SSTable:

1. The coordinator identifies the relevant SSTable and the row's position within the uncompressed data
2. The chunk number is calculated: `chunk_number = position / chunk_length`
3. The compressed chunk offset is looked up in the CompressionInfo.db offset table
4. The **entire chunk** is read from disk and decompressed—partial chunk decompression is not possible
5. The CRC checksum is verified with probability equal to `crc_check_chance`
6. The requested row is extracted from the decompressed chunk

This creates **read amplification**: even if only a single row (e.g., 200 bytes) is needed, the full chunk (e.g., 16 KB uncompressed) must be read and decompressed. Chunk size tuning directly controls this tradeoff. See [Chunk Size Tuning](#chunk-size-tuning).

For the full read path, see [Read Path](read-path.md).

### Write Path Behavior

Compression is applied when SSTables are written during memtable flushes and compaction. Key behavioral properties:

- Changing compression settings via `ALTER TABLE` affects only **newly written** SSTables. Existing SSTables retain their original compression until rewritten by compaction or explicit upgrade.
- To force recompression of existing SSTables, use [`nodetool upgradesstables`](../../operations/nodetool/upgradesstables.md) or [`nodetool recompress_sstables`](../../operations/nodetool/recompress_sstables.md).
- The `flush_compression` setting in `cassandra.yaml` (Cassandra 4.1+, CASSANDRA-15379) controls whether flushed SSTables use a fast compressor or the table-configured compressor. This allows faster flushes at the cost of temporarily lower compression ratios, with compaction applying the table's configured compressor later.

### Memory Overhead

Compression metadata (the chunk offset table) is stored **off-heap**, outside the Java heap. This is important for capacity planning:

| chunk_length_in_kb | Chunks per GB (uncompressed) | Relative Metadata Overhead |
|:------------------:|:----------------------------:|:--------------------------:|
| 4                  | ~262,144                     | 16x                        |
| 8                  | ~131,072                     | 8x                         |
| 16                 | ~65,536                      | 4x                         |
| 32                 | ~32,768                      | 2x                         |
| 64                 | ~16,384                      | 1x (baseline)              |
| 128                | ~8,192                       | 0.5x                       |
| 256                | ~4,096                       | 0.25x                      |

As a rough estimate, compression metadata consumes approximately 1–3 GB of off-heap memory per TB of on-disk data, depending on chunk size and compression ratio. Monitor this with `nodetool tablestats` (the `Compression metadata off heap memory used` field).

---

## Compression Algorithms

### Algorithm Comparison

| Compressor | Available Since | Compression Speed | Decompression Speed | Typical Ratio | CPU Cost | Primary Use Case |
|------------|:--------------:|:-----------------:|:-------------------:|:------------:|:--------:|------------------|
| LZ4Compressor | 1.2.2 (default since 2.0) | Fastest | Fastest | ~2–2.5x | Lowest | General purpose, latency-sensitive workloads |
| SnappyCompressor | 1.0 | Fast | Fast | ~2–2.5x | Low | Legacy; LZ4 generally preferred |
| ZstdCompressor | 4.0 | Medium | Fast | ~3–4x | Medium | Storage-constrained deployments |
| DeflateCompressor | 1.0 | Slow | Medium | ~3–4x | High | Archival or cold data |
| NoopCompressor | 4.0 | N/A | N/A | 1x | None | Pre-compressed or high-entropy data |

### LZ4Compressor

LZ4 is the default compressor for all tables since Cassandra 2.0. It provides the fastest compression and decompression among all available algorithms, with moderate compression ratios.

**Fast mode** (default): Optimized for speed with a fixed compression acceleration.

**High-compression mode** (Cassandra 3.6+, CASSANDRA-11051): Achieves better compression ratios at the cost of slower compression. Decompression speed is unaffected.

```sql
-- LZ4 fast mode (default)
CREATE TABLE sensor_data (...) WITH compression = {
    'class': 'LZ4Compressor'
};

-- LZ4 high-compression mode
ALTER TABLE archival_data WITH compression = {
    'class': 'LZ4Compressor',
    'lz4_compressor_type': 'high',
    'lz4_high_compressor_level': 12
};
```

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `lz4_compressor_type` | `fast`, `high` | `fast` | Selects fast or high-compression mode |
| `lz4_high_compressor_level` | 1–17 | 9 | Compression level for high mode. Higher values produce better ratios with slower compression |

### SnappyCompressor

Snappy was the default compressor before Cassandra 2.0. It offers similar performance characteristics to LZ4 but is retained primarily for backward compatibility. For new deployments, LZ4 is preferred as it generally provides equal or better performance across both compression and decompression.

```sql
ALTER TABLE my_table WITH compression = {
    'class': 'SnappyCompressor'
};
```

### ZstdCompressor

Zstandard (Zstd) was added in Cassandra 4.0 (CASSANDRA-14482). It achieves significantly better compression ratios than LZ4—typically 30–50% smaller compressed output on structured data—while maintaining competitive decompression speeds.

```sql
ALTER TABLE large_table WITH compression = {
    'class': 'ZstdCompressor',
    'compression_level': 3
};
```

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `compression_level` | -131072 to 22 | 3 | Higher values improve compression ratio at the cost of compression speed. Negative values enable fast mode with progressively less compression |

!!! info "Zstd and Storage Savings"
    On workloads with structured or repetitive data (JSON, log entries, wide rows with similar columns), Zstd at its default level can reduce SSTable size by 30–50% compared to LZ4, with minimal impact on read latency since decompression speed remains fast.

### DeflateCompressor

Deflate provides the highest compression ratios among the standard compressors but at significantly higher CPU cost for both compression and decompression. It is suitable for cold or archival data where storage savings outweigh latency concerns.

```sql
ALTER TABLE cold_data WITH compression = {
    'class': 'DeflateCompressor'
};
```

### Disabling Compression

Compression can be disabled entirely or replaced with `NoopCompressor`:

```sql
-- Disable compression
ALTER TABLE my_table WITH compression = {'enabled': 'false'};

-- NoopCompressor (4.0+): maintains metadata structure without compressing
ALTER TABLE my_table WITH compression = {'class': 'NoopCompressor'};
```

Disabling compression is appropriate when:

- Data is already in a compressed format (JPEG, PNG, video, compressed archives)
- Data has high entropy (encrypted data, random byte sequences)
- The workload requires absolute minimum read latency and sufficient disk capacity exists
- Off-heap memory is severely constrained and the dataset is large

---

## Configuration

### CQL Compression Parameters

Compression is configured per table using the `WITH compression` clause in `CREATE TABLE` or `ALTER TABLE`:

```sql
CREATE TABLE my_keyspace.my_table (
    id uuid PRIMARY KEY,
    data text
) WITH compression = {
    'class': 'ZstdCompressor',
    'chunk_length_in_kb': 16,
    'crc_check_chance': 1.0,
    'compression_level': 3
};
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `class` | string | `LZ4Compressor` | Fully qualified or short class name of the compressor |
| `chunk_length_in_kb` | integer | 16 (4.0+), 64 (pre-4.0) | Uncompressed chunk size in KB. Must be a power of 2, minimum 4 |
| `crc_check_chance` | float | 1.0 | Probability (0.0–1.0) of verifying the CRC checksum on each chunk read |
| `enabled` | boolean | `true` | Set to `false` to disable compression entirely |
| `compression_level` | integer | 3 (Zstd) | Compressor-specific compression level (ZstdCompressor only) |
| `lz4_compressor_type` | string | `fast` | LZ4 mode: `fast` or `high` (LZ4Compressor only, 3.6+) |
| `lz4_high_compressor_level` | integer | 9 | LZ4 high-compression level, 1–17 (LZ4Compressor only, 3.6+) |

To view a table's current compression settings:

```sql
SELECT compression FROM system_schema.tables
WHERE keyspace_name = 'my_keyspace' AND table_name = 'my_table';
```

### Applying Changes to Existing SSTables

Changing compression via `ALTER TABLE` only affects SSTables written after the change. To rewrite existing SSTables with the new settings:

```bash
# Rewrite all SSTables for a table (triggers recompression)
nodetool upgradesstables my_keyspace my_table

# Recompress without full SSTable rewrite (4.0+)
nodetool recompress_sstables my_keyspace my_table
```

For details, see [nodetool recompress_sstables](../../operations/nodetool/recompress_sstables.md).

!!! warning "Operational Impact"
    Both `upgradesstables` and `recompress_sstables` perform disk-intensive operations. Schedule these during low-traffic periods and monitor disk I/O and compaction throughput during execution.

### Server-Level Compression Settings

Several `cassandra.yaml` settings control compression at the server level:

| Setting | Default | Description |
|---------|---------|-------------|
| `flush_compression` | table-configured | Controls compression during memtable flushes. Options: `none`, `fast`, or the table's configured compressor (4.1+, CASSANDRA-15379) |
| `commitlog_compression` | none | Compressor for commit log segments. Supports LZ4, Snappy, Deflate. See [Commit Log](commitlog.md) |
| `internode_compression` | `dc` | Compression for inter-node traffic. Options: `all`, `dc` (inter-DC only), `none` |
| `hints_compression` | none | Compressor for hint files. Supports LZ4, Snappy, Deflate |

---

## Chunk Size Tuning

The `chunk_length_in_kb` parameter is the primary tuning lever for compression performance. It controls the tradeoff between three factors:

| Factor | Smaller Chunks (4–16 KB) | Larger Chunks (64–256 KB) |
|--------|--------------------------|---------------------------|
| Read amplification | Lower — less wasted I/O per read | Higher — more data read and decompressed per request |
| Compression ratio | Lower — less data context per chunk | Higher — compressor has more data to find patterns |
| Off-heap memory | Higher — more chunk offsets to store | Lower — fewer chunk offsets |
| Random read latency | Lower | Higher |
| Sequential read throughput | Similar | Slightly better |

### Workload-Based Recommendations

| Access Pattern | Recommended chunk_length_in_kb | Rationale |
|----------------|:-----------------------------:|-----------|
| Random point reads | 4–16 | Minimizes read amplification; each read decompresses only a small block |
| Mixed read/write | 16 | Balanced tradeoff; matches Cassandra 4.0+ default |
| Range scans / sequential | 64–256 | Better compression ratio; sequential reads amortize decompression over many rows |
| Write-heavy with memory constraints | 64–128 | Reduces off-heap metadata overhead |

!!! info "Default Change in Cassandra 4.0"
    The default `chunk_length_in_kb` changed from 64 to 16 in Cassandra 4.0, reflecting that most production workloads are read-heavy with random access patterns. Tables created prior to 4.0 retain the 64 KB setting unless explicitly altered.

---

## Operational Guidance

### Monitoring Compression

Use `nodetool tablestats` to inspect compression behavior per table:

```bash
nodetool tablestats my_keyspace.my_table
```

Key fields:

| Field | Description |
|-------|-------------|
| `SSTable Compression Ratio` | Ratio of compressed to uncompressed size (e.g., 0.37 means 37% of original size) |
| `Compression metadata off heap memory used` | Off-heap memory consumed by compression offset tables |

A compression ratio close to 1.0 indicates the compressor provides minimal benefit for the data in that table. Consider disabling compression or switching algorithms.

### Algorithm Selection by Use Case

| Scenario | Recommended Algorithm | chunk_length_in_kb | Rationale |
|----------|----------------------|:------------------:|-----------|
| General purpose | LZ4Compressor | 16 | Safe default; fast compression and decompression |
| Read-heavy, latency-sensitive | LZ4Compressor | 4–16 | Minimizes decompression overhead and read amplification |
| Storage-constrained | ZstdCompressor | 16–64 | Better compression ratio with competitive decompression speed |
| Archival / cold data | DeflateCompressor or ZstdCompressor (high level) | 64–256 | Maximum storage reduction; read latency is less critical |
| Pre-compressed data | Disabled or NoopCompressor | — | Avoids double-compression overhead with no benefit |
| Write-heavy, memory-constrained | LZ4Compressor | 64 | Fast compression with lower off-heap overhead |

### When to Disable Compression

!!! danger "Do Not Disable Without Measurement"
    **Problem:** Disabling compression without profiling wastes disk space and increases I/O without improving latency.

    **Instead:** Use `nodetool tablestats` to check the compression ratio first. If the ratio is close to 1.0 (minimal compression benefit), disabling may be appropriate. If the ratio is 0.5 or lower, compression is providing significant storage and I/O savings.

Compression should be disabled only when:

- The compression ratio is consistently near 1.0 (the data does not compress)
- Data is pre-compressed or encrypted
- Off-heap memory is critically constrained and cannot accommodate compression metadata

### CRC Check Chance

!!! warning "Bitrot Detection"
    The `crc_check_chance` parameter (default 1.0) is Cassandra's primary defense against silent data corruption (bitrot) in SSTables. At the default value, every chunk read verifies its CRC32 checksum.

    Lowering this value reduces CPU overhead on the read path but increases the risk of serving corrupted data without detection. Only reduce `crc_check_chance` if performance profiling demonstrates CRC verification is a measurable bottleneck, and ensure other integrity mechanisms (e.g., filesystem checksums, hardware RAID) are in place.

---

## Version History

| Version | Change | Reference |
|---------|--------|-----------|
| 1.0 | SnappyCompressor and DeflateCompressor available | — |
| 1.2.2 | LZ4Compressor added | — |
| 2.0 | LZ4Compressor becomes the default compressor | — |
| 3.6 | LZ4 high-compression mode added (`lz4_compressor_type`, `lz4_high_compressor_level`) | CASSANDRA-11051 |
| 4.0 | ZstdCompressor added | CASSANDRA-14482 |
| 4.0 | Default `chunk_length_in_kb` changed from 64 to 16 | — |
| 4.0 | NoopCompressor added | — |
| 4.1 | `flush_compression` cassandra.yaml setting added | CASSANDRA-15379 |

---

## Related Documentation

- [SSTable Reference](sstables.md) — SSTable file format and components including CompressionInfo.db
- [Read Path](read-path.md) — how decompression fits into the read path
- [Commit Log](commitlog.md) — commit log compression (independent of SSTable compression)
- [Protocol Compression](../client-connections/compression.md) — CQL frame compression for client-node communication
- [nodetool recompress_sstables](../../operations/nodetool/recompress_sstables.md) — recompressing existing SSTables
