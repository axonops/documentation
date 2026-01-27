#!/usr/bin/env python3
"""
Script to add SEO meta tags to all remaining markdown files.
"""

import os
import re

# All remaining pages that need meta tags
ALL_META = {
    # Authentication
    "authentication/jumpcloud-axonops-cloud/index": {
        "description": "Configure JumpCloud SAML authentication for AxonOps Cloud. Step-by-step SSO integration guide.",
        "keywords": "JumpCloud, SAML, SSO, AxonOps authentication, single sign-on"
    },
    "authentication/jumpcloud-axonops-cloud/01-jumpcloud-app": {
        "description": "Create JumpCloud SAML application for AxonOps Cloud integration. Configure SSO connector.",
        "keywords": "JumpCloud app, SAML application, AxonOps SSO, connector setup"
    },
    "authentication/jumpcloud-axonops-cloud/02-jumpcloud-roles": {
        "description": "Configure JumpCloud roles for AxonOps Cloud access. Map user groups to AxonOps permissions.",
        "keywords": "JumpCloud roles, user groups, AxonOps permissions, role mapping"
    },
    "authentication/jumpcloud-axonops-cloud/03-axonops-saml-jumpcloud": {
        "description": "Complete AxonOps SAML configuration with JumpCloud. Finalize SSO integration settings.",
        "keywords": "AxonOps SAML, JumpCloud integration, SSO configuration, SAML settings"
    },
    "authentication/ldap": {
        "description": "Configure LDAP authentication for AxonOps. Integrate with Active Directory or OpenLDAP.",
        "keywords": "LDAP authentication, Active Directory, OpenLDAP, AxonOps login"
    },

    # Cassandra - remaining files
    "cassandra/architecture/consistency/index": {
        "description": "Cassandra consistency levels explained. Configure read and write consistency for your workload.",
        "keywords": "consistency levels, Cassandra consistency, QUORUM, LOCAL_QUORUM"
    },
    "cassandra/architecture/data-distribution": {
        "description": "Data distribution in Cassandra. How partitioning and replication spread data across nodes.",
        "keywords": "data distribution, Cassandra partitioning, data placement, ring"
    },
    "cassandra/architecture/gossip": {
        "description": "Gossip protocol in Cassandra for cluster communication and failure detection.",
        "keywords": "gossip protocol, Cassandra gossip, cluster communication, failure detection"
    },
    "cassandra/getting-started/index": {
        "description": "Getting started with Apache Cassandra. Installation, first cluster, and quickstart guide.",
        "keywords": "Cassandra getting started, installation, first cluster, quickstart"
    },
    "cassandra/tools/nodetool/commands/stopdaemon": {
        "description": "Stop Cassandra daemon using nodetool stopdaemon command. Shutdown procedures.",
        "keywords": "nodetool stopdaemon, stop Cassandra, shutdown daemon"
    },

    # Cluster
    "cluster/cluster-overview": {
        "description": "AxonOps cluster overview dashboard. Monitor Cassandra and Kafka cluster health at a glance.",
        "keywords": "cluster overview, AxonOps dashboard, cluster health, monitoring"
    },

    # Configuration
    "configuration/agent-configuration": {
        "description": "AxonOps agent configuration reference. Configure monitoring agents for Cassandra and Kafka.",
        "keywords": "AxonOps agent config, agent configuration, monitoring agent, axon-agent.yml"
    },
    "configuration/axondash": {
        "description": "AxonOps Dashboard configuration. Configure web interface settings and authentication.",
        "keywords": "AxonOps dashboard config, axon-dash configuration, web interface"
    },
    "configuration/server-configuration": {
        "description": "AxonOps Server configuration reference. Configure backend server settings and storage.",
        "keywords": "AxonOps server config, server configuration, axon-server.yml"
    },

    # Dynamic pages (internal)
    "dynamic_pages/axon_agent/cassandra": {
        "description": "AxonOps Cassandra agent dynamic configuration page.",
        "keywords": "AxonOps agent, Cassandra agent, dynamic config"
    },
    "dynamic_pages/axon_agent/cassandra_agent": {
        "description": "AxonOps Cassandra agent installation dynamic page.",
        "keywords": "Cassandra agent install, AxonOps agent"
    },
    "dynamic_pages/axon_agent/java": {
        "description": "Java requirements for AxonOps Cassandra agent.",
        "keywords": "Java requirements, AxonOps agent, JVM"
    },
    "dynamic_pages/axon_agent/kafka_agent": {
        "description": "AxonOps Kafka agent installation dynamic page.",
        "keywords": "Kafka agent install, AxonOps agent"
    },
    "dynamic_pages/axon_agent/kafka_agent_config": {
        "description": "AxonOps Kafka agent configuration dynamic page.",
        "keywords": "Kafka agent config, AxonOps agent"
    },
    "dynamic_pages/axon_agent/kafka_java": {
        "description": "Java requirements for AxonOps Kafka agent.",
        "keywords": "Java requirements, Kafka agent, JVM"
    },
    "dynamic_pages/axon_agent/os": {
        "description": "Operating system requirements for AxonOps agent.",
        "keywords": "OS requirements, AxonOps agent, Linux"
    },
    "dynamic_pages/axon_dash/os": {
        "description": "Operating system requirements for AxonOps Dashboard.",
        "keywords": "OS requirements, AxonOps dashboard, Linux"
    },
    "dynamic_pages/axon_server/elastic": {
        "description": "Elasticsearch requirements for AxonOps Server.",
        "keywords": "Elasticsearch, AxonOps server, storage requirements"
    },
    "dynamic_pages/axon_server/os": {
        "description": "Operating system requirements for AxonOps Server.",
        "keywords": "OS requirements, AxonOps server, Linux"
    },

    # Editions
    "editions/enterprise_edition": {
        "description": "AxonOps Enterprise Edition features. Advanced monitoring, backup, and management for production clusters.",
        "keywords": "AxonOps Enterprise, enterprise features, production monitoring"
    },
    "editions/free_edition": {
        "description": "AxonOps Free Edition features. Get started with Cassandra and Kafka monitoring at no cost.",
        "keywords": "AxonOps Free, free tier, getting started, trial"
    },
    "editions/intro": {
        "description": "AxonOps editions comparison. Choose the right plan for your Cassandra and Kafka monitoring needs.",
        "keywords": "AxonOps editions, pricing, plans, comparison"
    },

    # Get Started
    "get_started/agent_setup_cassandra": {
        "description": "Set up AxonOps agent for Cassandra monitoring. Step-by-step installation guide.",
        "keywords": "Cassandra agent setup, AxonOps installation, monitoring setup"
    },
    "get_started/agent_setup_kafka": {
        "description": "Set up AxonOps agent for Kafka monitoring. Step-by-step installation guide.",
        "keywords": "Kafka agent setup, AxonOps installation, monitoring setup"
    },
    "get_started/docker": {
        "description": "Run AxonOps with Docker. Quick development setup using Docker Compose.",
        "keywords": "AxonOps Docker, Docker Compose, development setup, containers"
    },
    "get_started/getting_started": {
        "description": "Getting started with AxonOps self-hosted deployment. Installation overview and requirements.",
        "keywords": "AxonOps getting started, self-hosted, installation overview"
    },
    "get_started/proxy": {
        "description": "Configure AxonOps with proxy settings. HTTP proxy configuration for agents and server.",
        "keywords": "AxonOps proxy, HTTP proxy, proxy configuration"
    },

    # How-to
    "how-to/backup-restore-notifications": {
        "description": "Configure backup and restore notifications in AxonOps. Alert on backup status and failures.",
        "keywords": "backup notifications, restore alerts, AxonOps notifications"
    },
    "how-to/default-routing": {
        "description": "Set up default routing for AxonOps alerts. Configure notification channels and escalation.",
        "keywords": "alert routing, default routing, notification channels, AxonOps"
    },
    "how-to/reuse-host-id": {
        "description": "Reuse host ID in AxonOps when replacing nodes. Maintain monitoring history across node replacements.",
        "keywords": "reuse host ID, node replacement, monitoring history, AxonOps"
    },
    "how-to/rolling-restart": {
        "description": "Perform rolling restarts with AxonOps. Safely restart Cassandra nodes without downtime.",
        "keywords": "rolling restart, Cassandra restart, zero downtime, AxonOps"
    },
    "how-to/setup-alert-rules": {
        "description": "Create alert rules in AxonOps. Configure thresholds and notifications for metrics.",
        "keywords": "alert rules, AxonOps alerts, threshold configuration, notifications"
    },
    "how-to/setup-dashboards-global-integrations": {
        "description": "Set up global dashboard integrations in AxonOps. Configure organization-wide settings.",
        "keywords": "global integrations, dashboard setup, AxonOps configuration"
    },
    "how-to/setup-log-collection": {
        "description": "Configure log collection in AxonOps. Aggregate and search Cassandra and Kafka logs.",
        "keywords": "log collection, AxonOps logs, log aggregation, search logs"
    },
    "how-to/setup-servicechecks": {
        "description": "Set up service checks in AxonOps. Monitor service availability and health.",
        "keywords": "service checks, health monitoring, availability checks, AxonOps"
    },

    # Installation
    "installation/agent/agent_setup_cassandra": {
        "description": "Install AxonOps agent for Cassandra. Detailed installation steps for all platforms.",
        "keywords": "Cassandra agent install, AxonOps agent, installation guide"
    },
    "installation/agent/agent_setup_kafka": {
        "description": "Install AxonOps agent for Kafka. Detailed installation steps for all platforms.",
        "keywords": "Kafka agent install, AxonOps agent, installation guide"
    },
    "installation/agent/docker": {
        "description": "Run AxonOps agent in Docker containers. Container deployment guide.",
        "keywords": "AxonOps agent Docker, container deployment, Docker agent"
    },
    "installation/axon-dash/install": {
        "description": "Install AxonOps Dashboard. Web interface installation for monitoring and management.",
        "keywords": "AxonOps Dashboard install, web interface, installation"
    },
    "installation/axon-server/axonserver_install": {
        "description": "Install AxonOps Server. Backend server installation and configuration guide.",
        "keywords": "AxonOps Server install, backend installation, server setup"
    },
    "installation/axon-server/install": {
        "description": "AxonOps Server installation overview. Requirements and deployment options.",
        "keywords": "AxonOps Server, installation overview, deployment"
    },
    "installation/axon-server/metricsdatabase": {
        "description": "Configure metrics database for AxonOps Server. Cassandra as metrics storage backend.",
        "keywords": "metrics database, Cassandra metrics store, AxonOps storage"
    },
    "installation/compat_matrix/compat_matrix": {
        "description": "AxonOps compatibility matrix. Supported versions of Cassandra, Kafka, and operating systems.",
        "keywords": "compatibility matrix, supported versions, Cassandra versions, Kafka versions"
    },
    "installation/dse-agent/install": {
        "description": "Install AxonOps agent for DataStax Enterprise. DSE monitoring setup guide.",
        "keywords": "DSE agent, DataStax Enterprise, AxonOps DSE, monitoring"
    },
    "installation/elasticsearch/elastic": {
        "description": "Configure Elasticsearch for AxonOps. Search backend setup and optimization.",
        "keywords": "Elasticsearch setup, AxonOps Elasticsearch, search backend"
    },
    "installation/elasticsearch/install": {
        "description": "Install Elasticsearch for AxonOps. Log storage and search engine installation.",
        "keywords": "Elasticsearch install, AxonOps logs, search installation"
    },
    "installation/release_notes": {
        "description": "AxonOps release notes. Latest features, improvements, and bug fixes.",
        "keywords": "release notes, AxonOps updates, changelog, new features"
    },

    # Integrations
    "integrations/email-integration": {
        "description": "Configure email notifications in AxonOps. SMTP setup for alert delivery.",
        "keywords": "email integration, SMTP, email alerts, AxonOps notifications"
    },
    "integrations/log-file-integration": {
        "description": "Configure log file output in AxonOps. Write alerts to log files.",
        "keywords": "log file integration, alert logging, file output"
    },
    "integrations/microsoft-teams-integration": {
        "description": "Configure Microsoft Teams notifications in AxonOps. Send alerts to Teams channels.",
        "keywords": "Microsoft Teams, Teams integration, AxonOps alerts, chat notifications"
    },
    "integrations/overview": {
        "description": "AxonOps notification integrations overview. Connect to Slack, PagerDuty, Teams, and more.",
        "keywords": "integrations overview, notifications, alerting channels, AxonOps"
    },
    "integrations/pagerduty-integration": {
        "description": "Configure PagerDuty integration in AxonOps. Incident management and on-call alerting.",
        "keywords": "PagerDuty integration, incident management, on-call alerts, AxonOps"
    },
    "integrations/servicenow-integration": {
        "description": "Configure ServiceNow integration in AxonOps. Create tickets from alerts automatically.",
        "keywords": "ServiceNow integration, ticket creation, ITSM, AxonOps"
    },
    "integrations/slack-integration": {
        "description": "Configure Slack notifications in AxonOps. Send alerts to Slack channels.",
        "keywords": "Slack integration, Slack alerts, chat notifications, AxonOps"
    },

    # Introduction
    "introduction/overview": {
        "description": "AxonOps overview. Unified monitoring, maintenance, and backup platform for Cassandra and Kafka.",
        "keywords": "AxonOps overview, Cassandra monitoring, Kafka monitoring, database management"
    },

    # Kafka
    "kafka/acl/configure_acl": {
        "description": "Configure Kafka ACLs with AxonOps. Manage access control list settings.",
        "keywords": "Kafka ACL configure, access control, ACL settings"
    },
    "kafka/acl/create_acl": {
        "description": "Create Kafka ACLs with AxonOps. Set up access control for topics and groups.",
        "keywords": "create Kafka ACL, access control, permissions"
    },
    "kafka/acl/delete_acl": {
        "description": "Delete Kafka ACLs with AxonOps. Remove access control entries.",
        "keywords": "delete Kafka ACL, remove permissions, ACL management"
    },
    "kafka/acl/overview": {
        "description": "Kafka ACL management in AxonOps. Overview of access control list features.",
        "keywords": "Kafka ACL overview, access control, AxonOps Kafka"
    },
    "kafka/brokers/overview": {
        "description": "Kafka broker management in AxonOps. Monitor and manage Kafka brokers.",
        "keywords": "Kafka brokers, broker management, AxonOps Kafka"
    },
    "kafka/consumers/overview": {
        "description": "Kafka consumer group management in AxonOps. Monitor consumer lag and offsets.",
        "keywords": "Kafka consumers, consumer groups, lag monitoring, AxonOps"
    },
    "kafka/topics/configure_topic": {
        "description": "Configure Kafka topics with AxonOps. Modify topic settings and partitions.",
        "keywords": "configure Kafka topic, topic settings, partitions"
    },
    "kafka/topics/create_topic": {
        "description": "Create Kafka topics with AxonOps. Set up new topics with partitions and replication.",
        "keywords": "create Kafka topic, new topic, partitions, replication"
    },
    "kafka/topics/overview": {
        "description": "Kafka topic management in AxonOps. Monitor and manage topics across clusters.",
        "keywords": "Kafka topics, topic management, AxonOps Kafka"
    },

    # Metrics - Cassandra
    "metrics/cassandra/all_dashboards_metrics_reference": {
        "description": "Complete Cassandra metrics reference for AxonOps dashboards. All available metrics documented.",
        "keywords": "Cassandra metrics reference, all metrics, dashboard metrics"
    },
    "metrics/cassandra/application_metrics_mapping": {
        "description": "Cassandra application dashboard metrics mapping. Client request and latency metrics.",
        "keywords": "application metrics, client requests, latency metrics, Cassandra"
    },
    "metrics/cassandra/cache_metrics_mapping": {
        "description": "Cassandra cache dashboard metrics mapping. Key cache and row cache metrics.",
        "keywords": "cache metrics, key cache, row cache, Cassandra caching"
    },
    "metrics/cassandra/compactions_metrics_mapping": {
        "description": "Cassandra compaction dashboard metrics mapping. Compaction progress and throughput.",
        "keywords": "compaction metrics, compaction progress, throughput, Cassandra"
    },
    "metrics/cassandra/coordinator_metrics_mapping": {
        "description": "Cassandra coordinator dashboard metrics mapping. Request coordination metrics.",
        "keywords": "coordinator metrics, request coordination, Cassandra"
    },
    "metrics/cassandra/cql_metrics_mapping": {
        "description": "Cassandra CQL dashboard metrics mapping. Query performance and prepared statements.",
        "keywords": "CQL metrics, query performance, prepared statements"
    },
    "metrics/cassandra/data_metrics_mapping": {
        "description": "Cassandra data dashboard metrics mapping. Storage and SSTable metrics.",
        "keywords": "data metrics, storage metrics, SSTable metrics, Cassandra"
    },
    "metrics/cassandra/dropped_messages_metrics_mapping": {
        "description": "Cassandra dropped messages dashboard metrics mapping. Message drop statistics.",
        "keywords": "dropped messages, message drops, Cassandra metrics"
    },
    "metrics/cassandra/entropy_metrics_mapping": {
        "description": "Cassandra entropy dashboard metrics mapping. Repair and consistency metrics.",
        "keywords": "entropy metrics, repair metrics, consistency, Cassandra"
    },
    "metrics/cassandra/keyspace_metrics_mapping": {
        "description": "Cassandra keyspace dashboard metrics mapping. Per-keyspace statistics.",
        "keywords": "keyspace metrics, per-keyspace stats, Cassandra"
    },
    "metrics/cassandra/reporting_metrics_mapping": {
        "description": "Cassandra reporting dashboard metrics mapping. Operational reporting metrics.",
        "keywords": "reporting metrics, operational metrics, Cassandra"
    },
    "metrics/cassandra/security_metrics_mapping": {
        "description": "Cassandra security dashboard metrics mapping. Authentication and authorization metrics.",
        "keywords": "security metrics, authentication metrics, authorization, Cassandra"
    },
    "metrics/cassandra/system_metrics_mapping": {
        "description": "Cassandra system dashboard metrics mapping. CPU, memory, and disk metrics.",
        "keywords": "system metrics, CPU metrics, memory metrics, disk, Cassandra"
    },
    "metrics/cassandra/table_metrics_mapping": {
        "description": "Cassandra table dashboard metrics mapping. Per-table performance statistics.",
        "keywords": "table metrics, per-table stats, Cassandra performance"
    },
    "metrics/cassandra/thread_pools_metrics_mapping": {
        "description": "Cassandra thread pools dashboard metrics mapping. SEDA stage statistics.",
        "keywords": "thread pools metrics, SEDA stages, Cassandra threads"
    },

    # Metrics - Kafka
    "metrics/kafka/all_kafka_dashboards_metrics_reference": {
        "description": "Complete Kafka metrics reference for AxonOps dashboards. All available metrics documented.",
        "keywords": "Kafka metrics reference, all metrics, dashboard metrics"
    },
    "metrics/kafka/connect_overview_metrics_mapping": {
        "description": "Kafka Connect overview dashboard metrics mapping. Connector status and throughput.",
        "keywords": "Kafka Connect metrics, connector status, throughput"
    },
    "metrics/kafka/connect_tasks_metrics_mapping": {
        "description": "Kafka Connect tasks dashboard metrics mapping. Task performance statistics.",
        "keywords": "Connect tasks metrics, task performance, Kafka Connect"
    },
    "metrics/kafka/connect_workers_metrics_mapping": {
        "description": "Kafka Connect workers dashboard metrics mapping. Worker node statistics.",
        "keywords": "Connect workers metrics, worker stats, Kafka Connect"
    },
    "metrics/kafka/connections_metrics_mapping": {
        "description": "Kafka connections dashboard metrics mapping. Client connection statistics.",
        "keywords": "Kafka connections, client connections, connection metrics"
    },
    "metrics/kafka/consumer_groups_metrics_mapping": {
        "description": "Kafka consumer groups dashboard metrics mapping. Consumer lag and offset metrics.",
        "keywords": "consumer groups metrics, consumer lag, offset metrics, Kafka"
    },
    "metrics/kafka/controller_metrics_mapping": {
        "description": "Kafka controller dashboard metrics mapping. Controller election and partition metrics.",
        "keywords": "Kafka controller metrics, controller election, partitions"
    },
    "metrics/kafka/overview_metrics_mapping": {
        "description": "Kafka overview dashboard metrics mapping. Cluster health and throughput.",
        "keywords": "Kafka overview metrics, cluster health, throughput"
    },
    "metrics/kafka/performance_metrics_mapping": {
        "description": "Kafka performance dashboard metrics mapping. Latency and throughput statistics.",
        "keywords": "Kafka performance metrics, latency, throughput"
    },
    "metrics/kafka/replication_metrics_mapping": {
        "description": "Kafka replication dashboard metrics mapping. ISR and replica statistics.",
        "keywords": "Kafka replication metrics, ISR, replica stats"
    },
    "metrics/kafka/requests_metrics_mapping": {
        "description": "Kafka requests dashboard metrics mapping. Request rate and latency.",
        "keywords": "Kafka requests metrics, request rate, request latency"
    },
    "metrics/kafka/system_metrics_mapping": {
        "description": "Kafka system dashboard metrics mapping. CPU, memory, and disk metrics.",
        "keywords": "Kafka system metrics, CPU, memory, disk"
    },
    "metrics/kafka/topics_metrics_mapping": {
        "description": "Kafka topics dashboard metrics mapping. Per-topic throughput and size.",
        "keywords": "Kafka topics metrics, topic throughput, topic size"
    },
    "metrics/kafka/zookeeper_metrics_mapping": {
        "description": "ZooKeeper dashboard metrics mapping for Kafka. ZK cluster health metrics.",
        "keywords": "ZooKeeper metrics, ZK health, Kafka ZooKeeper"
    },

    # Monitoring
    "monitoring/grafana/grafana": {
        "description": "View AxonOps metrics in Grafana. Export and visualize Cassandra and Kafka metrics.",
        "keywords": "Grafana integration, AxonOps Grafana, metrics visualization"
    },
    "monitoring/logsandevents/logsandevents": {
        "description": "Logs and events in AxonOps. View and search Cassandra and Kafka log entries.",
        "keywords": "logs and events, log search, AxonOps logging"
    },
    "monitoring/metricsdashboards/cassandra": {
        "description": "Cassandra metrics dashboards in AxonOps. Pre-built dashboards for monitoring.",
        "keywords": "Cassandra dashboards, metrics dashboards, AxonOps monitoring"
    },
    "monitoring/metricsdashboards/kafka": {
        "description": "Kafka metrics dashboards in AxonOps. Pre-built dashboards for monitoring.",
        "keywords": "Kafka dashboards, metrics dashboards, AxonOps monitoring"
    },
    "monitoring/metricsdashboards/querysyntax": {
        "description": "AxonOps query syntax for Cassandra metrics. Build custom queries and dashboards.",
        "keywords": "query syntax, Cassandra metrics, custom queries, AxonOps"
    },
    "monitoring/metricsdashboards/querysyntax_kafka": {
        "description": "AxonOps query syntax for Kafka metrics. Build custom queries and dashboards.",
        "keywords": "query syntax, Kafka metrics, custom queries, AxonOps"
    },
    "monitoring/overview": {
        "description": "AxonOps monitoring overview. Features for Cassandra and Kafka cluster monitoring.",
        "keywords": "monitoring overview, AxonOps monitoring, cluster monitoring"
    },
    "monitoring/servicechecks/notifications": {
        "description": "Service check notifications in AxonOps. Configure alerts for service availability.",
        "keywords": "service check notifications, availability alerts, AxonOps"
    },
    "monitoring/servicechecks/overview": {
        "description": "Service checks in AxonOps. Monitor service health and availability.",
        "keywords": "service checks, health checks, availability monitoring"
    },

    # Operations - Backup
    "operations/cassandra/backup/aws_s3": {
        "description": "Configure AWS S3 backup for Cassandra with AxonOps. Store backups in Amazon S3.",
        "keywords": "AWS S3 backup, Cassandra backup, Amazon S3, AxonOps"
    },
    "operations/cassandra/backup/azure_blob": {
        "description": "Configure Azure Blob Storage backup for Cassandra with AxonOps.",
        "keywords": "Azure Blob backup, Cassandra backup, Azure storage, AxonOps"
    },
    "operations/cassandra/backup/azure_blob_storage": {
        "description": "Azure Blob Storage backup configuration for Cassandra. Detailed setup guide.",
        "keywords": "Azure Blob Storage, Cassandra backup, Azure, AxonOps"
    },
    "operations/cassandra/backup/gcs": {
        "description": "Configure Google Cloud Storage backup for Cassandra with AxonOps.",
        "keywords": "GCS backup, Google Cloud Storage, Cassandra backup, AxonOps"
    },
    "operations/cassandra/backup/generic_s3": {
        "description": "Configure S3-compatible storage backup for Cassandra. MinIO, Ceph, and other providers.",
        "keywords": "S3 compatible backup, MinIO, Ceph, Cassandra backup"
    },
    "operations/cassandra/backup/google_cloud_storage": {
        "description": "Google Cloud Storage backup configuration for Cassandra. Detailed setup guide.",
        "keywords": "Google Cloud Storage, GCS, Cassandra backup, AxonOps"
    },
    "operations/cassandra/backup/local_filesystem": {
        "description": "Configure local filesystem backup for Cassandra with AxonOps.",
        "keywords": "local backup, filesystem backup, Cassandra backup"
    },
    "operations/cassandra/backup/local_storage": {
        "description": "Local storage backup configuration for Cassandra. On-disk backup settings.",
        "keywords": "local storage backup, disk backup, Cassandra"
    },
    "operations/cassandra/backup/overview": {
        "description": "Cassandra backup overview with AxonOps. Automated backup features and options.",
        "keywords": "Cassandra backup overview, automated backup, AxonOps backup"
    },
    "operations/cassandra/backup/remote": {
        "description": "Remote backup destinations for Cassandra in AxonOps. Cloud storage options.",
        "keywords": "remote backup, cloud backup, Cassandra backup destinations"
    },
    "operations/cassandra/backup/s3_compatible": {
        "description": "S3-compatible storage backup for Cassandra. Configure alternative S3 providers.",
        "keywords": "S3 compatible, alternative S3, Cassandra backup"
    },
    "operations/cassandra/backup/sftp_ssh": {
        "description": "Configure SFTP/SSH backup for Cassandra with AxonOps. Remote server backup.",
        "keywords": "SFTP backup, SSH backup, remote backup, Cassandra"
    },
    "operations/cassandra/backup/ssh_sftp": {
        "description": "SSH/SFTP backup configuration for Cassandra. Secure remote backup setup.",
        "keywords": "SSH backup, SFTP, secure backup, Cassandra"
    },

    # Operations - Repair
    "operations/cassandra/repair/index": {
        "description": "Cassandra repair with AxonOps. Automated repair scheduling and management.",
        "keywords": "Cassandra repair, automated repair, AxonOps repair, anti-entropy"
    },

    # Operations - Restore
    "operations/cassandra/restore/overview": {
        "description": "Cassandra restore overview with AxonOps. Restore from backups to recover data.",
        "keywords": "Cassandra restore, data recovery, AxonOps restore, backup restore"
    },
    "operations/cassandra/restore/restore-cluster-different-ips": {
        "description": "Restore Cassandra cluster with different IP addresses. Migration and disaster recovery.",
        "keywords": "restore different IPs, cluster migration, disaster recovery, Cassandra"
    },
    "operations/cassandra/restore/restore-cluster-same-ip": {
        "description": "Restore Cassandra cluster with same IP addresses. In-place cluster recovery.",
        "keywords": "restore same IP, cluster recovery, in-place restore, Cassandra"
    },
    "operations/cassandra/restore/restore-different-cluster": {
        "description": "Restore Cassandra data to a different cluster. Cross-cluster data migration.",
        "keywords": "restore different cluster, data migration, cross-cluster, Cassandra"
    },
    "operations/cassandra/restore/restore-node-different-ip": {
        "description": "Restore single Cassandra node with different IP address. Node replacement scenario.",
        "keywords": "restore node different IP, node replacement, single node restore"
    },
    "operations/cassandra/restore/restore-node-same-ip": {
        "description": "Restore single Cassandra node with same IP address. Node recovery procedure.",
        "keywords": "restore node same IP, node recovery, single node restore"
    },

    # Operations - Rolling Restart
    "operations/cassandra/rollingrestart/overview": {
        "description": "Rolling restart for Cassandra with AxonOps. Zero-downtime cluster restarts.",
        "keywords": "rolling restart, Cassandra restart, zero downtime, AxonOps"
    },
    "operations/kafka/rollingrestart/overview": {
        "description": "Rolling restart for Kafka with AxonOps. Zero-downtime broker restarts.",
        "keywords": "rolling restart, Kafka restart, zero downtime, broker restart"
    },

    # Overview
    "overview/architecture": {
        "description": "AxonOps architecture overview. Components and deployment topology.",
        "keywords": "AxonOps architecture, components, deployment, topology"
    },
    "overview/axonops-cloud": {
        "description": "AxonOps Cloud overview. Managed monitoring service for Cassandra and Kafka.",
        "keywords": "AxonOps Cloud, managed service, SaaS monitoring"
    },
    "overview/axonops-enterprise": {
        "description": "AxonOps Enterprise overview. Self-hosted monitoring for production environments.",
        "keywords": "AxonOps Enterprise, self-hosted, on-premises monitoring"
    },
    "overview/motivation": {
        "description": "Why AxonOps was built. The motivation behind unified database operations platform.",
        "keywords": "AxonOps motivation, why AxonOps, database operations"
    },

    # PITR
    "pitr/configuration": {
        "description": "Configure point-in-time restore for Cassandra. Commitlog archiving setup.",
        "keywords": "PITR configuration, commitlog archiving, point-in-time setup"
    },
    "pitr/overview": {
        "description": "Point-in-time restore overview for Cassandra. Recover to any point in time.",
        "keywords": "PITR overview, point-in-time restore, Cassandra recovery"
    },
    "pitr/restore": {
        "description": "Perform point-in-time restore for Cassandra. Step-by-step recovery guide.",
        "keywords": "PITR restore, point-in-time recovery, Cassandra restore"
    },

    # Quickstart
    "quickstart/docker": {
        "description": "AxonOps Docker quickstart. Get started in minutes with Docker Compose.",
        "keywords": "Docker quickstart, AxonOps Docker, quick start, containers"
    },
    "quickstart/saas": {
        "description": "AxonOps Cloud quickstart. Get started with managed monitoring service.",
        "keywords": "SaaS quickstart, AxonOps Cloud, managed service, quick start"
    },

    # Release Notes
    "release_notes/releases": {
        "description": "AxonOps release history. All versions with features and improvements.",
        "keywords": "release history, all releases, AxonOps versions, changelog"
    },

    # Server
    "server/api/overview": {
        "description": "AxonOps API overview. REST API for automation and integration.",
        "keywords": "AxonOps API, REST API, automation, integration"
    },

    # System Requirements
    "system-requirements/index": {
        "description": "AxonOps system requirements. Hardware, software, and network prerequisites.",
        "keywords": "system requirements, prerequisites, hardware requirements, AxonOps"
    },

    # Workbench
    "workbench/cassandra/cassandra": {
        "description": "AxonOps Workbench for Cassandra. Desktop application for database management.",
        "keywords": "AxonOps Workbench, Cassandra GUI, desktop application, database management"
    },
    "workbench/cassandra/license": {
        "description": "AxonOps Workbench licensing. License types and activation.",
        "keywords": "Workbench license, AxonOps licensing, activation"
    },
}


