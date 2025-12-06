# CQLAI Configuration

CQLAI supports multiple configuration methods for maximum flexibility and compatibility with existing Cassandra setups.

## Configuration Precedence

Configuration sources are loaded in order (later sources override earlier ones):

1. **CQLSHRC files** (for cqlsh compatibility)
2. **CQLAI JSON files**
3. **Environment variables**
4. **Command-line flags** (highest priority)

---

## Command-Line Options

### Connection Options

| Option | Short | Description |
|--------|-------|-------------|
| `--host <host>` | | Cassandra host |
| `--port <port>` | | Cassandra port (default: 9042) |
| `--keyspace <ks>` | `-k` | Default keyspace |
| `--username <user>` | `-u` | Authentication username |
| `--password <pass>` | `-p` | Authentication password* |
| `--connect-timeout <sec>` | | Connection timeout (default: 10) |
| `--request-timeout <sec>` | | Request timeout (default: 10) |
| `--no-confirm` | | Disable confirmation prompts |
| `--debug` | | Enable debug logging |

*Password can be provided via:
1. `-p` flag (not recommended - visible in process list)
2. Interactive prompt when `-u` is used without `-p`
3. `CQLAI_PASSWORD` environment variable

### Batch Mode Options

| Option | Short | Description |
|--------|-------|-------------|
| `--execute <stmt>` | `-e` | Execute statement and exit |
| `--file <file>` | `-f` | Execute CQL file and exit |
| `--format <fmt>` | | Output: ascii, json, csv, table |
| `--no-header` | | Omit column headers (CSV) |
| `--field-separator <sep>` | | Field separator (default: `,`) |
| `--page-size <n>` | | Rows per batch (default: 100) |

### General Options

| Option | Short | Description |
|--------|-------|-------------|
| `--config-file <path>` | | Path to config file |
| `--help` | `-h` | Show help |
| `--version` | `-v` | Show version |

### Examples

```bash
# Interactive with authentication
cqlai --host cassandra.example.com -u myuser
# Password: [hidden prompt]

# Execute single statement
cqlai -e "SELECT * FROM users LIMIT 10;"

# Execute script file
cqlai -f schema.cql

# JSON output
cqlai -e "SELECT * FROM users;" --format json

# With specific keyspace
cqlai --host 127.0.0.1 -k my_keyspace

# Using password from environment
export CQLAI_PASSWORD=secret
cqlai --host 127.0.0.1 -u admin
```

---

## Configuration File (cqlai.json)

CQLAI uses a JSON configuration file for advanced settings.

### File Locations

CQLAI searches for configuration in:

1. `./cqlai.json` (current directory)
2. `~/.cqlai.json` (home directory)
3. `~/.config/cqlai/config.json` (XDG config directory)

Or specify explicitly:
```bash
cqlai --config-file /path/to/config.json
```

### Complete Configuration Reference

```json
{
  "host": "127.0.0.1",
  "port": 9042,
  "keyspace": "",
  "username": "",
  "password": "",
  "requireConfirmation": true,
  "consistency": "LOCAL_ONE",
  "pageSize": 100,
  "maxMemoryMB": 10,
  "connectTimeout": 10,
  "requestTimeout": 10,
  "debug": false,
  "historyFile": "~/.cqlai/history",
  "aiHistoryFile": "~/.cqlai/ai_history",
  "ssl": {
    "enabled": false,
    "certPath": "/path/to/client-cert.pem",
    "keyPath": "/path/to/client-key.pem",
    "caPath": "/path/to/ca-cert.pem",
    "hostVerification": true,
    "insecureSkipVerify": false
  },
  "ai": {
    "provider": "openai",
    "apiKey": "sk-...",
    "model": "gpt-4-turbo-preview",
    "url": ""
  }
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `host` | string | `127.0.0.1` | Cassandra host |
| `port` | number | `9042` | Cassandra port |
| `keyspace` | string | `""` | Default keyspace |
| `username` | string | `""` | Authentication username |
| `password` | string | `""` | Authentication password |
| `requireConfirmation` | boolean | `true` | Confirm dangerous commands |
| `consistency` | string | `LOCAL_ONE` | Default consistency level |
| `pageSize` | number | `100` | Rows per page |
| `maxMemoryMB` | number | `10` | Max memory for results |
| `connectTimeout` | number | `10` | Connection timeout (seconds) |
| `requestTimeout` | number | `10` | Request timeout (seconds) |
| `debug` | boolean | `false` | Enable debug logging |
| `historyFile` | string | `~/.cqlai/history` | Command history path |
| `aiHistoryFile` | string | `~/.cqlai/ai_history` | AI history path |

### SSL/TLS Configuration

```json
{
  "ssl": {
    "enabled": true,
    "certPath": "/path/to/client-cert.pem",
    "keyPath": "/path/to/client-key.pem",
    "caPath": "/path/to/ca-cert.pem",
    "hostVerification": true,
    "insecureSkipVerify": false
  }
}
```

| Option | Description |
|--------|-------------|
| `enabled` | Enable SSL/TLS |
| `certPath` | Client certificate path |
| `keyPath` | Client key path |
| `caPath` | CA certificate path |
| `hostVerification` | Verify server hostname |
| `insecureSkipVerify` | Skip certificate verification (not recommended) |

---

## Environment Variables

### Connection Variables

| Variable | Description |
|----------|-------------|
| `CQLAI_HOST` | Cassandra host |
| `CQLAI_PORT` | Cassandra port |
| `CQLAI_KEYSPACE` | Default keyspace |
| `CQLAI_USERNAME` | Username |
| `CQLAI_PASSWORD` | Password (secure for scripts) |
| `CQLAI_PAGE_SIZE` | Batch mode page size |

### Compatibility Variables

| Variable | Description |
|----------|-------------|
| `CASSANDRA_HOST` | Alternative host variable |
| `CASSANDRA_PORT` | Alternative port variable |
| `CQLSH_RC` | Path to cqlshrc file |

### AI Provider Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `GEMINI_API_KEY` | Google Gemini API key |
| `OPENROUTER_API_KEY` | OpenRouter API key |
| `OLLAMA_URL` | Ollama server URL |
| `OLLAMA_MODEL` | Ollama model name |

### Example

```bash
# Set credentials via environment
export CQLAI_HOST=cassandra.example.com
export CQLAI_USERNAME=admin
export CQLAI_PASSWORD=secret
export OPENAI_API_KEY=sk-...

