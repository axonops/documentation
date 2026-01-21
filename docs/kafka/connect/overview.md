---
title: "Kafka Connect"
description: "Kafka Connect management in AxonOps. Discover clusters, view connectors, and manage connector lifecycle."
meta:
  - name: keywords
    content: "Kafka Connect, connectors, connector management, AxonOps Kafka"
---

# Kafka Connect

## What is Kafka Connect

Kafka Connect is a framework for moving data between Kafka and external systems using connectors. 
It standardizes ingestion (source connectors) and export (sink connectors) so you can build pipelines without writing custom consumers or producers.

Common uses:
- Load data from databases or SaaS apps into Kafka.
- Stream Kafka topics to data warehouses, object storage, or search systems.
- Keep external systems in sync with Kafka topics.

## Kafka Connect in AxonOps

AxonOps integrates with your Kafka Connect REST endpoints through the agent. 
Once configured, you can:
- Discover Connect clusters and their versions.
- List connectors and view per-connector status.
- Create and update connector configurations.
- Pause, resume, stop, and restart connectors.
- Restart individual connector tasks.

## Configure Kafka Connect access

Enable the Connect client in the agent configuration and define one or more clusters.

### YAML configuration

```yaml
kafka:
  connect_client:
    enabled: true
    connectTimeout: 5s
    readTimeout: 5s
    requestTimeout: 5s
    clusters:
      - name: "connect-prod"
        url: "https://connect.example.com:8083"
        username: "connect_user"
        password: "connect_password"
        tls:
          enabled: true
          caFilepath: "/etc/ssl/certs/ca.pem"
          certFilepath: "/etc/ssl/certs/client.pem"
          keyFilepath: "/etc/ssl/private/client.key"
          insecureSkipTlsVerify: false
```

Notes:
- `clusters` is a list; `name` is used to target a specific Connect cluster.
- `username` and `password` enable HTTP basic auth.
- `token` is supported in config files if your Connect endpoint uses token auth.
- TLS settings are optional; if disabled, TLS 1.2+ is still enforced by the client.

### Environment variables

You can configure a single cluster via environment variables:

```bash
CONNECT_CLIENT_ENABLED=true
CONNECT_CLIENT_CONNECT_TIMEOUT=5s
CONNECT_CLIENT_READ_TIMEOUT=5s
CONNECT_CLIENT_REQUEST_TIMEOUT=5s

CONNECT_CLIENT_CLUSTER_NAME=connect-prod
CONNECT_CLIENT_CLUSTER_URL=https://connect.example.com:8083
CONNECT_CLIENT_CLUSTER_USERNAME=connect_user
CONNECT_CLIENT_CLUSTER_PASSWORD=connect_password

CONNECT_CLIENT_CLUSTER_TLS_ENABLED=true
CONNECT_CLIENT_CLUSTER_TLS_CAFILEPATH=/etc/ssl/certs/ca.pem
CONNECT_CLIENT_CLUSTER_TLS_CERTFILEPATH=/etc/ssl/certs/client.pem
CONNECT_CLIENT_CLUSTER_TLS_KEYFILEPATH=/etc/ssl/private/client.key
CONNECT_CLIENT_CLUSTER_TLS_VERIFY_ENABLED=false
```

Note on TLS verification: `CONNECT_CLIENT_CLUSTER_TLS_VERIFY_ENABLED` maps to the `insecureSkipTlsVerify` field. 
When set to `true`, certificate verification is skipped.

## Cluster discovery and status

Once enabled, AxonOps can fetch:
- Cluster version, commit, and Kafka cluster ID.
- Available connector plugins.
- Connector list and status per cluster.

## Connector lifecycle actions

AxonOps supports the following connector operations:
- Create connector with a full configuration payload.
- Update connector configuration.
- Pause / Resume connector execution.
- Stop connector.
- Restart connector (optionally include tasks or only failed tasks).
- Restart individual connector tasks.

These actions are executed against the Connect REST API through the agent.

## Troubleshooting

If you see no clusters or connectors:
- Confirm `CONNECT_CLIENT_ENABLED=true` (or `connect_client.enabled: true`).
- Verify the `url` is reachable from the agent host.
- Confirm TLS certificates and paths are valid.
- Check credentials if basic auth is required.
