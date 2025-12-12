---
description: "AxonOps monitoring overview. Features for Cassandra and Kafka cluster monitoring."
meta:
  - name: keywords
    content: "monitoring overview, AxonOps monitoring, cluster monitoring"
---

When monitoring enterprise service there are 3 categories of how the service is performing that we generally capture and monitor. These are;

* Performance metrics
* Events (logs)
* Service availability


### Performance Metrics
Performance metrics in Cassandra is highly extensive and there is a large number that can be captured to understand how Cassandra is performing. Another key metrics that also must be captured in order to effectively understand the performance of a database is the system resource utilisation.

AxonOps agent captures both Cassandra and OS metrics and pushes them to the AxonOps server.


### Events
Cassandra event logs are, by default, written to log files. There are important information in the log files that allows SREs and DevOps engineers to identify issues when they occur. AxonOps agent captures the logs and pushes them to the AxonOps server. These logs are visible within AxonOps dashboard allowing quick access to them without having to log in to the individual servers.


### Service Availability
Checking the momentary service availability and dashboards gives confidence that all services are running correctly as expected. Example service checks that allow engineers to gain confidence in the service availability are:

* System process
* Network open ports - e.g. CQL and storage ports
* Database availability - e.g. can execute CQL query



## AxonOps Monitoring
AxonOps implements all three types of monitoring described above. AxonOps agent captures the information, sends them securely to AxonOps server, and the information is stored in the backend data store.

AxonOps GUI provides comprehensive set of metrics dashboards combined with the event log view. It also provides separate service check status view showing the health of the cluster.

This section describes how the AxonOps GUI organises the dashboards of all three types of monitoring.

