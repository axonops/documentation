---
title: "Running AxonOps on Kubernetes"
description: "AxonOps Kubernetes installation. Deploy monitoring in K8s clusters."
meta:
  - name: keywords
    content: "AxonOps Kubernetes, K8s installation, container deployment"
---

# Running AxonOps on Kubernetes

## Introduction

The following shows how to install AxonOps for monitoring cassandra. AxonOps requires ElasticSearch and the documentation below shows how to install both. If you already have ElasticSearch running, you can omit the installation and just ensure the AxonOps config points to it.

AxonOps installation uses Helm Charts. Helm v3.8.0 or later is required in order to access the OCI repository hosting the charts.
The raw charts can be downloaded from the [GitHub repository](https://github.com/axonops/helm-axonops).

## Preparing the configuration

### Resources

| Cassandra Nodes | ElasticSearch CPU | ElasticSearch Memory | AxonOps Server CPU | AxonOps Server Memory |
|-----------------|-------------------|----------------------|--------------------|-----------------------|
| <10             | 1000m             | 4Gi                  | 750m               | 1Gi                   |
| <50             | 1000m             | 4Gi                  | 2000m              | 6Gi                   |
| 100             | 2000m             | 16Gi                 | 4000m              | 12Gi                  |
| 200             | 4000m             | 32Gi                 | 8000m              | 24Gi                  |

### ElasticSearch

The example below is a configuration file for the official [ElasticSearch helm repository](https://artifacthub.io/packages/helm/elastic/elasticsearch). See inline comments:

```yaml
---
clusterName: "axonops-elastic"

replicas: 1

esConfig:
  elasticsearch.yml: |
    thread_pool.write.queue_size: 2000

roles:
  master: "true"
  ingest: "true"
  data: "true"
  remote_cluster_client: "false"
  ml: "false"

# Adjust the memory and cpu requirements to your deployment
# 
esJavaOpts: "-Xms2g -Xmx2g"

resources:
  requests:
    cpu: "750m"
    memory: "2Gi"
  limits:
    cpu: "1500m"
    memory: "4Gi"

volumeClaimTemplate:
  accessModes: ["ReadWriteOnce"]
  storageClassName: "" # adjust to your storageClass if you don't want to use default
  resources:
    requests:
      storage: 50Gi

rbac:
  create: true
```

Save the configuration as `elastic.yaml` and you install it with:

```sh
helm upgrade --install elasticsearch elastic/elasticsearch --create-namespace -n axonops \
  --set secret.password="password" -f elastic.yaml
```

> **_NOTE:_** This example uses as password in plaintext. Check out the helm chart documentation on how to use
secrets and consider using a secrets manager.

### AxonOps

The default AxonOps installation does not expose the services outside of the cluster. We recommend that you use either a LoadBalancer service or an Ingress.

Below you can find an example using `Ingress` to expose both the dashboard and the AxonOps server.

```yaml
axon-dash:
  image:
    pullPolicy: IfNotPresent
    repository: registry.axonops.com/axonops-public/axonops-docker/axon-dash
    tag: latest
  ingress:
    enabled: true
    className: nginx
    annotations:
      external-dns.alpha.kubernetes.io/hostname: axonops.mycompany.com
    hosts:
      - host: axonops.mycompany.com
        path: "/"
    tls:
      - hosts:
          - axonops.mycompany.com
        secretName: axon-dash-tls
  resources:
    limits:
      cpu: 1000m
      memory: 1536Mi
    requests:
      cpu: 25m
      memory: 256Mi

# If you are using an existing ElasticSearch rather than installing it 
# as shown above then make sure you update the elasticHost URL below
axon-server:
  elasticHost: http://username:password@axonops-elastic-master:9200
  dashboardUrl: https://axonops.mycompany.com
  config:
    # Set your organization name here. This must match the name used in your license key
    org_name: demo
    # Enter your AxonOps license key here
    license_key: "..."
  image:
    pullPolicy: IfNotPresent
    repository: registry.axonops.com/axonops-public/axonops-docker/axon-server
    tag: latest
  # Enable the agent ingress to allow agents to connect from outside the Kubernetes cluster
  agentIngress:
    enabled: true
    className: nginx
    annotations:
      external-dns.alpha.kubernetes.io/hostname: axonops-server.mycompany.com
    hosts:
      - host: axonops-server.mycompany.com
        path: "/"
    tls:
      - hosts:
          - axonops-server.mycompany.com
        secretName: axon-server-tls

  resources:
    limits:
      cpu: 1
      memory: 1Gi
    requests:
      cpu: 100m
      memory: 256Mi
```

An example values file showing all available options can be found in the GitHub repository here: [values-full.yaml](https://github.com/axonops/helm-axonops/blob/main/values-full.yaml)


## Installing

### ElasticSearch

Now you can install Elasticsearch referencing the configuration file created in the previous step:

```sh
helm repo add elastic https://helm.elastic.co
helm update
helm upgrade -n axonops --install \
  --create-namespace \
  -f "elasticsearch.yaml" \
  elasticsearch elastic/elasticsearch
```

### AxonOps

Finally install the AxonOps helm chart:

```sh
helm upgrade -n axonops --install \
  --create-namespace \
  -f "axonops.yaml" \
  axonops oci://helm.axonops.com/axonops-public/axonops-helm/axonops
```
