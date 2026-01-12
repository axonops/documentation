---
title: Deploying AxonOps on Kubernetes
description: Complete guide to deploying AxonOps components on Kubernetes with cert-manager and storage configuration
---

# Deploying AxonOps on Kubernetes

This guide explains how to deploy AxonOps components and a Strimzi Kafka cluster on Kubernetes with local (hostPath) storage or shared storage and AxonOps monitoring agent integration.

## Components Required

- **AxonOps Server** - Core management server
- **AxonOps Dashboard** - Web UI
- **AxonOps Timeseries DB** - Metrics storage (Cassandra-based)
- **AxonOps Search DB** - Log and event storage (OpenSearch-based)
- **cert-manager** (Recommended) - Automatic TLS certificate management

## AxonOps Infrastructure Setup

### Cert Manager

Install cert-manager for automatic TLS certificate management:

```bash
helm upgrade --install \
  cert-manager oci://quay.io/jetstack/charts/cert-manager \
  --version v1.19.1 \
  --namespace cert-manager \
  --create-namespace \
  --set crds.enabled=true
```

Create a self-signed cluster issuer if you do not have another issuer to use:

```bash
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: selfsigned-cluster-issuer
spec:
  selfSigned: {}
EOF
```

### AxonOps Timeseries DB

Create the data directories on the host (user ID 999):

```bash
mkdir -p /data/axon-timeseries
chown -R 999:999 /data/axon-timeseries
```

Create `timeseries-values.yaml`:

```yaml
# Optional: Increase heap size for better performance
heapSize: 8192M

# TLS/SSL Configuration
tls:
  # Enable TLS/SSL for Cassandra
  enabled: true
  # cert-manager configuration for automatic certificate management
  certManager:
    # Enable cert-manager for certificate provisioning
    enabled: true
    issuer:
      name: selfsigned-cluster-issuer

persistence:
  enabled: false # Disable PVC-based persistence

# Define hostPath volumes using extraVolumes
extraVolumes:
  - name: timeseries-data
    hostPath:
      path: /data/axon-timeseries # Host directory path
      type: DirectoryOrCreate # Creates directory if it doesn't exist

# Mount the hostPath volumes (do not change the paths)
extraVolumeMounts:
  - name: timeseries-data
    mountPath: /var/lib/cassandra

# Optional: Set resource limits
resources:
  requests:
    cpu: 1001m
    memory: 2Gi
  limits:
    cpu: 2000m
    memory: 4Gi
```

Install:

```bash
helm install axondb-timeseries oci://ghcr.io/axonops/charts/axondb-timeseries \
  --namespace axonops \
  --create-namespace \
  -f timeseries-values.yaml
```

### AxonOps Search DB

Create the data directory on the host:

```bash
mkdir -p /data/axon-search
chown -R 999:999 /data/axon-search
```

Create `search-values.yaml`:

```yaml
# Large set up may need higher Heap Size
opensearchHeapSize: "8g"

persistence:
  enabled: false

# Define hostPath volumes using extraVolumes
extraVolumes:
  - name: data
    hostPath:
      path: /data/axon-search
      type: DirectoryOrCreate # Creates directory if it doesn't exist

# Mount the hostPath volumes (do not change the paths)
extraVolumeMounts:
  - name: data
    mountPath: /var/lib/opensearch

# TLS/SSL Configuration
tls:
  # Enable TLS/SSL
  enabled: true
  # cert-manager configuration for automatic certificate management
  certManager:
    # Enable cert-manager for certificate provisioning
    enabled: true
    issuer:
      name: selfsigned-cluster-issuer
```

Install:

```bash
helm install axondb-search oci://ghcr.io/axonops/charts/axondb-search \
  --namespace axonops \
  --create-namespace \
  -f search-values.yaml
```

### AxonOps Server

Create `axonops-server-secret.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: axon-server-config
  namespace: axonops
type: Opaque
stringData:
  axon-server.yml: |
    agents_port: 1888
    api_port: 8080
    host: 0.0.0.0

    search_db:
      hosts:
        - https://axondb-search-cluster-master.axonops.svc.cluster.local:9200
      username: admin
      password: MyS3cur3P@ss2025
      skip_verify: true

    org_name: example

    axon_dash_url: https://axonops.example.com

    # Log to stdout for Kubernetes
    log_file: /dev/stdout
    tls:
      mode: disabled
    auth:
      enabled: false
    cql_autocreate_tables: true
    cql_hosts:
      - axondb-timeseries-headless.axonops.svc.cluster.local
    cql_skip_verify: true
    cql_ssl: true
    cql_username: cassandra
    cql_password: cassandra
```

