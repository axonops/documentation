# Cassandra with AxonOps on Kubernetes

## Introduction

The following shows how to install AxonOps for monitoring cassandra. This process specifically requires the official [cassandra helm repository](https://github.com/helm/charts/tree/master/incubator/cassandra).

## Using minikube

The deployment should work fine on latest versions of [minikube](https://kubernetes.io/docs/tasks/tools/install-minikube/) as long as you provide enough memory for it.

```sh
minikube start --memory 10240 --cpus=4 --driver=hyperkit
minikube addons enable storage-provisioner
```

## Helmfile

### Overview

As this deployment contains multiple applications we recommend you use an automation system such as Ansible or [Helmfile](https://github.com/roboll/helmfile) to put together the config. The example below uses helmfile.

### Install requirements

You would need to install the following components:

- helm: https://helm.sh/docs/intro/install/
- helmfile: https://github.com/roboll/helmfile/releases

Alternatively you can consider using a dockerized version of them both such as https://hub.docker.com/r/chatwork/helmfile

### Config files

The values below are set for running on a laptop with `minikube`, adjust accordingly for larger deployments.

#### helmfile.yaml

```yaml
---
repositories:
  - name: stable
    url: https://kubernetes-charts.storage.googleapis.com
  - name: incubator
    url: https://kubernetes-charts-incubator.storage.googleapis.com
  - name: digitalis
    url: https://repo.axonops.com/public/helm/helm/charts/
  - name: bitnami
    url: https://charts.bitnami.com/bitnami
releases:
  - name: cassandra
    namespace: cassandra
    chart: "incubator/cassandra"
    wait: true
    labels:
      env: dev
    values:
      - values.yaml
  - name: axon-elastic
    namespace: {{ env "NAMESPACE" | default "monitoring" }}
    chart: "bitnami/elasticsearch"
    wait: true
    labels:
      env: minikube
    values:
      - fullnameOverride: axon-elastic
      - imageTag: "7.8.0"
      - data:
          replicas: 1
          persistence:
            size: 1Gi
            enabled: true
            accessModes: [ "ReadWriteOnce" ]
      - curator:
          enabled: true
      - coordinating:
          replicas: 1
      - master:
          replicas: 1
          persistence:
            size: 1Gi
            enabled: true
            accessModes: [ "ReadWriteOnce" ]

  - name: axonops
    namespace: {{ env "NAMESPACE" | default "monitoring" }}
    chart: "axonops-helm/axonops"
    wait: true
    labels:
      env: minikube
    values:
      - values.yaml
```

#### values.yaml

```yaml
---
persistence:
  enabled: true
  size: 1Gi
  accessMode: ReadWriteMany

podSettings:
  terminationGracePeriodSeconds: 300

image:
  tag: 3.11.6
  pullPolicy: IfNotPresent

config:
  cluster_name: minikube
  cluster_size: 3
  seed_size: 2
  num_tokens: 256
  max_heap_size: 512M
  heap_new_size: 512M

env:
  JVM_OPTS: "-javaagent:/var/lib/axonops/axon-cassandra3.11-agent.jar=/etc/axonops/axon-agent.yml"

extraVolumes:
  - name: axonops-agent-config
    configMap:
      name: axonops-agent
  - name: axonops-shared
    emptyDir: {}
  - name: axonops-logs
    emptyDir: {}

extraVolumeMounts:
  - name: axonops-shared
    mountPath: /var/lib/axonops
    readOnly: false
  - name: axonops-agent-config
    mountPath: /etc/axonops
    readOnly: true
  - name: axonops-logs
    mountPath: /var/log/axonops

extraContainers:
  - name: axonops-agent
    image: digitalisdocker/axon-server:latest
    env:
      - name: AXON_AGENT_VERBOSITY
        value: "1"
    volumeMounts:
      - name: axonops-agent-config
        mountPath: /etc/axonops
        readOnly: true
      - name: axonops-shared
        mountPath: /var/lib/axonops
        readOnly: false
      - name: axonops-logs
        mountPath: /var/log/axonops

axon-server:
  elastic_host: http://axon-elastic-elasticsearch-master
  image:
    repository: digitalisdocker/axon-server
    tag: latest
    pullPolicy: IfNotPresent


axon-dash:
  axonServerUrl: http://axonops-axon-server:8080
  service:
    # use NodePort for minikube, change to ClusterIP or LoadBalancer on fully featured
    # k8s deployments such as AWS or Google
    type: NodePort
  image:
    repository: digitalisdocker/axon-dash
    tag: latest
    pullPolicy: IfNotPresent
```

#### axon-agent.yml

```yaml
axon-server:
    hosts: "axonops-axon-server.monitoring" # Specify axon-server IP axon-server.mycompany.
    port: 1888

axon-agent:
    org: "minikube" # Specify your organisation name
    human_readable_identifier: "axon_agent_ip" # one of the following:

NTP:
    host: "pool.ntp.org" # Specify a NTP to determine a NTP offset

cassandra:
  tier0: # metrics collected every 5 seconds
      metrics:
          jvm_:
            - "java.lang:*"
          cas_:
            - "org.apache.cassandra.metrics:*"
            - "org.apache.cassandra.net:type=FailureDetector"

  tier1:
      frequency: 300 # metrics collected every 300 seconds (5m)
      metrics:
          cas_:
            - "org.apache.cassandra.metrics:name=EstimatedPartitionCount,*"

  blacklist: # You can blacklist metrics based on Regex pattern. Hit the agent on http://agentIP:9916/metricslist to list JMX metrics it is collecting
    - "org.apache.cassandra.metrics:type=ColumnFamily.*" # duplication of table metrics
    - "org.apache.cassandra.metrics:.*scope=Repair#.*" # ignore each repair instance metrics
    - "org.apache.cassandra.metrics:.*name=SnapshotsSize.*" # Collecting SnapshotsSize metrics slows down collection
    - "org.apache.cassandra.metrics:.*Max.*"
    - "org.apache.cassandra.metrics:.*Min.*"
    - ".*999thPercentile|.*50thPercentile|.*FifteenMinuteRate|.*FiveMinuteRate|.*MeanRate|.*Mean|.*OneMinuteRate|.*StdDev"

  JMXOperationsBlacklist:
    - "getThreadInfo"
    - "getDatacenter"
    - "getRack"

  DMLEventsWhitelist: # You can whitelist keyspaces / tables (list of "keyspace" and/or "keyspace.table" to log DML queries. Data is not analysed.
  # - "system_distributed"

  DMLEventsBlacklist: # You can blacklist keyspaces / tables from the DMLEventsWhitelist (list of "keyspace" and/or "keyspace.table" to log DML queries. Data is not analysed.
  # - system_distributed.parent_repair_history

  logSuccessfulRepairs: false # set it to true if you want to log all the successful repair events.

  warningThresholdMillis: 200 # This will warn in logs when a MBean takes longer than the specified value.

  logFormat: "%4$s %1$tY-%1$tm-%1$td %1$tH:%1$tM:%1$tS,%1$tL %5$s%6$s%n"
```

## Start up

### Create Axon Agent configuration

```sh
kubectl create configmap axonops-agent --from-file=axon-agent.yml -n cassandra
```

### Run helmfile

#### With locally installed helm and helmfile

```sh
cd your/config/directory
hemlfile sync
```

#### With docker image

```sh
docker run --rm \
    -v ~/.kube:/root/.kube \
    -v ${PWD}/.helm:/root/.helm \
    -v ${PWD}/helmfile.yaml:/helmfile.yaml \
    -v ${PWD}/values.yaml:/values.yaml \
    --net=host chatwork/helmfile sync
```

## Access

### Minikube

If you used `minikube`, identify the name of the service with `kubectl get svc -n monitoring` and launch it with 

```sh
minikube service axonops-axon-dash -n monitoring
```

### LoadBalancer

Find the DNS entry for it:

```sh
kubectl get svc -n monitoring -o wide
```

Open your browser and copy and paste the URL.