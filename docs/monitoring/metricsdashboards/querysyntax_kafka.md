---
title: "AxonOps Query Language Documentation"
description: "AxonOps query syntax for Kafka metrics. Build custom queries and dashboards."
meta:
  - name: keywords
    content: "query syntax, Kafka metrics, custom queries, AxonOps"
search:
  boost: 8
---

# AxonOps Query Language Documentation

AxonOps uses a powerful query language for dashboarding performance metrics collected from the AxonOps agent. This language is largely based on the Prometheus query language, allowing users familiar with Prometheus to quickly adapt to AxonOps. For a comprehensive guide on the Prometheus query language, please refer to the [Prometheus Query Language documentation](https://prometheus.io/docs/prometheus/latest/querying/basics/){target="_blank"}

## Key Difference in AxonOps Query Language

While most of the AxonOps query language is identical to Prometheus, there is a notable difference in the handling of the `rate` function, specifically for metrics of the "Count" type. AxonOps has implemented an optimized method for generating rate graphs for these metrics at the source in the agent. This method ensures accurate rated metrics, as well as faster query time for the rated metrics when compared to dynamically calculating at query time.

## Querying Rated Metrics

To query rated metrics in AxonOps, you need to use a specific syntax that includes embedding the `axonfunction='rate'` label within the query. This informs the AxonOps agent to generate the rated values for the Count metrics data at source. The following is an example of how to structure such a query:

### Example Query

```promql
sum(kaf_BrokerTopicMetrics_MessagesInPerSec{axonfunction='rate',rack=~'$rack',host_id=~'$host_id',topic=~'$topic'}) by (host_id)
```

### Explanation of the Query

- `sum()`: adds up the values returned by the metric 
- `kaf_BrokerTopicMetrics_MessagesInPerSec`: The specific metric being queried.
- `{axonfunction='rate', ...}`: The curly braces set the includes for e.g. `axonfunction='rate'`, which instructs the AxonOps agent to generate the rated values.
    - `axonfunction='rate'`: This label indicates that the agent should compute rate values.
    - `dc=~'$dc'`, `rack=~'$rack'`, `host_id=~'$host_id'`, `topic=~'$topic'`: Additional labels that allow filtering by data center, rack, host ID and topic using regular expressions.
- `by (host_id)`: groups the metric query by host_id. can be grouped by host–id,topic,rack or dc.

### Parameters

- **`axonfunction='rate'`**: Tells the AxonOps agent to generate rated values for Count metrics.
- **`dc`**: Filters metrics by data center.
- **`rack`**: Filters metrics by rack.
- **`host_id`**: Filters metrics by host ID.
- **`topic`**: A Topic Name