:::note
The default installation assumes your clients will be all in Kubernetes. If you will have AxonOps clients outside of Kubernetes (external Cassandra or Kafka clusters) you will also need to add an ingress or NodePort configuration.
:::

If you need external access, create `axon-server-values.yaml` using the following example:

```yaml
# If you do not have an ingress (Preferred) you can use nodePort by setting
# it up here
agentService:
  type: ClusterIP
  listenPort: 1888
  annotations: {}
  labels: {}
  externalIPs: []
  # Optional, only used for "type: ClusterIP"
  clusterIP: ""
  # Optional, only used for "type: LoadBalancer"
  loadBalancerIP: ""
  loadBalancerSourceRanges: []
  # Optional, only used for "type: NodePort"
  nodePort: 0

# For ingress, you can chose between nginx, traefik, etc or the new
# HTTPRoute Gateway API: https://gateway-api.sigs.k8s.io/api-types/httproute/
apiIngress:
  enabled: false
  className: traefik
  annotations: {}
    # cert-manager.io/cluster-issuer: "letsencrypt"
  hosts:
    - host: api.example.com
      paths:
        - path: /
          pathType: ImplementationSpecific
  tls: []
    # - secretName: api-tls
    #   hosts:
    #     - api.example.com

# HTTPRoute configuration for Gateway API (alternative to Ingress)
httpRoute:
  enabled: false
  annotations: {}
  parentRefs:
    - name: gateway
      sectionName: http
      # namespace: default
  hostnames:
    - api.example.com
  rules:
    - matches:
        - path:
            type: PathPrefix
            value: /
```

Install:

```bash
kubectl apply -n axonops -f axonops-server-secret.yaml

helm install axon-server oci://ghcr.io/axonops/charts/axon-server \
  --namespace axonops \
  --create-namespace \
  -f axon-server-values.yaml \ ## IF used
  --set configurationSecret=axon-server-config
```

### AxonOps Dashboard

Create `axonops-dash-values.yaml`:

```yaml
# Configuration for axon-dash application
config:
  # Axon server URL endpoint
  axonServerUrl: "http://axon-server-api.axonops.svc.cluster.local:8080"

service:
  type: ClusterIP
  port: 3000

# Alternative: NodePort configuration
# service:
#   type: NodePort
#   ports:
#     - port: 3000
#       targetPort: 3000
#       nodePort: 32000 # The ACTUAL "Host Port" (must be 30000-32767)

ingress:
  enabled: false
  className: ""
  annotations: {}
    # kubernetes.io/ingress.class: nginx
    # kubernetes.io/tls-acme: "true"
    # cert-manager.io/cluster-issuer: selfsigned-cluster-issuer
  hosts:
    - host: axonops.mycompany.com
      paths:
        - path: /
          pathType: ImplementationSpecific
  tls: []
    # - secretName: axon-dash-tls
    #   hosts:
    #     - axonops.mycompany.com
```

:::note
You will need to choose between Ingress (preferred option) or NodePort for external access.
:::

Install:

```bash
helm install axon-dash oci://ghcr.io/axonops/charts/axon-dash \
  --namespace axonops \
  --create-namespace \
  -f axonops-dash-values.yaml
```

## Validation

Verify all pods are running:

```bash
k get po -n axonops
```

Expected output:

```
NAME                              READY   STATUS    RESTARTS   AGE
axon-dash-847d57885-bmnnl         1/1     Running   0          62s
axon-server-0                     1/1     Running   0          63s
axondb-search-cluster-master-0    1/1     Running   0          3m9s
axondb-timeseries-0               1/1     Running   0          4m43s
```

Verify all services are created:

```bash
k get svc -n axonops
```

Expected output:

```
NAME                                    TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)                      AGE
axon-dash-svc                           ClusterIP   10.43.72.64     <none>        3000/TCP                     89s
axon-server-agent                       ClusterIP   10.43.8.100     <none>        1888/TCP                     90s
axon-server-api                         ClusterIP   10.43.237.168   <none>        8080/TCP                     90s
axondb-search-cluster-master            ClusterIP   10.43.120.95    <none>        9200/TCP,9300/TCP,9600/TCP   3m36s
axondb-search-cluster-master-headless   ClusterIP   None            <none>        9200/TCP,9300/TCP,9600/TCP   3m36s
axondb-timeseries                       ClusterIP   10.43.16.42     <none>        9042/TCP,7199/TCP            5m10s
axondb-timeseries-headless              ClusterIP   None            <none>        9042/TCP                     5m10s
```
