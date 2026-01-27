---
title: "AxonOps Monitoring"
description: "AxonOps monitoring overview. Features for Cassandra and Kafka cluster monitoring."
meta:
  - name: keywords
    content: "monitoring overview, AxonOps monitoring, cluster monitoring"
---

# AxonOps Monitoring

When monitoring an enterprise service, there are three categories we generally capture and monitor:

* Performance metrics
* Events (logs)
* Service availability


### Performance Metrics
Performance metrics in Cassandra are extensive. A key set of metrics for understanding database performance is system resource utilization.

The AxonOps agent captures both Cassandra and OS metrics and pushes them to the AxonOps server.


### Events
Cassandra event logs are written to log files by default. The log files contain information that allows SREs and DevOps engineers to identify issues when they occur. The AxonOps agent captures the logs and pushes them to the AxonOps server. These logs are visible within the AxonOps Dashboard, allowing quick access without logging in to individual servers.


### Service Availability
Checking service availability gives confidence that services are running as expected. Example service checks include:

* System process
* Network open ports - for example, CQL and storage ports
* Database availability - for example, executing a CQL query

AxonOps implements all three types of monitoring described above. The AxonOps agent captures the information, sends it securely to the AxonOps server, and stores it in the backend data store.

The AxonOps Dashboard provides a comprehensive set of metrics dashboards combined with the event log view. It also provides a separate service check status view showing the health of the cluster.

This section describes how the AxonOps GUI organises the dashboards of all three types of monitoring.
