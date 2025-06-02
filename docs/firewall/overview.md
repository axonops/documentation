---
hide:
  - toc
---

# Firewall Rules

For axon-server, axon-dash, Elasticsearch and Cassandra for Metrics to connect securely a list of ports need to be included in a rule that will allow traffic through a firewall.

## Firewall ports and definitions

| Port        | Typical Use                                                              | Origin  | Destination |
| ----------- | ------------------------------------------------------------------------ | ----------------- | ----------------- |
| 1888 | Inbound agent connections, needs to be accessible from the agents either directly or via an HTTP(s) proxy | axon-agent on Cassandra or Kafka | axon-server |
| 3000 | Web UI (axon-dash) HTTP only, recomendation is to run a HTTP proxy to secure traffic | HTTP/S proxy or browser | axon-dash |
| 8080 | axon-server internal port for axon-dash to connect to | axon-dash | axon-server |
| 9042 | Cassandra (Default), Native client protocol port for CQL (Cassandra Query Language) connections; this is the default port for axon-server applications connecting to Cassandra | axon-server | Option 2 : Cassandra Metrics Node |
| 9200 | Elasticsearch (Default), Used for HTTP communication, including client requests, REST API calls, and search queries. | axon-server | Option 2 : Elasticsearch Node |

## Configuration Options for on-premises installations 

### Option 1:

 AxonOps setup with single server that has the following services installed:

 - axon-server
 - axon-dash
 - Elasticsearch (mandatory)
 - Cassandra for Metrics (optional)

### Option 2:

AxonOps setup with split roles and responsibilities:

AxonOps Frontend:

- axon-server
- axon-dash

AxonOps Metrics Backend:

- Elasticsearch (mandatory)
- Cassandra for Metrics (optional)

