---
hide:
  - toc
---

# Firewall Rules

For axon-server, axon-dash, Elasticsearch, and Cassandra Metrics Node to connect together securely, a list of ports need to be included in a rule that will allow traffic through a firewall.

## Firewall Ports and Definitions

<style>
table th:first-of-type {
    width: 20%;
}
table th:nth-of-type(2) {
    width: 1%;
}
table th:nth-of-type(3) {
    width: 15%;
}
</style>

| Destination | Port | Origin | Typical Use |
| ----------- | ---- | ------ | ----------- |
| axon-server | 1888 | axon-agent from Cassandra or Kafka nodes | Inbound agent connections. Server (axon-server) needs to be accessible from the agents (axon-agents) either directly or via an HTTP(s) proxy. |
| axon-server | 8080 | axon-dash | Server's (axon-server) internal port for Web UI (axon-dash) to connect to. |
| axon-dash | 3000 | axon-server and HTTP/S proxy or browser | Web UI (axon-dash) serves HTTP requests on this port. Recomendation is to run a HTTP proxy to secure traffic. |
| Multi-Server setup: Cassandra Metrics Node | 9042 | axon-server | Cassandra's default native client protocol port for CQL (Cassandra Query Language) connections. This is the default port for the server (axon-server) to connect to Cassandra. |
| Multi-Server setup: Elasticsearch Node | 9200 | axon-server | Elasticsearch's default port used for HTTP communication, including client requests, REST API calls, and search queries. |

## Configuration Options for On-Premises Installations

### Single-Server

A single-server AxonOps setup would have the following services installed:

 - axon-server
 - axon-dash
 - Elasticsearch (mandatory)
 - Cassandra Metrics Node (optional)

### Multi-Server

A multi-server AxonOps setup with split roles and responsibilities would look like this:

AxonOps frontend server:

- axon-server
- axon-dash

AxonOps metrics backend server:

- Elasticsearch (mandatory)
- Cassandra Metrics Node (optional)

