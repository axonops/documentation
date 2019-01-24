# Welcome to AxonOps Documentation

## Introduction

AxonOps is an extensible operational management tool initially built for Apache Cassandra (https://cassandra.apache.org). It is currently being extended to manage Apache Kafka (http://kafka.apache.org), Elasticsearch (https://www.elastic.co/products/elasticsearch), and others.

## Features

* Simple deployment model
* Dashboarding metrics, logs, and healthchecks
* Integrates with ChatOps tools - Slack, PagerDuty etc.
* Highly efficient metrics collection and storage
* Domain aware functionalities, including Cassandra repairs and backups.

## Components 

AxonOps is a set of 3 main components:

* axon-server - The main server of axonops that collect metrics, logs, events and more.
* axon-agents - They corresponds to small binaries deployed onto the nodes of your clusters.
* axon-dash - The UI to interact with axon-server (dash for AxonOps Dashboards).

