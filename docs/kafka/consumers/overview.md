# Kafka Consumers

## What is a Consumer

Kafka consumers are client applications that read (consume) messages from Kafka topics. 
They are fundamental for retrieving and processing data from a Kafka cluster. 
Consumers connect to Kafka brokers, subscribe to one or more topics, and continuously poll for new messages to process.

### How Consumers Work:

A consumer subscribes to one or more topics and fetches messages from assigned partitions.

Kafka tracks the offset (position) of each message consumed, enabling consumers to resume from where they left off in case of restarts or failures.

Multiple consumers can be grouped into a consumer group. 
Each consumer in a group is assigned a subset of partitions, allowing for parallel processing and scaling. 
No two consumers in the same group will read the same partition at the same time.

Multiple consumer groups can independently consume the same data from a topic, supporting different applications or processing pipelines.

### Example Use Cases

- Real-time analytics
- Event-driven microservices
- Data ingestion pipelines

### Key Configuration Tips:

- Use a unique `group.id` for each logical application or processing pipeline.

- Decide between automatic (`enable.auto.commit=true`) and manual offset commits depending on your need for processing guarantees.

- Adjust `max.poll.records` and `max.poll.interval.ms` based on your message processing time and throughput needs.

- Set up security parameters (security.protocol, SSL/SASL configs) if your Kafka cluster requires authentication or encryption

### View consumer List and Consumer Metrics

#### Click Consumer in the Left Navigation

Navigate to the Consumers Section

<img src="/kafka/consumers/consumer_click.png" width="700">

#### Click any of the Consumers in the list

<img src="/kafka/consumers/consumer_overview.png" width="700">

#### Partitions and Consumer Overview

<img src="/kafka/consumers/consumer_metrics.png" width="700">
