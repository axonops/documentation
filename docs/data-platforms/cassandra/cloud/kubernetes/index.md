---
title: "Cassandra on Kubernetes"
description: "Deploy Apache Cassandra on Kubernetes using StatefulSets and operators. Container configuration, persistent volumes, scaling, and production best practices."
meta:
  - name: keywords
    content: "Cassandra Kubernetes, K8s deployment, StatefulSet, operators"
---

# Cassandra on Kubernetes

This guide covers deploying Apache Cassandra on Kubernetes using StatefulSets and operators.

## Deployment Options

| Option | Complexity | Features | Best For |
|--------|------------|----------|----------|
| StatefulSet | Medium | Basic orchestration | Simple deployments |
| K8ssandra | Low | Full-featured operator | Production |
| Cass-operator | Medium | DataStax operator | Enterprise |
| Custom Helm | Medium | Flexible | Custom requirements |

## StatefulSet Deployment

### Basic StatefulSet

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: cassandra
  labels:
    app: cassandra
spec:
  serviceName: cassandra
  replicas: 3
  selector:
    matchLabels:
      app: cassandra
  template:
    metadata:
      labels:
        app: cassandra
    spec:
      terminationGracePeriodSeconds: 1800
      containers:
      - name: cassandra
        image: cassandra:4.1
        ports:
        - containerPort: 7000
          name: intra-node
        - containerPort: 7001
          name: tls-intra-node
        - containerPort: 7199
          name: jmx
        - containerPort: 9042
          name: cql
        resources:
          limits:
            cpu: "2"
            memory: 4Gi
          requests:
            cpu: "1"
            memory: 2Gi
        securityContext:
          capabilities:
            add:
              - IPC_LOCK
        lifecycle:
          preStop:
            exec:
              command:
              - /bin/sh
              - -c
              - nodetool drain
        env:
          - name: MAX_HEAP_SIZE
            value: 1G
          - name: HEAP_NEWSIZE
            value: 256M
          - name: CASSANDRA_SEEDS
            value: "cassandra-0.cassandra.default.svc.cluster.local"
          - name: CASSANDRA_CLUSTER_NAME
            value: "K8sCluster"
          - name: CASSANDRA_DC
            value: "DC1"
          - name: CASSANDRA_RACK
            value: "Rack1"
          - name: POD_IP
            valueFrom:
              fieldRef:
                fieldPath: status.podIP
        readinessProbe:
          exec:
            command:
            - /bin/bash
            - -c
            - /ready-probe.sh
          initialDelaySeconds: 15
          timeoutSeconds: 5
        volumeMounts:
        - name: cassandra-data
          mountPath: /var/lib/cassandra
  volumeClaimTemplates:
  - metadata:
      name: cassandra-data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: fast
      resources:
        requests:
          storage: 100Gi
```

### Headless Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: cassandra
  labels:
    app: cassandra
spec:
  ports:
  - port: 9042
    name: cql
  clusterIP: None
  selector:
    app: cassandra
```

### Client Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: cassandra-client
  labels:
    app: cassandra
spec:
  ports:
  - port: 9042
    name: cql
  selector:
    app: cassandra
```

## K8ssandra Operator

### Installation

```bash
# Add Helm repository
helm repo add k8ssandra https://helm.k8ssandra.io/stable
helm repo update

