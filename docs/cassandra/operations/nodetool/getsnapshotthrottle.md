# nodetool getsnapshotthrottle

Displays the snapshot link creation throttle.

---

## Synopsis

```bash
nodetool [connection_options] getsnapshotthrottle
```

## Description

`nodetool getsnapshotthrottle` shows the current throttle rate for snapshot hard link creation in MB/s. This limits the I/O impact of snapshot operations.

---

## Examples

### Basic Usage

```bash
nodetool getsnapshotthrottle
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [setsnapshotthrottle](setsnapshotthrottle.md) | Modify throttle |
| [snapshot](snapshot.md) | Create snapshots |
