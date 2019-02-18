# Welcome to AxonOps Documentation

## Introduction

AxonOps is an extensible operational management tool initially built for Apache Cassandra (https://cassandra.apache.org). It is currently being extended to manage Apache Kafka (http://kafka.apache.org), Elasticsearch (https://www.elastic.co/products/elasticsearch), and others.

## Features

* **Inventory** information overview
* Dashboarding **metrics**, **logs**, and **healthchecks**
* **Highly efficient** metrics collection and storage from the agents
* Integrates with ChatOps and alerting tools - **Slack** and **PagerDuty** etc for notifications and alerts
* Domain aware functionalities, including Cassandra **repairs** and **backups** schedulers.
* **Free** version supports up to 6 nodes.

## Components 

AxonOps has four main components:

* **axon-server** - The main server of axonops that collect metrics, logs, events and more.
* **axon-dash** - The UI to interact with axon-server (dash for AxonOps Dashboards).
* **axon-agents** - An to small agent binary deployed onto the managed nodes.
* **Elasticsearch** - A distributed search engine which stores all of the collected data.