# Install operator
helm install k8ssandra-operator k8ssandra/k8ssandra-operator -n k8ssandra-operator --create-namespace
```

## AxonOps K8ssandra Integration

AxonOps provides production-ready container images that combine Apache Cassandra with K8ssandra Management API and AxonOps monitoring, optimized for Kubernetes deployments.

### Components

| Component | Description |
|-----------|-------------|
| Apache Cassandra 5.0.x | Database engine (versions 5.0.1 – 5.0.6) |
| K8ssandra Management API | Operational control interface |
| AxonOps Agent | Monitoring and management integration |
| cqlai | Modern CQL shell |
| jemalloc | Optimized memory allocator |

### Image Versioning

Images use a three-component versioning scheme for full immutability:

```
{CASSANDRA}-v{K8SSANDRA_API}-{AXONOPS}
```

Example: `5.0.6-v0.1.110-1.0.0`

!!! warning "Production Deployments"
    Pin to specific immutable versions rather than floating `latest` tags. Digest-based references provide cryptographic guarantees against supply chain attacks.

### Required Configuration

| Variable | Description |
|----------|-------------|
| `AXON_AGENT_KEY` | AxonOps API authentication key |
| `AXON_AGENT_ORG` | Organization identifier |
| `AXON_AGENT_HOST` | Server endpoint (default: `agents.axonops.cloud`) |

### Quick Start

1. Install K8ssandra Operator using the provided script
2. Configure AxonOps credentials as environment variables
3. Deploy using the example cluster configuration

### Documentation and Examples

For detailed deployment instructions, configuration options, and production best practices:

**Repository**: [github.com/axonops/axonops-containers/tree/development/k8ssandra](https://github.com/axonops/axonops-containers/tree/development/k8ssandra)

The repository includes:

- Installation scripts for K8ssandra Operator
- Example cluster configurations
- CI/CD workflows for building custom images
- Security scanning and verification procedures

### K8ssandraCluster Resource

```yaml
apiVersion: k8ssandra.io/v1alpha1
kind: K8ssandraCluster
metadata:
  name: production-cluster
spec:
  cassandra:
    serverVersion: "4.1.3"
    datacenters:
      - metadata:
          name: dc1
        size: 3
        storageConfig:
          cassandraDataVolumeClaimSpec:
            storageClassName: fast
            accessModes:
              - ReadWriteOnce
            resources:
              requests:
                storage: 500Gi
        config:
          jvmOptions:
            heapSize: 8G
        resources:
          requests:
            cpu: 2
            memory: 16Gi
          limits:
            cpu: 4
            memory: 16Gi
  stargate:
    size: 2
  reaper:
    autoScheduling:
      enabled: true
  medusa:
    storageProperties:
      storageProvider: s3
      bucketName: cassandra-backups
```

## Storage Configuration

### Storage Classes

```yaml
# AWS EBS
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast
provisioner: ebs.csi.aws.com
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true

---
# GCP
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast
provisioner: pd.csi.storage.gke.io
parameters:
  type: pd-ssd
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true

---
# Azure
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast
provisioner: disk.csi.azure.com
parameters:
  skuName: Premium_LRS
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

## Pod Disruption Budget

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: cassandra-pdb
spec:
  maxUnavailable: 1
  selector:
    matchLabels:
      app: cassandra
```

## Anti-Affinity Rules

```yaml
spec:
  template:
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - cassandra
            topologyKey: kubernetes.io/hostname
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - cassandra
              topologyKey: topology.kubernetes.io/zone
```

## Scaling

### Scale Up

```bash
# Scale StatefulSet
kubectl scale statefulset cassandra --replicas=5

# Or edit the resource
kubectl edit statefulset cassandra
```

### Scale Down

```bash
# Decommission node first
kubectl exec cassandra-4 -- nodetool decommission

# Wait for streaming to complete
kubectl exec cassandra-4 -- nodetool netstats

# Then scale down
kubectl scale statefulset cassandra --replicas=4
```

## Monitoring

### Prometheus Integration

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: cassandra
spec:
  selector:
    matchLabels:
      app: cassandra
  endpoints:
  - port: metrics
    interval: 15s
```

## Best Practices

### Resource Management

```yaml
resources:
  requests:
    cpu: "2"
    memory: "8Gi"
  limits:
    cpu: "4"
    memory: "8Gi"  # Same as request for predictable performance
```

### Health Checks

```yaml
readinessProbe:
  exec:
    command:
    - /bin/bash
    - -c
    - "nodetool status | grep -E '^UN\\s+${POD_IP}'"
  initialDelaySeconds: 90
  periodSeconds: 30
  timeoutSeconds: 10

livenessProbe:
  exec:
    command:
    - /bin/bash
    - -c
    - "nodetool info"
  initialDelaySeconds: 120
  periodSeconds: 30
  timeoutSeconds: 10
```

---

## Next Steps

- **[AWS Deployment](../aws/index.md)** - EKS specifics
- **[GCP Deployment](../gcp/index.md)** - GKE specifics
- **[Operations](../../operations/index.md)** - Kubernetes operations