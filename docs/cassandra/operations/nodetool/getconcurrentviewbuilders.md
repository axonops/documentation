# nodetool getconcurrentviewbuilders

Displays the number of concurrent view builders.

---

## Synopsis

```bash
nodetool [connection_options] getconcurrentviewbuilders
```

## Description

`nodetool getconcurrentviewbuilders` shows the current number of threads available for building materialized views concurrently.

---

## Examples

### Basic Usage

```bash
nodetool getconcurrentviewbuilders
```

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [setconcurrentviewbuilders](setconcurrentviewbuilders.md) | Modify builders |
| [viewbuildstatus](viewbuildstatus.md) | View build status |
