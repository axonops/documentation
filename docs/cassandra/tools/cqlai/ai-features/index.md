---
title: "CQLAI AI Features"
description: "CQLAI AI features overview. Natural language queries and intelligent suggestions."
meta:
  - name: keywords
    content: "CQLAI AI features, natural language, intelligent suggestions"
---

# CQLAI AI Features

CQLAI includes optional AI-powered query generation that converts natural language into CQL queries. This feature is completely optional - CQLAI works as a full-featured CQL shell without any AI configuration.

## Overview

Use the `.ai` command to describe the desired query in plain English:

```sql
cqlai> .ai show all active users who registered this month

Generated CQL:
  SELECT * FROM users
  WHERE status = 'active'
  AND created_at >= '2024-01-01'
  AND created_at < '2024-02-01'
  ALLOW FILTERING;

Execute? [Y/n]:
```

## How It Works

1. **Natural Language Input**: Type `.ai` followed by the request
2. **Schema Context**: CQLAI automatically extracts the current schema
3. **Query Generation**: AI generates a CQL query based on the schema
4. **Preview & Confirm**: Review the generated query before execution
5. **Execute or Edit**: Run the query, modify it, or cancel

## Supported AI Providers

| Provider | Models | API Key Required | Local Option |
|----------|--------|------------------|--------------|
| **OpenAI** | GPT-4, GPT-3.5 | Yes | No |
| **Anthropic** | Claude 3 (Opus, Sonnet, Haiku) | Yes | No |
| **Google Gemini** | Gemini Pro | Yes | No |
| **Ollama** | Llama, Mistral, CodeLlama, etc. | No | Yes |
| **OpenRouter** | Multiple models | Yes | No |
| **Synthetic** | Open source models | Yes | No |
| **Mock** | (Testing only) | No | Yes |

---

## Provider Configuration

### OpenAI

Best for general-purpose query generation with high accuracy.

**Get API Key**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

```json
{
  "ai": {
    "provider": "openai",
    "apiKey": "sk-...",
    "model": "gpt-4-turbo-preview"
  }
}
```

**Recommended Models**:
- `gpt-4-turbo-preview` - Best quality (default)
- `gpt-4o` - Fast and capable
- `gpt-3.5-turbo` - Cost-effective

**Environment Variable**: `OPENAI_API_KEY`

### Anthropic (Claude)

Excellent for complex reasoning and context-aware queries.

**Get API Key**: [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)

```json
{
  "ai": {
    "provider": "anthropic",
    "apiKey": "sk-ant-...",
    "model": "claude-3-sonnet-20240229"
  }
}
```

**Recommended Models**:
- `claude-3-opus-20240229` - Most powerful
- `claude-3-sonnet-20240229` - Balanced (default)
- `claude-3-haiku-20240307` - Fastest

**Environment Variable**: `ANTHROPIC_API_KEY`

### Google Gemini

Fast and capable model from Google.

