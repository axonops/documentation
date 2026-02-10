---
title: "AxonOps Integration"
description: "Link AxonOps Workbench to AxonOps monitoring dashboards. Deep links to cluster, keyspace, and table views."
meta:
  - name: keywords
    content: "AxonOps integration, monitoring, dashboards, cluster monitoring, AxonOps Workbench"
---

# AxonOps Integration

AxonOps Workbench can link directly to [AxonOps](https://axonops.com){:target="_blank"} monitoring dashboards, giving you one-click access to cluster, keyspace, and table-level metrics from within the workbench. When enabled, an AxonOps tab appears in each connection's work area, embedding the relevant dashboard view right alongside your CQL console.

## What is AxonOps?

AxonOps is a monitoring and management platform purpose-built for Apache Cassandra. It provides real-time metrics, alerting, backup management, and operational insights for your clusters. For full documentation, see the [AxonOps Documentation](https://docs.axonops.com){:target="_blank"}.

The integration in AxonOps Workbench creates deep links between your development environment and your monitoring dashboards, so you can investigate performance characteristics and validate the impact of schema changes without leaving the workbench.

## Enabling the Integration

The AxonOps integration is controlled at two levels: a global toggle in application settings, and per-workspace or per-connection overrides.

### Global Setting

1. Open **Settings** from the navigation sidebar.
2. Under the **Features** section, locate the **AxonOps Integration** checkbox.
3. Enable the checkbox to activate the integration across all workspaces.

<!-- Screenshot: Settings dialog showing the AxonOps Integration checkbox under Features -->

!!! info
    The AxonOps integration is enabled by default. You can disable it globally if your environment does not use AxonOps monitoring.

### Per-Workspace and Per-Connection Control

Even with the global setting enabled, the integration can be toggled on or off for individual workspaces and connections. This allows you to enable monitoring links only for the clusters that are registered with AxonOps.

## Configuring a Connection for AxonOps

Each connection has an **AxonOps** tab in the connection dialog where you provide the details needed to build dashboard links.

<!-- Screenshot: Connection dialog showing the AxonOps configuration tab -->

### Configuration Fields

| Field | Description |
|-------|-------------|
| **AxonOps Organization** | Your organization name in AxonOps. This corresponds to the organization segment in your AxonOps dashboard URL. |
| **AxonOps Cluster Name** | The name of the cluster as registered in AxonOps. This must match exactly. |
| **AxonOps URL** | Choose between **AxonOps Cloud** (the managed SaaS platform) or **AxonOps Self-Host** (your own AxonOps installation). |

### AxonOps URL Options

- **AxonOps Cloud** -- Uses the default AxonOps Cloud endpoint (`https://dash.axonops.cloud`). Select this if you are using the managed AxonOps Cloud platform. The URL is set automatically and cannot be changed.
- **AxonOps Self-Host** -- Allows you to specify a custom URL for your self-hosted AxonOps installation. Enter the protocol (e.g., `https`) and hostname (e.g., `axonops.internal.company.com`) in the provided fields.

### Example Configuration

For a cluster named `production-cluster` in the organization `mycompany` on AxonOps Cloud:

| Field | Value |
|-------|-------|
| AxonOps Organization | `mycompany` |
| AxonOps Cluster Name | `production-cluster` |
| AxonOps URL | AxonOps Cloud |

For a self-hosted AxonOps instance:

| Field | Value |
|-------|-------|
| AxonOps Organization | `mycompany` |
| AxonOps Cluster Name | `staging-cluster` |
| AxonOps URL | AxonOps Self-Host: `https://axonops.internal.company.com` |

## Deep Links

Once configured, AxonOps Workbench generates context-aware deep links that open the appropriate dashboard view. These links are available through the AxonOps integration tab in the connection work area, and through context actions in the schema browser.

### Cluster Overview

Navigate to the overall cluster dashboard showing health, node status, and aggregate metrics.

**URL pattern:**

```
{AxonOps URL}/{ORG}/cassandra/{CLUSTER_NAME}/deeplink/dashboard/cluster
```

### Keyspace-Level Metrics

View metrics scoped to a specific keyspace, including read/write latencies, partition sizes, and table-level breakdowns.

**URL pattern:**

```
{AxonOps URL}/{ORG}/cassandra/{CLUSTER_NAME}/deeplink/dashboard/keyspace?keyspace={KEYSPACE_NAME}&scope=.*
```

### Table-Level Metrics

Drill down to metrics for a specific table within a keyspace, such as SSTable counts, compaction statistics, and per-table latencies.

**URL pattern:**

```
{AxonOps URL}/{ORG}/cassandra/{CLUSTER_NAME}/deeplink/dashboard/keyspace?keyspace={KEYSPACE_NAME}&scope={TABLE_NAME}
```

!!! tip
    Right-click a keyspace or table in the schema browser to access AxonOps deep links directly from the context menu.

## Use Cases

### Investigating Slow Queries

When a query takes longer than expected in the CQL console, switch to the AxonOps integration tab to check read and write latencies for the relevant table. The table-level deep link takes you directly to the metrics dashboard for that specific table, where you can correlate latency spikes with compaction activity or cluster-wide events.

### Verifying Schema Change Impact

After running an `ALTER TABLE` or `CREATE INDEX` statement, use the keyspace-level deep link to monitor the impact on read/write performance and SSTable counts. This helps confirm that the schema change is behaving as expected before rolling it out to other environments.

### Development Clusters with Monitoring

For teams that run AxonOps on their development or staging clusters, the integration provides a seamless workflow: write and test queries in the CQL console, then immediately check how those queries affect cluster metrics -- all within the same application window.

### Comparing Environments

If you maintain connections to multiple clusters (development, staging, production), each with its own AxonOps configuration, you can quickly switch between dashboard views to compare metrics across environments without leaving the workbench.
