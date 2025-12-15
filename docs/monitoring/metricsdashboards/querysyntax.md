---
title: "AxonOps Query Language Documentation"
description: "AxonOps query syntax for Cassandra metrics. Build custom queries and dashboards."
meta:
  - name: keywords
    content: "query syntax, Cassandra metrics, custom queries, AxonOps"
---

# AxonOps Query Language Documentation

AxonOps uses a powerful query language for dashboarding performance metrics collected from the AxonOps agent. This language is largely based on the Prometheus query language, allowing users familiar with Prometheus to quickly adapt to AxonOps. For a comprehensive guide on the Prometheus query language, please refer to the [Prometheus Query Language documentation](https://prometheus.io/docs/prometheus/latest/querying/basics/){target="_blank"}

## Key Difference in AxonOps Query Language

While most of the AxonOps query language is identical to Prometheus, there is a notable difference in the handling of the `rate` function, specifically for metrics of the "Count" type. AxonOps has implemented an optimized method for generating rate graphs for these metrics at the source in the agent. This method ensures accurate rated metrics, as well as faster query time for the rated metrics when compared to dynamically calculating at query time.

## Querying Rated Metrics

To query rated metrics in AxonOps, you need to use a specific syntax that includes embedding the `axonfunction='rate'` label within the query. This informs the AxonOps agent to generate the rated values for the Count metrics data at source. The following is an example of how to structure such a query:

### Example Query

```promql
cas_ClientRequest_Latency{axonfunction='rate',scope='Write_*$consistency',function='Count',dc=~'$dc',rack=~'$rack',host_id=~'$host_id'}
```

### Explanation of the Query

- `cas_ClientRequest_Latency`: The specific metric being queried.
- `{axonfunction='rate', ...}`: The label set that includes `axonfunction='rate'`, which instructs the AxonOps agent to generate the rated values.
  - `axonfunction='rate'`: This label indicates that the agent should compute rate values.
  - `scope='Write_*$consistency'`: A scope pattern that matches the relevant metrics.
  - `function='Count'`: Specifies that the metric type is Count.
  - `dc=~'$dc'`, `rack=~'$rack'`, `host_id=~'$host_id'`: Additional labels that allow filtering by data center, rack, and host ID using regular expressions.

### Parameters

- **`axonfunction='rate'`**: Tells the AxonOps agent to generate rated values for Count metrics.
- **`scope`**: A pattern for filtering the scope of the query.
- **`function`**: Specifies the metric type, which should be "Count" for rated metrics.
- **`dc`**: Filters metrics by data center.
- **`rack`**: Filters metrics by rack.
- **`host_id`**: Filters metrics by host ID.



