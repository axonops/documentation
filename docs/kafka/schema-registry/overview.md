---
title: "Schema Registry (AxonOps)"
description: "Use AxonOps to connect to your Kafka Schema Registry and browse subjects, versions, and compatibility."
meta:
  - name: keywords
    content: "AxonOps schema registry, Kafka schema registry UI, subjects, compatibility"
---

# Schema Registry (AxonOps)

AxonOps connects to your existing Kafka Schema Registry so you can browse schemas, versions, and compatibility from the AxonOps UI.

## Prerequisites

- A running Kafka Schema Registry service (AxonOps, Confluent, or compatible).
- Network access from the AxonOps agent to the registry endpoint.
- Credentials or tokens if your registry is secured.

## Configure the agent

Enable the schema registry client in the AxonOps agent configuration:

```yaml
kafka:
  schema_registry_client:
    enabled: true
    url: "https://schema-registry.example.com"
    # Use one of the authentication methods below:
    # username: "registry_user"
    # password: "registry_password"
    # bearerToken: "registry_bearer_token"
    # Optional TLS settings
    # tls:
    #   enabled: true
    #   caFilepath: /path/to/ca.pem
    #   insecureSkipTlsVerify: false
```

After saving the file, restart the AxonOps agent so it can connect.

## Use Schema Registry in AxonOps

1. Open **Kafka** in the AxonOps UI.
2. Select **Schema Registry**.
3. Choose the registry/cluster connection.
4. Monitor **metrics** and **logs** for the registry service.
5. Browse **subjects** and open a subject to view schema **versions** and details.
6. Use **Add schema** to register new schema versions.

Depending on your registry implementation and permissions, AxonOps may allow additional actions (such as changing compatibility or deleting versions). If your registry is read-only, AxonOps will still provide visibility into metrics, logs, subjects, and versions.

## Related

- [Schema Registry concepts](../../data-platforms/kafka/schema-registry/index.md)
