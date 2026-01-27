---
title: "nodetool reloadtriggers"
description: "Reload trigger classes in Cassandra using nodetool reloadtriggers command."
meta:
  - name: keywords
    content: "nodetool reloadtriggers, reload triggers, Cassandra triggers, hot reload"
---

# nodetool reloadtriggers

Reloads trigger classes.

---

## Synopsis

```bash
nodetool [connection_options] reloadtriggers
```

## Description

`nodetool reloadtriggers` reloads custom trigger classes from the triggers directory without requiring a node restart. Triggers are custom code that executes on mutations.

---

## Examples

### Basic Usage

```bash
nodetool reloadtriggers
```

---

## When to Use

### After Updating Trigger JARs

```bash
# 1. Copy new trigger JAR to triggers directory
cp my_trigger.jar /etc/cassandra/triggers/

# 2. Reload triggers
nodetool reloadtriggers
```

### After Removing Triggers

```bash
# 1. Remove trigger JAR
rm /etc/cassandra/triggers/old_trigger.jar

# 2. Reload
nodetool reloadtriggers
```

---

## Trigger Directory

Default location:
```
/etc/cassandra/triggers/
```

Or configured in cassandra.yaml.

---

## Best Practices

!!! tip "Guidelines"

    1. **Test triggers** - Test in non-production first
    2. **Cluster-wide** - Update and reload on all nodes
    3. **Version control** - Track trigger code changes

---

## Related Commands

| Command | Relationship |
|---------|--------------|
| [reloadlocalschema](reloadlocalschema.md) | Reload schema |
| [reloadssl](reloadssl.md) | Reload SSL certificates |