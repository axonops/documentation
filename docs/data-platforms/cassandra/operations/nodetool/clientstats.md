---
title: "nodetool clientstats"
description: "Display client connection statistics in Cassandra using nodetool clientstats command."
meta:
  - name: keywords
    content: "nodetool clientstats, client connections, Cassandra statistics, connection info"
---

# nodetool clientstats

Displays information about connected clients.

---

## Synopsis

```bash
nodetool [connection_options] clientstats [--all] [--by-protocol] [--clear]
```

## Description

`nodetool clientstats` displays statistics about client connections to the Cassandra node. This includes information about connected clients, their protocols, and connection details.

---

## Options

| Option | Description |
|--------|-------------|
| `--all` | Include all client information |
| `--by-protocol` | Group statistics by protocol version |
| `--clear` | Clear the statistics |

---

## Examples

### Basic Usage

```bash
nodetool clientstats
```

### Grouped by Protocol

```bash
nodetool clientstats --by-protocol
```

### Clear Statistics

```bash
nodetool clientstats --clear
```

---

## Output Fields

| Field | Description |
|-------|-------------|
| Address | Client IP address |
| Connections | Number of connections |
| Protocol version | CQL protocol version |
| User | Authenticated user (if auth enabled) |

---

## Use Cases

### Monitor Client Connections

```bash
# View all connected clients
nodetool clientstats --all
```

### Protocol Version Analysis

```bash
# Check which protocol versions are in use
nodetool clientstats --by-protocol
```

### Connection Troubleshooting

```bash
# Check for unexpected connections
nodetool clientstats | grep -v expected_client_ip
```

---

## Best Practices

!!! tip "Client Stats Guidelines"

    1. **Regular monitoring** - Track connection patterns
    2. **Protocol awareness** - Know which versions clients use
    3. **Security** - Identify unexpected connections
    4. **Capacity planning** - Monitor connection growth

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [status](status.md) | Cluster overview |
| [info](info.md) | Node information |
| [tpstats](tpstats.md) | Thread pool statistics |