# Running AxonOps on Kubernetes

## Introduction

The following shows how to install AxonOps for monitoring cassandra. AxonOps requires ElasticSearch and the documentation below shows how to install both. If you already have ElasticSearch running, you can omit the installation and just ensure the AxonOps config points to it.

AxonOps installation uses Helm Charts.

## Preparing the configuration

### Resources

| Cassandra Nodes  | ElasticSearch CPU  | ElasticSearch Memory | AxonOps Server CPU | AxonOps Server Memory |
|---|---|---|---|---|
| <10  | 1000m | 4Gi | 500m | 1Gi |
| <50  | 1000m | 4Gi | 1000m | 2Gi |
| 100  | 2000m | 16Gi | 2000m | 8Gi |
| 200  | 4000m | 32Gi | 4000m | 16Gi |

### ElasticSearch

The example below is a configuration file for the official ElasticSearch helm repository. See inline comments:

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


### AxonOps

The default AxonOps installation does not expose the services outside of the cluster. We recommend that you use either a LoadBalancer service or an Ingress.

Below you can find an example using `Ingress` to expose both the dashboard and the AxonOps server.

```yaml
axon-dash:
  config:
    axonServerUrl: http://axonops-axon-server:8080
  image:
    pullPolicy: IfNotPresent
    repository: registry.axonops.com/axonops-public/axonops-docker/axon-dash
    tag: 1.0.13
  ingress:
    enabled: true
    annotations:
      external-dns.alpha.kubernetes.io/hostname: axonops.mycompany.com
    hosts:
      - host: axonops.mycompany.com
        paths:
          - /
    tls:
      - hosts:
          - axonops.mycompany.com
        secretName: axon-dash-tls
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 25m
      memory: 64Mi

# If you are using an existing ElasticSearch rather than installing it 
# as shown here then make sure you update the elasticHost URL below
axon-server:
  elasticHost: http://axonops-elastic-master:9200
  dashboardUrl: https://axonops.mycompany.com
  config:
    # Set up your organization name here
    org_name: demo
  image:
    pullPolicy: IfNotPresent
    repository: registry.axonops.com/axonops-public/axonops-docker/axon-server
    tag: 1.0.40
  ingress:
    enabled: true
    annotations:
      external-dns.alpha.kubernetes.io/hostname: axonops-server.mycompany.com
    hosts:
      - host: axonops-server.mycompany.com
        paths:
          - /
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
  serviceAccount:
    create: true
```

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
