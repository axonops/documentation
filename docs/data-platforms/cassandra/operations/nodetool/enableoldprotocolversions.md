---
title: "nodetool enableoldprotocolversions"
description: "Enable old CQL protocol versions in Cassandra using nodetool enableoldprotocolversions."
meta:
  - name: keywords
    content: "nodetool enableoldprotocolversions, CQL protocol, protocol versions, Cassandra"
---

# nodetool enableoldprotocolversions

Enables support for older CQL protocol versions.

---

## Synopsis

```bash
nodetool [connection_options] enableoldprotocolversions
```

## Description

`nodetool enableoldprotocolversions` re-enables support for older CQL native protocol versions that may have been disabled. This allows older clients to connect.

---

## Examples

### Basic Usage

```bash
nodetool enableoldprotocolversions
```

---

## When to Use

### Support Legacy Clients

```bash
# If older clients can't connect
nodetool enableoldprotocolversions
```

---

## Best Practices

!!! warning "Security Consideration"

    Older protocol versions may lack security features. Only enable when necessary for compatibility.

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [disableoldprotocolversions](disableoldprotocolversions.md) | Disable old versions |
| [clientstats](clientstats.md) | View client connections |