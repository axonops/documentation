---
title: "CQLAI Troubleshooting"
description: "CQLAI troubleshooting guide. Common issues and solutions."
meta:
  - name: keywords
    content: "CQLAI troubleshooting, common issues, problem solving"
---

# CQLAI Troubleshooting

Common issues and solutions when using CQLAI.

---

## Connection Issues

### Cannot Connect to Cluster

**Symptom:** CQLAI fails to connect with timeout or connection refused errors.

**Diagnosis:**

```bash
# Test basic connectivity
nc -zv <cassandra-host> 9042

# Try with explicit host
cqlai --host <cassandra-host> --port 9042
```

**Solutions:**

| Cause | Solution |
|-------|----------|
| Wrong host/port | Verify connection parameters |
| Firewall blocking | Open port 9042 |
| Cassandra not running | Check `nodetool status` |
| SSL required | Add `--ssl` flag |

### Authentication Failures

**Symptom:** `AuthenticationException` or access denied errors.

**Solutions:**

```bash
# Connect with credentials
cqlai --username cassandra --password cassandra

# Or use environment variables
export CQLAI_USERNAME=cassandra
export CQLAI_PASSWORD=cassandra
cqlai
```

### SSL/TLS Connection Issues

**Symptom:** SSL handshake failures or certificate errors.

**Solutions:**

```bash
# Enable SSL
cqlai --ssl

# With custom certificate
cqlai --ssl --ssl-ca-cert /path/to/ca.crt

# Skip certificate verification (development only)
cqlai --ssl --ssl-skip-verify
```

---

## AI Feature Issues

### AI Provider Not Responding

**Symptom:** `.ai` commands hang or timeout.

**Diagnosis:**

```bash
# Check API key is set
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# Test provider connectivity
curl -I https://api.openai.com
```

**Solutions:**

| Cause | Solution |
|-------|----------|
| Missing API key | Set appropriate environment variable |
| Network issues | Check firewall/proxy settings |
| Rate limiting | Wait and retry, or use different provider |
| Invalid API key | Regenerate key from provider dashboard |

### Poor Query Generation

**Symptom:** AI generates incorrect or suboptimal CQL queries.

**Solutions:**

1. **Ensure schema is loaded**: Run `.schema` to verify CQLAI knows the current schema
2. **Be more specific**: Add column names and conditions to the request
3. **Use a different model**: Try GPT-4 or Claude for complex queries
4. **Review and edit**: Always review generated queries before execution

### Ollama Connection Issues

**Symptom:** Cannot connect to local Ollama instance.

**Solutions:**

```bash
# Verify Ollama is running
curl http://localhost:11434/api/tags

# Check model is available
ollama list

# Set correct endpoint (both variable names are supported)
export CQLAI_OLLAMA_HOST=http://localhost:11434
# or
export OLLAMA_URL=http://localhost:11434
```

---

## Query Execution Issues

### Syntax Errors

**Symptom:** CQL syntax errors when executing queries.

**Solutions:**

- Check for missing semicolons
- Verify keyspace/table names are correct
- Use `.schema` to check available tables and columns
- Quote identifiers with special characters

### Timeout During Query

**Symptom:** Query times out before completing.

**Solutions:**

```bash
# Increase timeout (value in seconds)
cqlai --request-timeout 60

# For large result sets, use paging
cqlai --page-size 100
```

### Large Result Set Issues

**Symptom:** Memory issues or slow display with large results.

**Solutions:**

```bash
# Limit results
SELECT * FROM table LIMIT 100;

# Enable paging
cqlai --page-size 1000

# Export to file instead
.export table results.csv
```

---

## Parquet Export Issues

### Export Fails

**Symptom:** Parquet export command fails with errors.

**Diagnosis:**

```bash
# Check disk space
df -h .

# Verify write permissions
touch test.parquet && rm test.parquet
```

**Solutions:**

| Cause | Solution |
|-------|----------|
| Insufficient disk space | Free up space or export to different location |
| Permission denied | Check write permissions |
| Invalid query | Test query first before export |
| Memory exhausted | Reduce batch size or use streaming |

### Corrupted Parquet Files

**Symptom:** Exported Parquet files cannot be read.

**Solutions:**

1. Re-run the export with `--overwrite`
2. Check for disk errors
3. Verify sufficient disk space during entire export
4. Try exporting smaller batches

---

## Display Issues

### Output Formatting Problems

**Symptom:** Results display incorrectly or are hard to read.

**Solutions:**

```bash
# Switch output format
.format json
.format table
.format vertical

# Adjust column width
.width 120
```

### Unicode/Character Issues

**Symptom:** Special characters display as question marks or boxes.

**Solutions:**

- Set terminal encoding to UTF-8
- Use a terminal that supports Unicode
- Check `LANG` and `LC_ALL` environment variables

---

## Performance Issues

### Slow Startup

**Symptom:** CQLAI takes a long time to start.

**Solutions:**

- Check network connectivity to Cassandra
- Disable auto-schema loading if not needed
- Verify DNS resolution is working

### High Memory Usage

**Symptom:** CQLAI consumes excessive memory.

**Solutions:**

- Use paging for large queries
- Export large results to files
- Close and restart for long-running sessions

---

## Configuration Issues

### Configuration Not Loading

**Symptom:** Settings from config file are ignored.

**Diagnosis:**

```bash
# Check config file locations
ls -la ~/.cqlai.json ~/.config/cqlai/config.json ./cqlai.json

# Verify JSON syntax
cat ~/.config/cqlai/config.json | python3 -m json.tool
```

**Solutions:**

1. Ensure config file is valid JSON
2. Check file permissions
3. Use explicit config path: `cqlai --config-file /path/to/config.json`

### Environment Variables Not Working

**Symptom:** Environment variables are ignored.

**Solutions:**

```bash
# Verify variables are exported
env | grep CQLAI

# Check for typos in variable names
export CQLAI_HOST=localhost  # Correct
export CQLAIHOST=localhost   # Wrong
```

---

## Getting Help

### Useful Commands

```bash
# Show version
cqlai --version

# Show help
cqlai --help

# Show available dot commands
.help

# Enable debug logging
cqlai --debug
```

### Reporting Issues

When reporting issues, include:

1. CQLAI version (`cqlai --version`)
2. Cassandra version
3. Operating system
4. Full error message
5. Steps to reproduce

Report issues at: [github.com/axonops/cqlai/issues](https://github.com/axonops/cqlai/issues)

---

## Related Documentation

- [Installation](installation/index.md) - Installation instructions
- [Configuration](configuration/index.md) - Configuration options
- [AI Features](ai-features/index.md) - AI provider setup
