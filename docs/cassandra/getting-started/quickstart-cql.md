---
title: "Cassandra CQL Quickstart Guide"
description: "CQL quickstart guide. Learn basic Cassandra Query Language operations."
meta:
  - name: keywords
    content: "CQL quickstart, Cassandra Query Language, CQL basics"
---

# CQL Quickstart Guide

Learn Cassandra Query Language (CQL) fundamentals in this hands-on tutorial. CQL is similar to SQL but designed for Cassandra's distributed architecture.

## Prerequisites

- Cassandra running (see [Installation Guide](installation/index.md))
- Access to `cqlsh` or [CQLAI](../tools/cqlai/index.md)

## Connecting to Cassandra

### Using cqlsh

```bash
# Connect to local Cassandra
cqlsh

# Connect to remote host
cqlsh 192.168.1.10 9042

# Connect with authentication
cqlsh -u cassandra -p cassandra

# Connect with SSL
cqlsh --ssl
```

### Using CQLAI (Recommended)

```bash
# Connect with CQLAI (modern, AI-powered shell)
cqlai

# Connect with specific host
cqlai --host 192.168.1.10
```

## Creating a Keyspace

A **keyspace** is the top-level container for data (similar to a database in SQL).

### Create a Keyspace

```sql
-- For development (single node)
CREATE KEYSPACE IF NOT EXISTS my_app
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};

-- For production (multi-datacenter)
CREATE KEYSPACE IF NOT EXISTS my_app
WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3,
    'dc2': 3
};
```

### Use the Keyspace

```sql
USE my_app;
```

### View Keyspaces

```sql
-- List all keyspaces
DESCRIBE KEYSPACES;

-- Show keyspace details
DESCRIBE KEYSPACE my_app;
```

---

## Creating Tables

### Basic Table

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    username TEXT,
    email TEXT,
    created_at TIMESTAMP
);
```

### Compound Primary Key

```sql
-- Partition key: user_id
-- Clustering column: message_time (sorted DESC)
CREATE TABLE user_messages (
    user_id UUID,
    message_time TIMESTAMP,
    message_id UUID,
    content TEXT,
    PRIMARY KEY ((user_id), message_time, message_id)
) WITH CLUSTERING ORDER BY (message_time DESC);
```

### Composite Partition Key

```sql
-- Composite partition key: (tenant_id, year_month)
CREATE TABLE events (
    tenant_id TEXT,
    year_month TEXT,
    event_time TIMESTAMP,
    event_id UUID,
    event_type TEXT,
    data TEXT,
    PRIMARY KEY ((tenant_id, year_month), event_time, event_id)
) WITH CLUSTERING ORDER BY (event_time DESC);
```

### View Table Structure

```sql
-- Show table schema
DESCRIBE TABLE users;

-- List all tables in keyspace
DESCRIBE TABLES;
```

---

## Inserting Data

### Basic Insert

```sql
INSERT INTO users (user_id, username, email, created_at)
VALUES (uuid(), 'john_doe', 'john@example.com', toTimestamp(now()));
```

### Insert with Specific UUID

```sql
INSERT INTO users (user_id, username, email, created_at)
VALUES (
    550e8400-e29b-41d4-a716-446655440000,
    'jane_smith',
    'jane@example.com',
    '2024-01-15 10:30:00'
);
```

### Insert with TTL (Time To Live)

```sql
-- Data expires after 86400 seconds (24 hours)
INSERT INTO users (user_id, username, email, created_at)
VALUES (uuid(), 'temp_user', 'temp@example.com', toTimestamp(now()))
USING TTL 86400;
```

### Insert If Not Exists (Lightweight Transaction)

```sql
INSERT INTO users (user_id, username, email, created_at)
VALUES (uuid(), 'unique_user', 'unique@example.com', toTimestamp(now()))
IF NOT EXISTS;
```

### Batch Insert

```sql
BEGIN BATCH
    INSERT INTO users (user_id, username, email, created_at)
    VALUES (uuid(), 'user1', 'user1@example.com', toTimestamp(now()));

    INSERT INTO users (user_id, username, email, created_at)
    VALUES (uuid(), 'user2', 'user2@example.com', toTimestamp(now()));

    INSERT INTO users (user_id, username, email, created_at)
    VALUES (uuid(), 'user3', 'user3@example.com', toTimestamp(now()));