def add_frontmatter(filepath, description, keywords):
    """Add YAML front matter to a markdown file."""
    with open(filepath, 'r') as f:
        content = f.read()

    # Check if front matter already exists
    if content.startswith('---'):
        print(f"Skipping {filepath} - already has front matter")
        return False

    # Create front matter
    frontmatter = f"""---
description: "{description}"
meta:
  - name: keywords
    content: "{keywords}"
---

"""

    # Write new content
    with open(filepath, 'w') as f:
        f.write(frontmatter + content)

    print(f"Added meta tags to {filepath}")
    return True


def process_all_files(base_path):
    """Process all files based on meta dictionary."""
    docs_path = os.path.join(base_path, "docs")
    count = 0
    missing = []

    for key, meta in ALL_META.items():
        filepath = os.path.join(docs_path, f"{key}.md")
        if os.path.exists(filepath):
            if add_frontmatter(filepath, meta["description"], meta["keywords"]):
                count += 1
        else:
            missing.append(filepath)

    print(f"\nProcessed {count} files")
    if missing:
        print(f"\nWarning: {len(missing)} files not found:")
        for f in missing[:10]:
            print(f"  - {f}")
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more")

    return count


if __name__ == "__main__":
    base_path = "/home/hayato/git/documentation"
    total = process_all_files(base_path)
    print(f"\n=== Total files processed: {total} ===")
