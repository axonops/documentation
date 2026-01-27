---
title: "Set up Log Collection"
description: "Configure log collection in AxonOps. Aggregate and search Cassandra and Kafka logs."
meta:
  - name: keywords
    content: "log collection, AxonOps logs, log aggregation, search logs"
---

# Set up Log Collection

AxonOps dashboards provide a comprehensive set of charts with an embedded view for logs and events. You can correlate metrics with logs/events by zooming in on the logs histogram or metrics charts to drill down on both.

The log and event view is located at the bottom of the page and can be expanded/collapsed with the horizontal splitter.


![dashboard](./dashboard.JPG)

The setup for log collection is accessible via **Settings > Logs**.



![log_1](./log_1.JPG)

**newlineregex** is used by the log collector to handle multiline logs. The default **newlineregex** for Cassandra is usually sufficient unless you've customized the format.