**Get API Key**: [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

```json
{
  "ai": {
    "provider": "gemini",
    "apiKey": "...",
    "model": "gemini-pro"
  }
}
```

**Environment Variable**: `GEMINI_API_KEY`

### Ollama (Local)

Run AI models locally without sending data externally.

**Get Started**: [ollama.ai](https://ollama.ai)

```json
{
  "ai": {
    "provider": "ollama",
    "model": "llama3.2",
    "url": "http://localhost:11434/v1"
  }
}
```

**Recommended Models**:
- `llama3.2` - General purpose
- `codellama` - Code-specialized
- `qwen2.5-coder` - Code generation
- `mistral` - Fast and capable

**Setup**:
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama3.2

# Configure CQLAI
cqlai  # Uses local Ollama automatically
```

**Environment Variables**:
- `OLLAMA_URL` - Server URL (default: `http://localhost:11434/v1`)
- `OLLAMA_MODEL` - Model name

### OpenRouter

Access multiple AI models through a single API.

**Get API Key**: [openrouter.ai/keys](https://openrouter.ai/keys)

```json
{
  "ai": {
    "provider": "openrouter",
    "apiKey": "sk-or-...",
    "model": "anthropic/claude-3-sonnet",
    "url": "https://openrouter.ai/api/v1"
  }
}
```

**Available Models**: See [openrouter.ai/models](https://openrouter.ai/models)

### Synthetic

Access various open-source models at affordable prices.

**Get Started**: [synthetic.new](https://synthetic.new/)

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

Note: Synthetic uses OpenAI-compatible API, so set `provider` to `openai` with custom `url`.

### Mock Provider (Testing)

For testing without API keys:

```json
{
  "ai": {
    "provider": "mock"
  }
}
```

---

## Usage Examples

### Simple Queries

```sql
-- List data
.ai show all users
.ai list the first 10 orders
.ai count products by category

-- Filters
.ai find users where status is active
.ai get orders with total greater than 100
.ai show products added in the last 7 days
```

### Complex Queries

```sql
-- Aggregations
.ai count orders grouped by customer
.ai show total revenue per month

-- Joins (via denormalized tables)
.ai find all orders for customer john@example.com
.ai get user details with their recent orders
```

### Schema Operations

```sql
-- DDL
.ai create a table for storing user sessions with session_id, user_id, created_at, and expires_at
.ai add a column 'last_login' to the users table
.ai create an index on the email column of users table

-- Discovery
.ai what tables exist in this keyspace
.ai describe the users table structure
.ai show the primary key of orders table
```

### Data Modification

```sql
-- Insert
.ai insert a new user with name John Doe and email john@example.com

-- Update
.ai update user status to inactive where last_login is older than 90 days
.ai set the email to new@example.com for user with id abc123

-- Delete (with warnings)
.ai delete all expired sessions
.ai remove products with stock count of zero
```

---

## Safety Features

### Read-Only Preference

By default, AI prefers generating SELECT queries unless modifications are explicitly requested:

```sql
.ai users                    -- Generates: SELECT * FROM users
.ai delete inactive users    -- Generates DELETE with warnings
```

### Dangerous Operation Warnings

Destructive operations display warnings:

```sql
.ai drop the temp_data table

⚠️  WARNING: This is a destructive operation!
Generated CQL:
  DROP TABLE temp_data;

This will permanently delete the table and all its data.
Type 'yes' to confirm:
```

### Confirmation Required

All generated queries require confirmation before execution:

```sql
.ai show all users

Generated CQL:
  SELECT * FROM users;

Execute? [Y/n]:
```

Options:
- `Y` or Enter - Execute the query
- `n` - Cancel
- `e` - Edit the query before executing

### Schema Validation

CQLAI validates generated queries against the current schema to catch errors before execution.

---

## Best Practices

### Be Specific

```sql
-- Good
.ai show users where created_at is after January 1, 2024

-- Too vague
.ai show recent users
```

### Mention Table Names

```sql
-- Good
.ai count rows in the orders table

-- May be ambiguous
.ai count all orders
```

### Review Generated Queries

Always review the generated CQL before execution, especially for:
- DELETE operations
- UPDATE operations
- DDL commands (CREATE, ALTER, DROP)

### Use for Discovery

AI is useful for exploring the schema:

```sql
.ai what tables are in this keyspace
.ai show me the schema of the events table
.ai how is the users table partitioned
```

---

## Troubleshooting

### AI Not Responding

1. Check API key is configured correctly
2. Verify network connectivity to API endpoint
3. Check for rate limiting

```bash
# Test with curl
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Poor Query Generation

1. Be more specific in the request
2. Mention table and column names explicitly
3. Try a different model (GPT-4 vs GPT-3.5)

### Ollama Connection Issues

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Check model is pulled
ollama list
```

---

## Privacy Considerations

When using AI features:

1. **Schema Information Sent**: The schema (table names, columns, types) is sent to the AI provider for context
2. **Query Intent Sent**: The natural language request is sent to the provider
3. **Data Not Sent**: Actual data is never sent to AI providers

For maximum privacy, use **Ollama** to run models locally.

---

## Next Steps

- **[Commands Reference](../commands/index.md)** - All CQLAI commands
- **[Configuration](../configuration/index.md)** - Full configuration options
- **[Troubleshooting](../troubleshooting.md)** - Common issues