# Run CQLAI
cqlai
```

---

## CQLSHRC Compatibility

CQLAI can read standard CQLSHRC files used by cqlsh, making migration seamless.

### Supported Sections

- `[connection]` - hostname, port, ssl settings
- `[authentication]` - keyspace, credentials file path
- `[auth_provider]` - authentication module and username
- `[ssl]` - SSL/TLS certificate configuration

### CQLSHRC Locations

1. `$CQLSH_RC` (if set)
2. `~/.cassandra/cqlshrc`
3. `~/.cqlshrc`

### Example CQLSHRC

```ini
; ~/.cassandra/cqlshrc
[connection]
hostname = cassandra.example.com
port = 9042
ssl = true

[authentication]
keyspace = my_keyspace
credentials = ~/.cassandra/credentials

[ssl]
certfile = ~/certs/ca.pem
userkey = ~/certs/client-key.pem
usercert = ~/certs/client-cert.pem
validate = true
```

CQLAI will automatically read this configuration if present.

---

## AI Provider Configuration

Configure AI for natural language query generation. See [AI Features](../ai-features/index.md) for detailed setup.

### OpenAI

```json
{
  "ai": {
    "provider": "openai",
    "apiKey": "sk-...",
    "model": "gpt-4-turbo-preview"
  }
}
```

### Anthropic

```json
{
  "ai": {
    "provider": "anthropic",
    "apiKey": "sk-ant-...",
    "model": "claude-3-sonnet-20240229"
  }
}
```

### Ollama (Local)

```json
{
  "ai": {
    "provider": "ollama",
    "model": "llama3.2",
    "url": "http://localhost:11434/v1"
  }
}
```

### Synthetic (Open Source Models)

```json
{
  "ai": {
    "provider": "openai",
    "apiKey": "your-synthetic-api-key",
    "url": "https://api.synthetic.new/openai/v1",
    "model": "hf:Qwen/Qwen3-235B-A22B-Instruct-2507"
  }
}
```

---

## Example Configurations

### Development

```json
{
  "host": "127.0.0.1",
  "port": 9042,
  "consistency": "ONE",
  "pageSize": 50,
  "requireConfirmation": false
}
```

### Production

```json
{
  "host": "cassandra.prod.example.com",
  "port": 9042,
  "keyspace": "production",
  "consistency": "LOCAL_QUORUM",
  "pageSize": 100,
  "requireConfirmation": true,
  "connectTimeout": 30,
  "requestTimeout": 30,
  "ssl": {
    "enabled": true,
    "certPath": "/etc/cqlai/client-cert.pem",
    "keyPath": "/etc/cqlai/client-key.pem",
    "caPath": "/etc/cqlai/ca-cert.pem",
    "hostVerification": true
  }
}
```

### With AI Enabled

```json
{
  "host": "127.0.0.1",
  "port": 9042,
  "ai": {
    "provider": "anthropic",
    "apiKey": "sk-ant-...",
    "model": "claude-3-sonnet-20240229"
  }
}
```

---

## Next Steps

- **[AI Features](../ai-features/index.md)** - Configure AI providers in detail
- **[Commands Reference](../commands/index.md)** - Available commands
- **[Troubleshooting](../troubleshooting.md)** - Common configuration issues
