---
description: "Deploy Cassandra on Google Cloud Platform. Compute Engine, persistent disks, and VPC setup."
meta:
  - name: keywords
    content: "Cassandra GCP, Google Cloud, Compute Engine, persistent disks"
---

# Cassandra on Google Cloud Platform

This guide covers deploying Apache Cassandra on Google Cloud Platform.

## Instance Types

### Recommended Machine Types

| Use Case | Machine Type | vCPUs | RAM | Notes |
|----------|--------------|-------|-----|-------|
| Development | n2-standard-2 | 2 | 8GB | Testing only |
| Small Prod | n2-highmem-4 | 4 | 32GB | Small workloads |
| Standard Prod | n2-highmem-8 | 8 | 64GB | Recommended |
| High Perf | n2-highmem-16 | 16 | 128GB | Heavy workloads |

### Storage Options

```yaml
# Persistent Disk options
pd-ssd:
  iops: "Read: 15K-100K, Write: 15K-30K"
  throughput: "Read: 240-1200 MB/s"
  use_case: "General production"

pd-extreme:
  iops: "Up to 120K"
  throughput: "Up to 2400 MB/s"
  use_case: "High performance"

# Local SSD (ephemeral)
local-ssd:
  iops: "680K read, 360K write"
  size: "375GB per disk"
  note: "Data lost on maintenance/stop"
```

## Network Configuration

### VPC Setup

```hcl
# Terraform example
resource "google_compute_network" "cassandra" {
  name                    = "cassandra-network"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "cassandra" {
  count         = 3
  name          = "cassandra-subnet-${count.index}"
  ip_cidr_range = "10.0.${count.index}.0/24"
  region        = var.region
  network       = google_compute_network.cassandra.id
}
```

### Firewall Rules

```hcl
resource "google_compute_firewall" "cassandra_internal" {
  name    = "cassandra-internal"
  network = google_compute_network.cassandra.name

  allow {
    protocol = "tcp"
    ports    = ["7000", "7001", "7199", "9042"]
  }

  source_tags = ["cassandra"]
  target_tags = ["cassandra"]
}
```

## Snitch Configuration

### GoogleCloudSnitch

```yaml
# cassandra.yaml
endpoint_snitch: GoogleCloudSnitch

# Automatically detects:
# - DC = project:region (e.g., myproject:us-central1)
# - Rack = zone (e.g., us-central1-a)
```

## Deployment with GKE

```yaml
# Kubernetes StatefulSet
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: cassandra
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
      containers:
      - name: cassandra
        image: cassandra:4.1
        ports:
        - containerPort: 9042
        - containerPort: 7000
        volumeMounts:
        - name: cassandra-data
          mountPath: /var/lib/cassandra
  volumeClaimTemplates:
  - metadata:
      name: cassandra-data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: premium-rwo
      resources:
        requests:
          storage: 500Gi
```

## Multi-Zone Deployment

```
Deploy across 3 zones:

┌──────────────────────────────────────────────┐
│           Region: us-central1                 │
├──────────────┬──────────────┬────────────────┤
│  Zone: 1-a   │  Zone: 1-b   │   Zone: 1-c    │
│  ┌────────┐  │  ┌────────┐  │  ┌────────┐    │
│  │ Node 1 │  │  │ Node 2 │  │  │ Node 3 │    │
│  └────────┘  │  └────────┘  │  └────────┘    │
└──────────────┴──────────────┴────────────────┘
```

---

## Next Steps

- **[Azure Deployment](../azure/index.md)** - Azure guide
- **[Kubernetes](../kubernetes/index.md)** - GKE deployment