APPLY BATCH;
```

---

## Querying Data

### Select All

```sql
SELECT * FROM users;
```

### Select Specific Columns

```sql
SELECT username, email FROM users;
```

### Query by Primary Key

```sql
-- By partition key (efficient)
SELECT * FROM users WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;
```

### Query with Clustering Columns

```sql
-- Get messages for a user, newest first
SELECT * FROM user_messages
WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;

-- Get messages in time range
SELECT * FROM user_messages
WHERE user_id = 550e8400-e29b-41d4-a716-446655440000
  AND message_time >= '2024-01-01'
  AND message_time < '2024-02-01';

-- Limit results
SELECT * FROM user_messages
WHERE user_id = 550e8400-e29b-41d4-a716-446655440000
LIMIT 10;
```

### Query with ALLOW FILTERING (Use Sparingly!)

```sql
-- WARNING: Scans entire table - avoid in production
SELECT * FROM users WHERE email = 'john@example.com' ALLOW FILTERING;
```

> **Warning**: `ALLOW FILTERING` performs a full table scan. Only use for development or very small tables. For production, use proper data modeling or secondary indexes.

### Using IN Clause

```sql
-- Query multiple partition keys
SELECT * FROM users
WHERE user_id IN (
    550e8400-e29b-41d4-a716-446655440000,
    660e8400-e29b-41d4-a716-446655440001
);
```

---

## Updating Data

### Basic Update

```sql
UPDATE users
SET email = 'newemail@example.com'
WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;
```

### Update Multiple Columns

```sql
UPDATE users
SET
    email = 'updated@example.com',
    username = 'updated_username'
WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;
```

### Update with TTL

```sql
UPDATE users USING TTL 3600
SET email = 'temp@example.com'
WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;
```

### Conditional Update (Lightweight Transaction)

```sql
UPDATE users
SET email = 'new@example.com'
WHERE user_id = 550e8400-e29b-41d4-a716-446655440000
IF email = 'old@example.com';
```

---

## Deleting Data

### Delete a Row

```sql
DELETE FROM users
WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;
```

### Delete Specific Columns

```sql
DELETE email FROM users
WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;
```

### Delete with Condition

```sql
DELETE FROM users
WHERE user_id = 550e8400-e29b-41d4-a716-446655440000
IF EXISTS;
```

### Truncate Table

```sql
-- Delete all data from table
TRUNCATE users;
```

---

## Working with Collections

### List Type

```sql
CREATE TABLE user_hobbies (
    user_id UUID PRIMARY KEY,
    hobbies LIST<TEXT>
);

-- Insert list
INSERT INTO user_hobbies (user_id, hobbies)
VALUES (uuid(), ['reading', 'gaming', 'hiking']);

-- Append to list
UPDATE user_hobbies
SET hobbies = hobbies + ['cooking']
WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;

-- Prepend to list
UPDATE user_hobbies
SET hobbies = ['swimming'] + hobbies
WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;

-- Remove from list
UPDATE user_hobbies
SET hobbies = hobbies - ['gaming']
WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;
```

### Set Type

```sql
CREATE TABLE user_tags (
    user_id UUID PRIMARY KEY,
    tags SET<TEXT>
);

-- Insert set
INSERT INTO user_tags (user_id, tags)
VALUES (uuid(), {'premium', 'verified', 'active'});

-- Add to set
UPDATE user_tags
SET tags = tags + {'vip'}
WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;

-- Remove from set
UPDATE user_tags
SET tags = tags - {'active'}
WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;
```

### Map Type

```sql
CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY,
    preferences MAP<TEXT, TEXT>
);

-- Insert map
INSERT INTO user_preferences (user_id, preferences)
VALUES (uuid(), {'theme': 'dark', 'language': 'en', 'timezone': 'UTC'});

-- Update map entries
UPDATE user_preferences
SET preferences['theme'] = 'light'
WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;

-- Add new map entry
UPDATE user_preferences
SET preferences = preferences + {'notifications': 'enabled'}
WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;

-- Remove map entry
DELETE preferences['timezone'] FROM user_preferences
WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;
```

---

## User-Defined Types (UDT)

```sql
-- Create a UDT
CREATE TYPE address (
    street TEXT,
    city TEXT,
    state TEXT,
    zip_code TEXT,
    country TEXT
);

-- Use UDT in table
CREATE TABLE customers (
    customer_id UUID PRIMARY KEY,
    name TEXT,
    billing_address FROZEN<address>,
    shipping_address FROZEN<address>
);

