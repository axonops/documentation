# nodetool getconcurrency

Displays the concurrency settings.

---

## Synopsis

```bash
nodetool [connection_options] getconcurrency
```

## Description

`nodetool getconcurrency` shows the current concurrency settings for various operations including reads, writes, and counter writes.

---

## Examples

### Basic Usage

```bash
nodetool getconcurrency
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [setconcurrency](setconcurrency.md) | Modify concurrency |
| [tpstats](tpstats.md) | Thread pool statistics |
