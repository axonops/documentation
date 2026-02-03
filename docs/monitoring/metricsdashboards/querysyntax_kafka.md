---
title: "AxonOps Query Language Documentation"
description: "AxonOps query syntax for Kafka metrics. Build custom queries and dashboards."
meta:
  - name: keywords
    content: "query syntax, Kafka metrics, custom queries, AxonOps"
---

# AxonOps Query Language Documentation

AxonOps uses a powerful query language for dashboarding performance metrics collected from axon-agent. This language is largely based on the Prometheus query language, allowing users familiar with Prometheus to quickly adapt to AxonOps. For a comprehensive guide on the Prometheus query language, please refer to the [Prometheus Query Language documentation](https://prometheus.io/docs/prometheus/latest/querying/basics/){target="_blank"}

## Key Difference in AxonOps Query Language

While most of the AxonOps query language is identical to Prometheus, there is a notable difference in the handling of the `rate` function for metrics of the `Count` type. AxonOps generates rate values at the agent, which improves accuracy and reduces query time compared to computing rates at query time.

## Querying Rated Metrics

To query rate metrics in AxonOps, include the `axonfunction='rate'` label in the query. This tells the agent to generate rate values for `Count` metrics at source. The following is an example of how to structure such a query:

### Example Query

```promql
sum(kaf_BrokerTopicMetrics_MessagesInPerSec{axonfunction='rate',dc=~'$dc',rack=~'$rack',host_id=~'$host_id',topic=~'$topic'}) by (host_id)
```

### Explanation of the Query

- `sum()`: adds up the values returned by the metric 
- `kaf_BrokerTopicMetrics_MessagesInPerSec`: The specific metric being queried.
- `{axonfunction='rate', ...}`: Label matchers (for example, `axonfunction='rate'`) instruct axon-agent to generate rate values.
    - `axonfunction='rate'`: This label indicates that the agent should compute rate values.
    - `dc=~'$dc'`, `rack=~'$rack'`, `host_id=~'$host_id'`, `topic=~'$topic'`: Additional labels that allow filtering by data center, rack, host ID and topic using regular expressions.
- `by (host_id)`: groups the metric query by host_id. You can group by `host_id`, `topic`, `rack`, or `dc`.

### Parameters

- **`axonfunction='rate'`**: Tells axon-agent to generate rated values for Count metrics.
- **`dc`**: Filters metrics by data center.
- **`rack`**: Filters metrics by rack.
- **`host_id`**: Filters metrics by host ID.
- **`topic`**: A Topic Name