-- Insert with UDT
INSERT INTO customers (customer_id, name, billing_address, shipping_address)
VALUES (
    uuid(),
    'John Doe',
    {street: '123 Main St', city: 'New York', state: 'NY', zip_code: '10001', country: 'USA'},
    {street: '456 Oak Ave', city: 'Boston', state: 'MA', zip_code: '02101', country: 'USA'}
);

-- Query UDT fields
SELECT name, billing_address.city, shipping_address.city FROM customers;
```

---

## Secondary Indexes

### Create Secondary Index

```sql
-- Index on regular column
CREATE INDEX ON users (email);

-- Named index
CREATE INDEX users_email_idx ON users (email);

-- Query using index
SELECT * FROM users WHERE email = 'john@example.com';
```

### Storage-Attached Index (SAI) - Cassandra 5.0+

```sql
-- Create SAI index (more efficient)
CREATE INDEX ON users (email) USING 'sai';

-- SAI with options
CREATE INDEX ON users (username) USING 'sai'
WITH OPTIONS = {'case_sensitive': 'false'};
```

---

## Aggregate Functions

```sql
-- Count rows
SELECT COUNT(*) FROM users;

-- Min/Max (requires primary key or index)
SELECT MIN(created_at), MAX(created_at) FROM user_messages
WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;

-- Sum and Average
CREATE TABLE sales (
    product_id UUID,
    sale_date DATE,
    amount DECIMAL,
    PRIMARY KEY ((product_id), sale_date)
);

SELECT SUM(amount), AVG(amount) FROM sales
WHERE product_id = 550e8400-e29b-41d4-a716-446655440000;
```

---

## Useful Functions

### UUID Functions

```sql
-- Generate random UUID
SELECT uuid();

-- Generate time-based UUID
SELECT now();  -- Returns timeuuid

-- Convert timeuuid to timestamp
SELECT toTimestamp(now());

-- Extract date from timeuuid
SELECT toDate(now());
```

### Timestamp Functions

```sql
-- Current timestamp
SELECT toTimestamp(now());

-- Date from timestamp
SELECT toDate(toTimestamp(now()));

-- Specific timestamp
INSERT INTO users (user_id, username, email, created_at)
VALUES (uuid(), 'user', 'user@example.com', '2024-01-15 14:30:00+0000');
```

### Token Function

```sql
-- Get token value for partition key
SELECT token(user_id), * FROM users;

-- Query token range (useful for debugging)
SELECT * FROM users WHERE token(user_id) > -9223372036854775808;
```

### TTL and WriteTime

```sql
-- Check TTL remaining
SELECT TTL(email) FROM users WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;

-- Check write timestamp
SELECT WRITETIME(email) FROM users WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;
```

---

## Consistency Levels

```sql
-- Set consistency for session
CONSISTENCY QUORUM;

-- Check current consistency
CONSISTENCY;

-- Common consistency levels:
-- ONE        - Fastest, least consistent
-- QUORUM     - Balanced (majority of replicas)
-- LOCAL_QUORUM - Majority in local datacenter
-- ALL        - Slowest, most consistent
```

### Consistency Level Reference

| Level | Description | Use Case |
|-------|-------------|----------|
| `ONE` | One replica responds | High throughput reads |
| `TWO` | Two replicas respond | Improved consistency |
| `THREE` | Three replicas respond | High consistency |
| `QUORUM` | Majority responds | Default for most apps |
| `LOCAL_QUORUM` | Majority in local DC | Multi-DC deployments |
| `EACH_QUORUM` | Quorum in each DC | Strong multi-DC consistency |
| `ALL` | All replicas respond | Highest consistency |
| `ANY` | Any node (including hints) | Highest availability writes |
| `LOCAL_ONE` | One replica in local DC | Low-latency local reads |

---

## Tracing Queries

```sql
-- Enable tracing
TRACING ON;

-- Run query (trace shown automatically)
SELECT * FROM users WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;

-- Disable tracing
TRACING OFF;
```

---

## Practical Examples

### Example 1: User Profile System

```sql
-- Create keyspace
CREATE KEYSPACE social_app WITH replication = {
    'class': 'NetworkTopologyStrategy',
    'dc1': 3
};

USE social_app;

-- User profiles table
CREATE TABLE user_profiles (
    user_id UUID,
    username TEXT,
    display_name TEXT,
    bio TEXT,
    avatar_url TEXT,
    follower_count COUNTER,
    created_at TIMESTAMP,
    PRIMARY KEY (user_id)
);

