# Running AxonOps on Kubernetes

## Introduction

The following shows how to install AxonOps for monitoring cassandra. AxonOps requires ElasticSearch and the documentation below shows how to install both. If you already have ElasticSearch running, you can omit the installation and just ensure the AxonOps config points to it.

AxonOps installation uses Helm Charts.

## Adding the helm repositories

To follow this guide, you need two helm repositories: AxonOps and Elastic. You can add them using the commands:

```sh
helm repo add axonops https://repo.axonops.com/public/helm/helm/charts/
helm repo add elastic https://helm.elastic.co
helm update
```

## Preparing the configuration

### Resources

| Cassandra Nodes  | ElasticSearch CPU  | ElasticSearch Memory | AxonOps Server CPU | AxonOps Server Memory |
|---|---|---|---|---|
| <50  | 1000m | 4Gbi | 1000m | 2Gi |
| 100  | 2000m | 16Gbi | 2000m | 8Gi |
| 200  | 4000m | 64Gbi | 4000m | 24Gi |

### ElasticSearch

The example below is a configuration file for the official ElasticSearch helm repository. See inline comments:

```yaml
---
clusterName: "axonops-elastic"

replicas: 3

esConfig:
  elasticsearch.yml: |
    thread_pool.write.queue_size: 2000

# Adjust the memory and cpu requirements to your deployment
# 
esJavaOpts: "-Xms10g -Xmx10g"

resources:
  requests:
    cpu: "750m"
    memory: "5Gi"
  limits:
    cpu: "2000m"
    memory: "12Gi"

volumeClaimTemplate:
  accessModes: ["ReadWriteOnce"]
  storageClassName: "gp2"
  resources:
    requests:
      storage: 50Gi

rbac:
  create: true
  serviceAccountAnnotations: {}
  serviceAccountName: ""
  automountToken: true
```


### AxonOps

AxonOps installation will work with default settings fine for most people. Below you can find a more complex example using `Ingress` to expose both
the dashboard and the AxonOps server.

```yaml
axon-dash:
  autoscaling:
    enabled: "true"
    maxReplicas: "2"
    minReplicas: "1"
    targetCPUUtilizationPercentage: "75"
  config:
    axonServerUrl: http://axonops-axon-server:8080
  image:
    pullPolicy: IfNotPresent
    repository: docker.cloudsmith.io/axonops/axonops-private/axon-dash
    tag: 1.0.2
  imagePullSecrets:
    - axonops-registry
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
    org_name: demo
    auth:
      enabled: false
  image:
    pullPolicy: IfNotPresent
    repository: docker.cloudsmith.io/axonops/axonops-private/axon-server
    tag: 1.0.4
  imagePullSecrets:
    - axonops-registry
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
      cpu: 2
      memory: 4Gi
    requests:
      cpu: 100m
      memory: 1Gi
  serviceAccount:
    create: true
    createClusterRole: false
```

## Installing

### ElasticSearch

Now you can install Elasticsearch referencing the configuration file created in the previous step:

```sh
helm upgrade -n axonops --install \
  --create-namespace \
  -f "elasticsearch.yaml" \
  elasticsearch elastic/elasticsearch
```

### AxonOps

Before you can install AxonOps you will need access the the private container repository and to create the required secret.

```sh
kubectl create secret docker-registry \
  -n axonops \
  axonops-registry \
  --docker-username=axonops/axonops-private \
  --docker-password=XXXXXXXXXXX
```

And finally install the AxonOps helm chart:

```sh
helm upgrade -n axonops --install \
  --create-namespace \
  -f "axonops.yaml" \
  axonops axonops/axonops
```
