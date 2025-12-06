# CQLAI Data Import/Export

Import and export data using CQLAI with support for multiple formats.

## Export Data

### Export Table to CSV

```
cqlai> .export users /tmp/users.csv

Exporting users to /tmp/users.csv...
Exported 10,532 rows in 2.3s
```

### Export to JSON

```
cqlai> .export users /tmp/users.json --format json

Exporting users to /tmp/users.json...
Exported 10,532 rows in 2.8s
```

### Export Query Results

```
cqlai> .export "SELECT user_id, email FROM users WHERE status = 'active'" /tmp/active_users.csv

Exporting query results to /tmp/active_users.csv...
Exported 8,234 rows in 1.9s
```

### Export Options

```
cqlai> .export users /tmp/users.csv \
    --format csv \
    --delimiter ";" \
    --quote "'" \
    --header true \
    --null-value "NULL" \
    --batch-size 5000
```

| Option | Description | Default |
|--------|-------------|---------|
| `--format` | Output format (csv, json, jsonl) | csv |
| `--delimiter` | CSV field delimiter | `,` |
| `--quote` | CSV quote character | `"` |
| `--header` | Include header row | true |
| `--null-value` | Representation for NULL | (empty) |
| `--batch-size` | Rows per batch | 1000 |
| `--compress` | Gzip output | false |

### Export with Compression

```
cqlai> .export users /tmp/users.csv.gz --compress

Exporting users to /tmp/users.csv.gz (compressed)...
Exported 10,532 rows in 1.8s (compressed 12MB → 2.1MB)
```

### Export Specific Columns

```
cqlai> .export "SELECT user_id, username, email FROM users" /tmp/users_subset.csv
```

## Import Data

### Import from CSV

```
cqlai> .import /tmp/users.csv users

Importing /tmp/users.csv into users...
Imported 10,532 rows in 4.2s
```

### Import from JSON

```
cqlai> .import /tmp/users.json users --format json

Importing /tmp/users.json into users...
Imported 10,532 rows in 5.1s
```

### Import Options

```
cqlai> .import /tmp/users.csv users \
    --format csv \
    --delimiter "," \
    --skip-header true \
    --batch-size 100 \
    --consistency LOCAL_QUORUM \
    --skip-errors true \
    --max-errors 100
```

| Option | Description | Default |
|--------|-------------|---------|
| `--format` | Input format (csv, json, jsonl) | auto-detect |
| `--delimiter` | CSV field delimiter | `,` |
| `--skip-header` | Skip first row | true |
| `--batch-size` | Rows per batch insert | 100 |
| `--consistency` | Write consistency level | LOCAL_ONE |
| `--skip-errors` | Continue on errors | false |
| `--max-errors` | Max errors before abort | 0 (unlimited) |
| `--dry-run` | Validate without inserting | false |

### Preview Before Import

```
cqlai> .import /tmp/users.csv users --preview

Preview of /tmp/users.csv:

Detected columns: user_id (uuid), username (text), email (text), created_at (timestamp)

Sample rows:
┌──────────────────────────────────────┬──────────┬─────────────────────┬─────────────────────┐
│ user_id                              │ username │ email               │ created_at          │
├──────────────────────────────────────┼──────────┼─────────────────────┼─────────────────────┤
│ 123e4567-e89b-12d3-a456-426614174000 │ alice    │ alice@example.com   │ 2024-01-15 10:30:00 │
│ 223e4567-e89b-12d3-a456-426614174001 │ bob      │ bob@example.com     │ 2024-01-16 14:22:00 │
│ 323e4567-e89b-12d3-a456-426614174002 │ charlie  │ charlie@example.com │ 2024-01-17 09:15:00 │
└──────────────────────────────────────┴──────────┴─────────────────────┴─────────────────────┘

Total rows: 10,532
Proceed with import? [y/N]:
```

### Column Mapping

```
cqlai> .import /tmp/legacy_users.csv users \
    --mapping "id:user_id,name:username,mail:email"

Column mapping:
  id   → user_id
  name → username
  mail → email
```

## Supported Formats

### CSV

```csv
user_id,username,email,created_at
123e4567-e89b-12d3-a456-426614174000,alice,alice@example.com,2024-01-15T10:30:00Z
223e4567-e89b-12d3-a456-426614174001,bob,bob@example.com,2024-01-16T14:22:00Z
```

### JSON (Array)

```json
[
  {
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "alice",
    "email": "alice@example.com",
    "created_at": "2024-01-15T10:30:00Z"
  },
  {
    "user_id": "223e4567-e89b-12d3-a456-426614174001",
    "username": "bob",
    "email": "bob@example.com"
  }
]
```

### JSON Lines (JSONL)

```json
{"user_id": "123e4567-e89b-12d3-a456-426614174000", "username": "alice", "email": "alice@example.com"}
{"user_id": "223e4567-e89b-12d3-a456-426614174001", "username": "bob", "email": "bob@example.com"}
```

## Data Type Handling

### Automatic Type Conversion

| Source Format | Cassandra Type | Notes |
|---------------|----------------|-------|
| String | uuid | Auto-parsed if valid UUID |
| ISO 8601 | timestamp | `2024-01-15T10:30:00Z` |
| Unix timestamp | timestamp | Milliseconds since epoch |
| true/false | boolean | Case-insensitive |
| JSON array | list | `["a", "b", "c"]` |
| JSON object | map | `{"key": "value"}` |
| Base64 | blob | Auto-detected |

### Complex Types

```csv
# List type
user_id,tags
123...,["admin","active","verified"]

# Map type
user_id,preferences
123...,{"theme": "dark", "notifications": "true"}

# Set type
user_id,roles
123...,["user","moderator"]
```

## Migration Workflows

### Table-to-Table Copy

```
cqlai> .export source_keyspace.users /tmp/users.json --format json
cqlai> USE target_keyspace;
cqlai> .import /tmp/users.json users --format json
```

### Schema Migration

```
# Export schema
cqlai> DESCRIBE KEYSPACE source_ks > /tmp/schema.cql

# Export data
cqlai> .export source_ks.table1 /tmp/table1.csv
cqlai> .export source_ks.table2 /tmp/table2.csv

# Create schema on target
cqlai -h target-host -f /tmp/schema.cql

# Import data
cqlai -h target-host
cqlai> .import /tmp/table1.csv table1
cqlai> .import /tmp/table2.csv table2
```

### Incremental Export

```
cqlai> .export "SELECT * FROM events WHERE event_date = '2024-01-15'" \
    /tmp/events_20240115.csv
```

## Error Handling

### View Import Errors

```
cqlai> .import /tmp/users.csv users --skip-errors --error-log /tmp/errors.log

Import completed with errors:
  Imported: 10,432 rows
  Failed: 100 rows
  Error log: /tmp/errors.log
```

### Error Log Format

```
Line 1523: Invalid UUID format: "not-a-uuid" for column user_id
Line 2891: Type mismatch: expected timestamp, got "invalid-date"
Line 3042: Missing required column: user_id
```

## Performance Tips

1. **Use appropriate batch size** - Default 100, increase for faster imports
2. **Lower consistency for bulk imports** - Use LOCAL_ONE
3. **Compress large exports** - Use `--compress` for network transfer
4. **Use JSONL for streaming** - Better memory efficiency than JSON array
5. **Disable tracing during bulk operations** - Reduces overhead

---

## Next Steps

- **[Features](../features/index.md)** - Full feature reference
- **[AI Features](../ai-features/index.md)** - AI-powered queries
- **[Configuration](../configuration/index.md)** - Advanced settings