-- Separate counter table (counters need separate table)
CREATE TABLE user_counters (
    user_id UUID PRIMARY KEY,
    followers COUNTER,
    following COUNTER,
    posts COUNTER
);

-- Update counters
UPDATE user_counters SET followers = followers + 1
WHERE user_id = 550e8400-e29b-41d4-a716-446655440000;
```

### Example 2: Time-Series IoT Data

```sql
-- IoT sensor readings
CREATE TABLE sensor_readings (
    sensor_id TEXT,
    date DATE,
    reading_time TIMESTAMP,
    temperature DOUBLE,
    humidity DOUBLE,
    pressure DOUBLE,
    PRIMARY KEY ((sensor_id, date), reading_time)
) WITH CLUSTERING ORDER BY (reading_time DESC);

-- Insert reading
INSERT INTO sensor_readings (sensor_id, date, reading_time, temperature, humidity, pressure)
VALUES ('sensor-001', '2024-01-15', toTimestamp(now()), 23.5, 65.2, 1013.25);

-- Get today's readings for a sensor
SELECT * FROM sensor_readings
WHERE sensor_id = 'sensor-001'
  AND date = '2024-01-15'
LIMIT 100;

-- Get readings in time range
SELECT * FROM sensor_readings
WHERE sensor_id = 'sensor-001'
  AND date = '2024-01-15'
  AND reading_time >= '2024-01-15 08:00:00'
  AND reading_time < '2024-01-15 17:00:00';
```

### Example 3: E-commerce Orders

```sql
-- Orders by customer
CREATE TABLE orders_by_customer (
    customer_id UUID,
    order_date DATE,
    order_id UUID,
    status TEXT,
    total DECIMAL,
    items LIST<FROZEN<MAP<TEXT, TEXT>>>,
    PRIMARY KEY ((customer_id), order_date, order_id)
) WITH CLUSTERING ORDER BY (order_date DESC, order_id ASC);

-- Insert order
INSERT INTO orders_by_customer (customer_id, order_date, order_id, status, total, items)
VALUES (
    550e8400-e29b-41d4-a716-446655440000,
    '2024-01-15',
    uuid(),
    'pending',
    99.99,
    [
        {'product_id': 'prod-001', 'name': 'Widget', 'quantity': '2', 'price': '49.99'},
        {'product_id': 'prod-002', 'name': 'Gadget', 'quantity': '1', 'price': '0.01'}
    ]
);

-- Get customer's recent orders
SELECT * FROM orders_by_customer
WHERE customer_id = 550e8400-e29b-41d4-a716-446655440000
LIMIT 10;
```

---

## Common Mistakes to Avoid

### 1. Using ALLOW FILTERING in Production

```sql
-- BAD: Full table scan
SELECT * FROM users WHERE email = 'john@example.com' ALLOW FILTERING;

-- GOOD: Create an index or denormalize
CREATE INDEX ON users (email);
SELECT * FROM users WHERE email = 'john@example.com';
```

### 2. Large Partitions

```sql
-- BAD: All orders in one partition (unbounded growth)
CREATE TABLE orders (
    order_id UUID PRIMARY KEY,
    customer_id UUID,
    ...
);

-- GOOD: Partition by customer with time bucketing
CREATE TABLE orders_by_customer (
    customer_id UUID,
    year_month TEXT,  -- e.g., '2024-01'
    order_id UUID,
    ...
    PRIMARY KEY ((customer_id, year_month), order_id)
);
```

### 3. Using Collections for Large Data

```sql
-- BAD: Collections have 64KB limit per element
CREATE TABLE user_posts (
    user_id UUID PRIMARY KEY,
    posts LIST<TEXT>  -- Will fail with many/large posts
);

-- GOOD: Use a separate table
CREATE TABLE posts_by_user (
    user_id UUID,
    post_time TIMESTAMP,
    post_id UUID,
    content TEXT,
    PRIMARY KEY ((user_id), post_time, post_id)
);
```

---

## Next Steps

After learning CQL basics:

1. **[Data Modeling Guide](../data-modeling/index.md)** - Design effective schemas
2. **[First Cluster Setup](first-cluster.md)** - Multi-node deployment
3. **[CQL Reference](../cql/index.md)** - Complete language reference
4. **[Install CQLAI](../tools/cqlai/installation/index.md)** - Modern CQL shell with AI
