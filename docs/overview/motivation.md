# Motivation

AxonOps has been developed and actively maintained by [digitalis.io](https://digitalis.io), a company providing managed services for Apache Cassandra™ and other modern distributed data technologies.

digitalis.io used a variety of modern and popular open source tools to manage its customer's data platforms to gain quick insight into how the clusters are working, and be alerted when there are issues.

The open source tools we used are:

* [**Grafana**](https://grafana.com/) - metrics dashboarding
* [**Prometheus**](https://prometheus.io/) - time series database for metrics
* [**Prometheus Alertmanager**](https://prometheus.io/docs/alerting/alertmanager/) - metrics alerting
* [**ELK**](https://www.elastic.co/elk-stack) - Log capture and visualisation
* [**elastalert**](https://github.com/Yelp/elastalert) - Alerting on logs
* [**Consul**](https://www.consul.io/) - Service Discovery and Health Checks
* [**consul-alerts**](https://github.com/AcalephStorage/consul-alerts) - Alerting on service health check failures
* [**Rundeck**](https://www.rundeck.com/) - Job Scheduler
* [**Ansible**](https://www.ansible.com/) - Provisioning automation

## Problems
The tools listed above served us well. They gave us the confidence to manage enterprise deployment of distributed data platforms – alerting us when there are problems, ability to diagnose issues quickly, automatically performing routine scheduled tasks etc.

However, using these tools and their problems were realised over time.

1. **Too many components** - There are many components including the agents that need to be installed. Takes a lot of effort to integrate all components for each customer's on-premises environment, even with fully automated implementation using Ansible.
2. **Steep learning curve** - The learning curve of deploying and configuring all the components is high.
3. **Patching hell** - Patching schedule became a nightmare because of the sheer number of components. Imagine having to raise change requests for patching all above components!
4. **Enterprise hell** - Firewall configurations became big for enterprise on-premises customers, often required many hours of tracing which change requests were unsuccessfully executed.
5. **Multiple dashboards** - Multiple dashboards for metrics, logs and service availability.
6. **Complex alerting configurations** - Alert notification configurations were all over the place. Fine-tuning alerts and updating them takes a lot of work.

## Wish List
With the above problems in mind, we needed to become more efficient as a company deploying the tools we need to manage our customers.
After promoting the above tools to our customers, we ate the humble pie, and went back to the drawing board with the aim of reducing the efforts needed to on-board new customers.

* On-premises / cloud deployment
* Single dashboard for metrics / logs / service health
* Simple alert rules configurations
* Capture all metrics at high resolution (with Cassandra there are well over 20,000 metrics!)
* Capture logs and internal events like authentication, DDL, DML etc
* Scheduled backup / restore feature
* Performs domain specific administrative tasks, including Cassandra repair
* Manages the following products;
    * Apache Cassandra
    * Apache Kafka
    * DataStax Enterprise
    * Confluent Enterprise
    * Elasticsearch
    * Apache Spark
    * etc
* Simplified deployment model
* Single agent for collecting metrics, logs, event, configs
* The same agent performs execution of health checks, backup, restore
* No JMX to capture the metrics, and must be push from the JVM and not pull
* Single socket connection initiated by agent to management server requiring only simple firewall rules
* Bidirectional communication between agent and management server over the single socket
* Modern snappy GUI
