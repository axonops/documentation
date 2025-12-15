---
title: "CQLAI AI Providers"
description: "CQLAI AI providers configuration. Connect to OpenAI, Anthropic, and other models."
meta:
  - name: keywords
    content: "CQLAI AI providers, OpenAI, Anthropic, LLM configuration"
---

# CQLAI AI Providers

Configure AI providers for natural language query generation in CQLAI.

## Supported Providers

| Provider | Models | Best For |
|----------|--------|----------|
| OpenAI | GPT-4, GPT-4 Turbo, GPT-3.5 Turbo | Best accuracy |
| Anthropic | Claude 3 Opus, Sonnet, Haiku | Complex reasoning |
| Azure OpenAI | GPT-4, GPT-3.5 | Enterprise compliance |
| AWS Bedrock | Claude, Titan | AWS integration |
| Google Vertex AI | Gemini Pro | Google Cloud |
| Ollama | Llama 3, Mixtral, etc. | Local/private |
| OpenAI-compatible | Various | Custom endpoints |

## OpenAI Configuration

### Setup

```bash
# Environment variable
export CQLAI_AI_PROVIDER=openai
export CQLAI_AI_KEY=sk-...

# Or command line
cqlai --ai-provider openai --ai-key sk-...
```

### Configuration File

```yaml
# ~/.cqlai/config.yaml
ai:
  provider: openai
  model: gpt-4-turbo
  # key from CQLAI_AI_KEY environment variable

  options:
    temperature: 0.1
    max_tokens: 1000
```

### Available Models

| Model | Speed | Accuracy | Cost |
|-------|-------|----------|------|
| gpt-4-turbo | Fast | Highest | $$$$ |
| gpt-4 | Slow | Highest | $$$$ |
| gpt-3.5-turbo | Fastest | Good | $ |

## Anthropic Configuration

### Setup

```bash
export CQLAI_AI_PROVIDER=anthropic
export CQLAI_AI_KEY=sk-ant-...
```

### Configuration

```yaml
ai:
  provider: anthropic
  model: claude-3-sonnet-20240229

  options:
    temperature: 0.1
    max_tokens: 1000
```

### Available Models

| Model | Speed | Accuracy | Cost |
|-------|-------|----------|------|
| claude-3-opus | Slow | Highest | $$$$ |
| claude-3-sonnet | Fast | High | $$ |
| claude-3-haiku | Fastest | Good | $ |

## Azure OpenAI Configuration

### Setup

```bash
export CQLAI_AI_PROVIDER=azure
export CQLAI_AI_KEY=your-azure-key
export CQLAI_AZURE_ENDPOINT=https://your-resource.openai.azure.com
export CQLAI_AZURE_DEPLOYMENT=your-deployment-name
```

### Configuration

```yaml
ai:
  provider: azure
  azure:
    endpoint: https://your-resource.openai.azure.com
    deployment: gpt-4-deployment
    api_version: "2024-02-15-preview"
```

## AWS Bedrock Configuration

### Setup

```bash
export CQLAI_AI_PROVIDER=bedrock
export AWS_REGION=us-east-1
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
```

### Configuration

```yaml
ai:
  provider: bedrock
  model: anthropic.claude-3-sonnet-20240229-v1:0

  bedrock:
    region: us-east-1
```

## Google Vertex AI Configuration

### Setup

```bash
export CQLAI_AI_PROVIDER=vertex
export GOOGLE_CLOUD_PROJECT=your-project
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

### Configuration

```yaml
ai:
  provider: vertex
  model: gemini-pro

  vertex:
    project: your-project
    location: us-central1
```

## Ollama (Local AI)

Run AI models locally without cloud dependencies.

### Install Ollama

```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# macOS
brew install ollama

# Start Ollama
ollama serve
```

### Pull Model

```bash
# Recommended for CQL generation
ollama pull llama3
ollama pull codellama
ollama pull mixtral
```

### Configure CQLAI

```bash
export CQLAI_AI_PROVIDER=ollama
export CQLAI_OLLAMA_HOST=http://localhost:11434
```

```yaml
ai:
  provider: ollama
  model: llama3

  ollama:
    host: http://localhost:11434
```

### Recommended Local Models

| Model | Parameters | RAM | Best For |
|-------|------------|-----|----------|
| llama3 | 8B | 8GB | General use |
| codellama | 7B | 8GB | Code generation |
| mixtral | 8x7B | 48GB | Complex queries |

## OpenAI-Compatible Endpoints

Use any OpenAI-compatible API endpoint.

```yaml
ai:
  provider: openai-compatible
  model: your-model

  openai_compatible:
    endpoint: https://your-api.example.com/v1
    api_key_env: YOUR_API_KEY_VAR
```

## Provider Comparison

### Accuracy vs Cost

```
Accuracy:   Claude 3 Opus ≈ GPT-4 > GPT-4 Turbo > Claude Sonnet > GPT-3.5
Speed:      GPT-3.5 > Claude Haiku > GPT-4 Turbo > Claude Sonnet > GPT-4
Cost:       Ollama (free) < GPT-3.5 < Claude Haiku < Sonnet < GPT-4
Privacy:    Ollama (local) > Azure (enterprise) > Cloud providers
```

### Recommendations

| Use Case | Recommended Provider |
|----------|---------------------|
| Development | Ollama (free, local) |
| Production (accuracy) | OpenAI GPT-4 or Claude Opus |
| Production (cost) | Claude Haiku or GPT-3.5 |
| Enterprise/Compliance | Azure OpenAI |
| AWS Environment | AWS Bedrock |
| Privacy-critical | Ollama (local) |

## Configuration Options

### Common Options

```yaml
ai:
  provider: openai
  model: gpt-4-turbo

  options:
    # Lower = more deterministic (recommended for CQL)
    temperature: 0.1

    # Maximum response length
    max_tokens: 1000

    # Include table schemas in context
    include_schema: true

    # Number of schema tables to include
    schema_context_limit: 10

    # Retry failed requests
    retry_count: 3
    retry_delay: 1s
```

### Context Settings

```yaml
ai:
  context:
    # Always include current keyspace schema
    include_current_keyspace: true

    # Include table statistics for optimization hints
    include_statistics: true

    # Maximum schema size to send
    max_schema_size: 50000
```

## Security Best Practices

1. **Never commit API keys** - Use environment variables
2. **Use Azure/Bedrock for enterprise** - Better compliance
3. **Consider Ollama** - No data leaves your network
4. **Rotate keys regularly** - Set up key rotation
5. **Monitor usage** - Track API costs and calls

```bash
# Secure key storage
# Store in environment, not config file
export CQLAI_AI_KEY=$(cat ~/.secrets/openai_key)
```

## Troubleshooting

### API Key Issues

```
Error: Invalid API key

Solutions:
1. Verify key is correct
2. Check key permissions
3. Ensure key is not expired
4. Verify environment variable is set
```

### Rate Limiting

```
Error: Rate limit exceeded

Solutions:
1. Use a model with higher limits
2. Add retry configuration
3. Implement request caching
4. Upgrade API plan
```

### Local Model Issues (Ollama)

```
Error: Connection refused

Solutions:
1. Ensure Ollama is running: ollama serve
2. Check port: http://localhost:11434
3. Verify model is pulled: ollama list
```

---

## Next Steps

- **[AI Features](../index.md)** - AI capabilities overview
- **[Getting Started](../../getting-started/index.md)** - CQLAI basics
- **[Configuration](../../configuration/index.md)** - Full configuration reference
