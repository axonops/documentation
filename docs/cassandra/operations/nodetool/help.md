# nodetool help

Displays help information for nodetool commands.

---

## Synopsis

```bash
nodetool help [command]
```

## Description

`nodetool help` displays usage information for nodetool. When called without arguments, it lists all available commands. When called with a command name, it shows detailed help for that specific command.

---

## Examples

### List All Commands

```bash
nodetool help
```

### Help for Specific Command

```bash
nodetool help status
nodetool help repair
nodetool help compact
```

---

## Output

### General Help

Lists all available nodetool commands with brief descriptions.

### Command-Specific Help

Shows:
- Command synopsis
- Description
- Available options
- Arguments

---

## Use Cases

### Discover Commands

```bash
# List all commands
nodetool help | less
```

### Learn Command Options

```bash
# Get detailed options for repair
nodetool help repair
```

---

## Alternative

```bash
# Most commands also support --help
nodetool status --help
nodetool repair --help
```

---

## Related Commands

All nodetool commands can be explored via help.
