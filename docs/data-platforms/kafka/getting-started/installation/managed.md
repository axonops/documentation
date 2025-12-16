---
title: "Managed Kafka Services"
description: "Managed Apache Kafka services. Cloud provider offerings and selection criteria."
meta:
  - name: keywords
    content: "Managed Kafka, Confluent Cloud, Amazon MSK, Azure Event Hubs, Kafka as a service"
---

# Managed Kafka Services

Managed Kafka services provide Apache Kafka without operational overhead, handling infrastructure, scaling, and maintenance.

---

## Benefits of Managed Services

| Benefit | Description |
|---------|-------------|
| **No operations** | Provider handles upgrades, patches, monitoring |
| **Automatic scaling** | Scale throughput and storage on demand |
| **High availability** | Built-in replication across availability zones |
| **Security** | Managed encryption, authentication, authorization |
| **Cost efficiency** | Pay for what is used, no over-provisioning |

---

## Cloud Provider Services

### AWS MSK (Managed Streaming for Apache Kafka)

Amazon MSK provides fully managed Apache Kafka clusters.

**Features:**

- Apache Kafka compatibility
- Multi-AZ deployment
- Integration with AWS services
- MSK Connect for connectors
- MSK Serverless option

**Configuration:**

```bash
# AWS CLI - Create cluster
aws kafka create-cluster \
  --cluster-name my-kafka-cluster \
  --broker-node-group-info file://broker-config.json \
  --kafka-version 3.5.1 \
  --number-of-broker-nodes 3
```

**Connection:**

```properties
bootstrap.servers=b-1.cluster.region.amazonaws.com:9092,b-2.cluster.region.amazonaws.com:9092
security.protocol=SASL_SSL
sasl.mechanism=AWS_MSK_IAM
sasl.jaas.config=software.amazon.msk.auth.iam.IAMLoginModule required;
sasl.client.callback.handler.class=software.amazon.msk.auth.iam.IAMClientCallbackHandler
```

### Azure Event Hubs for Kafka

Azure Event Hubs provides a Kafka-compatible endpoint.

**Features:**

- Kafka protocol support
- Auto-scaling throughput units
- Integration with Azure services
- Capture to Azure Storage

**Connection:**

```properties
bootstrap.servers=namespace.servicebus.windows.net:9093
security.protocol=SASL_SSL
sasl.mechanism=PLAIN
sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required username="$ConnectionString" password="Endpoint=sb://...";
```

### Google Cloud Managed Service for Apache Kafka

Google Cloud provides managed Kafka clusters.

**Features:**

- Native Apache Kafka
- Integration with GCP services
- VPC connectivity
- Automatic scaling

### Aiven for Apache Kafka

Aiven provides multi-cloud managed Kafka.

**Features:**

- Available on AWS, GCP, Azure
- Apache Kafka with add-ons
- Kafka Connect included
- Schema Registry included

---

## Selection Criteria

| Criteria | Considerations |
|----------|----------------|
| **Cloud provider** | Existing infrastructure, data locality |
| **Kafka compatibility** | Native Kafka vs Kafka-compatible |
| **Throughput** | Peak message rate, burst capacity |
| **Latency** | P99 latency requirements |
| **Features** | Connect, Schema Registry, Streams |
| **Compliance** | Data residency, certifications |
| **Cost** | Per-hour, per-GB, reserved capacity |

---

## Comparison

| Feature | AWS MSK | Azure Event Hubs | GCP Managed Kafka |
|---------|:-------:|:----------------:|:-----------------:|
| Native Kafka | Yes | Kafka protocol | Yes |
| Serverless | Yes | Yes | No |
| Connect | MSK Connect | No | Yes |
| Schema Registry | Glue SR | No | Yes |
| Multi-region | Manual | Geo-DR | Manual |

---

## Migration to Managed

### Planning

1. **Inventory topics and configurations**
2. **Assess client compatibility**
3. **Plan data migration strategy**
4. **Configure networking (VPC, peering)**
5. **Set up authentication/authorization**

### Data Migration

**MirrorMaker 2:**

```properties
# mm2.properties
clusters=source,target
source.bootstrap.servers=old-kafka:9092
target.bootstrap.servers=managed-kafka:9092

source->target.enabled=true
source->target.topics=.*

replication.factor=3
```

```bash
connect-mirror-maker.sh mm2.properties
```

### Client Migration

1. Update bootstrap servers
2. Configure authentication
3. Test connectivity
4. Gradual traffic shift
5. Decommission old cluster

---

## Connectivity

### VPC/Private Connectivity

Most managed services support private networking:

| Provider | Private Access |
|----------|---------------|
| AWS MSK | VPC, PrivateLink |
| Azure | Private Endpoint |
| GCP | Private Service Connect |
| Aiven | VPC Peering, PrivateLink |

### Public Access

For development or when private networking is not required:

```properties
# With TLS and authentication
bootstrap.servers=public-endpoint:9094
security.protocol=SASL_SSL
```

---

## Monitoring

Managed services provide built-in monitoring:

| Provider | Monitoring |
|----------|------------|
| AWS MSK | CloudWatch, Open Monitoring |
| Azure | Azure Monitor |
| GCP | Cloud Monitoring |
| Aiven | Built-in dashboards, integrations |

---

## Cost Optimization

| Strategy | Description |
|----------|-------------|
| **Right-size brokers** | Match instance size to workload |
| **Reserved capacity** | Commit for discounts |
| **Tiered storage** | Offload cold data to object storage |
| **Compression** | Reduce storage and network costs |
| **Retention tuning** | Keep only necessary data |

---

## Related Documentation

- [Installation Overview](index.md) - All installation methods
- [Cloud Deployment](../../cloud/index.md) - Cloud deployment guides
- [Operations](../../operations/index.md) - Operational procedures
