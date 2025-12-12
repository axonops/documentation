#!/usr/bin/env python3
"""
Script to add SEO meta tags to remaining Cassandra documentation files.
"""

import os

# All remaining Cassandra pages that need meta tags
CASSANDRA_META = {
    # Application Development
    "cassandra/application-development/cqlai": {
        "description": "CQLAI - AI-powered CQL shell for Apache Cassandra. Natural language queries and intelligent assistance.",
        "keywords": "CQLAI, AI CQL, Cassandra AI, natural language queries, intelligent shell"
    },
    "cassandra/application-development/drivers/best-practices": {
        "description": "Best practices for Cassandra driver usage. Connection pooling, retry logic, and performance optimization.",
        "keywords": "Cassandra driver best practices, connection pooling, retry logic, performance"
    },
    "cassandra/application-development/drivers/connection-management": {
        "description": "Cassandra driver connection management. Configure connection pools, timeouts, and keep-alive settings.",
        "keywords": "Cassandra connection management, connection pool, timeouts, keep-alive"
    },
    "cassandra/application-development/drivers/index": {
        "description": "Cassandra drivers overview. Official drivers for Java, Python, Node.js, Go, and other languages.",
        "keywords": "Cassandra drivers, Java driver, Python driver, DataStax drivers"
    },
    "cassandra/application-development/drivers/policies/index": {
        "description": "Cassandra driver policies overview. Load balancing, retry, reconnection, and speculative execution.",
        "keywords": "Cassandra driver policies, load balancing policy, retry policy"
    },
    "cassandra/application-development/drivers/policies/load-balancing": {
        "description": "Cassandra load balancing policies. Configure token-aware, data center-aware, and round-robin routing.",
        "keywords": "Cassandra load balancing, token-aware, DC-aware, round-robin"
    },
    "cassandra/application-development/drivers/policies/reconnection": {
        "description": "Cassandra reconnection policies. Configure exponential backoff and constant delay strategies.",
        "keywords": "Cassandra reconnection, exponential backoff, connection retry"
    },
    "cassandra/application-development/drivers/policies/retry": {
        "description": "Cassandra retry policies. Handle read/write timeouts and unavailable exceptions.",
        "keywords": "Cassandra retry policy, timeout handling, unavailable exception"
    },
    "cassandra/application-development/drivers/policies/speculative-execution": {
        "description": "Cassandra speculative execution policy. Reduce tail latencies with parallel queries.",
        "keywords": "speculative execution, Cassandra latency, parallel queries"
    },
    "cassandra/application-development/drivers/prepared-statements": {
        "description": "Cassandra prepared statements guide. Optimize performance and prevent CQL injection.",
        "keywords": "Cassandra prepared statements, CQL performance, query optimization"
    },
    "cassandra/application-development/index": {
        "description": "Cassandra application development guide. Drivers, best practices, and data modeling.",
        "keywords": "Cassandra development, application development, Cassandra drivers"
    },
    "cassandra/application-development/workbench": {
        "description": "AxonOps Workbench for Cassandra development. GUI tool for schema design and query building.",
        "keywords": "AxonOps Workbench, Cassandra GUI, schema design, query builder"
    },

    # Cloud
    "cassandra/cloud/aws/index": {
        "description": "Deploy Cassandra on AWS. EC2 instances, EBS storage, and networking best practices.",
        "keywords": "Cassandra AWS, EC2 deployment, EBS storage, AWS best practices"
    },
    "cassandra/cloud/azure/index": {
        "description": "Deploy Cassandra on Microsoft Azure. Virtual machines, managed disks, and networking.",
        "keywords": "Cassandra Azure, Azure deployment, managed disks, Azure VMs"
    },
    "cassandra/cloud/gcp/index": {
        "description": "Deploy Cassandra on Google Cloud Platform. Compute Engine, persistent disks, and VPC setup.",
        "keywords": "Cassandra GCP, Google Cloud, Compute Engine, persistent disks"
    },
    "cassandra/cloud/index": {
        "description": "Cassandra cloud deployment options. AWS, Azure, GCP, and Kubernetes deployments.",
        "keywords": "Cassandra cloud, cloud deployment, AWS, Azure, GCP, Kubernetes"
    },
    "cassandra/cloud/kubernetes/index": {
        "description": "Deploy Cassandra on Kubernetes. Operators, StatefulSets, and container orchestration.",
        "keywords": "Cassandra Kubernetes, K8s deployment, StatefulSet, operators"
    },

    # Data Modeling
    "cassandra/data-modeling/anti-patterns/index": {
        "description": "Cassandra data modeling anti-patterns. Common mistakes and how to avoid them.",
        "keywords": "Cassandra anti-patterns, data modeling mistakes, design pitfalls"
    },
    "cassandra/data-modeling/concepts/index": {
        "description": "Cassandra data modeling concepts. Partition keys, clustering columns, and denormalization.",
        "keywords": "Cassandra data modeling, partition key, clustering column, denormalization"
    },
    "cassandra/data-modeling/examples/e-commerce": {
        "description": "E-commerce data model example for Cassandra. Product catalog, orders, and user profiles.",
        "keywords": "Cassandra e-commerce model, product catalog, order management"
    },
    "cassandra/data-modeling/index": {
        "description": "Cassandra data modeling guide. Design patterns, best practices, and examples.",
        "keywords": "Cassandra data modeling, schema design, data model patterns"
    },
    "cassandra/data-modeling/patterns/time-bucketing": {
        "description": "Time bucketing pattern for Cassandra. Manage time-series data with efficient partitions.",
        "keywords": "time bucketing, Cassandra time-series, partition management"
    },

    # Getting Started
    "cassandra/getting-started/drivers/index": {
        "description": "Getting started with Cassandra drivers. Quick setup guides for popular languages.",
        "keywords": "Cassandra drivers setup, quick start, language drivers"
    },
    "cassandra/getting-started/first-cluster": {
        "description": "Create your first Cassandra cluster. Step-by-step guide for beginners.",
        "keywords": "first Cassandra cluster, cluster setup, beginner guide"
    },
    "cassandra/getting-started/installation/index": {
        "description": "Cassandra installation guide. Install on Linux, macOS, and Windows.",
        "keywords": "Cassandra installation, install Cassandra, setup guide"
    },
    "cassandra/getting-started/production-checklist": {
        "description": "Cassandra production readiness checklist. Essential configurations before going live.",
        "keywords": "Cassandra production checklist, production readiness, deployment checklist"
    },
    "cassandra/getting-started/quickstart-cql": {
        "description": "CQL quickstart guide. Learn basic Cassandra Query Language operations.",
        "keywords": "CQL quickstart, Cassandra Query Language, CQL basics"
    },
    "cassandra/getting-started/what-is-cassandra": {
        "description": "What is Apache Cassandra. Distributed NoSQL database for high availability and scalability.",
        "keywords": "what is Cassandra, Apache Cassandra introduction, NoSQL database"
    },
    "cassandra/index": {
        "description": "Apache Cassandra documentation. Comprehensive guide for deployment, operations, and development.",
        "keywords": "Apache Cassandra docs, Cassandra documentation, Cassandra guide"
    },

    # Operations - Backup/Restore
    "cassandra/operations/backup-restore/backup": {
        "description": "Cassandra backup strategies. Snapshot-based and incremental backup methods.",
        "keywords": "Cassandra backup, snapshot backup, incremental backup"
    },
    "cassandra/operations/backup-restore/index": {
        "description": "Cassandra backup and restore overview. Strategies and tools for data protection.",
        "keywords": "Cassandra backup restore, data protection, backup strategies"
    },
    "cassandra/operations/backup-restore/restore": {
        "description": "Cassandra restore procedures. Recover data from snapshots and backups.",
        "keywords": "Cassandra restore, data recovery, snapshot restore"
    },

    # Operations - Cluster Management
    "cassandra/operations/cluster-management/adding-nodes": {
        "description": "Add nodes to Cassandra cluster. Scale out procedure and bootstrap process.",
        "keywords": "add Cassandra node, cluster scaling, bootstrap node"
    },
    "cassandra/operations/cluster-management/index": {
        "description": "Cassandra cluster management. Scaling, topology changes, and node operations.",
        "keywords": "Cassandra cluster management, cluster operations, node management"
    },

    # Operations - Compaction
    "cassandra/operations/compaction-management/index": {
        "description": "Cassandra compaction management. Strategies, tuning, and monitoring compaction.",
        "keywords": "Cassandra compaction, compaction strategies, STCS, LCS, TWCS"
    },

    # Operations - Configuration
    "cassandra/operations/configuration/cassandra-yaml/index": {
        "description": "Cassandra.yaml configuration reference. All settings for Cassandra nodes.",
        "keywords": "cassandra.yaml, Cassandra configuration, config reference"
    },
    "cassandra/operations/configuration/guardrails": {
        "description": "Cassandra guardrails configuration. Prevent dangerous operations and protect clusters.",
        "keywords": "Cassandra guardrails, operation limits, cluster protection"
    },
    "cassandra/operations/configuration/index": {
        "description": "Cassandra configuration overview. YAML files, JVM options, and runtime settings.",
        "keywords": "Cassandra configuration, config files, settings overview"
    },
    "cassandra/operations/configuration/jvm-options/index": {
        "description": "Cassandra JVM options configuration. Heap size, GC settings, and performance tuning.",
        "keywords": "Cassandra JVM options, heap size, garbage collection, JVM tuning"
    },
    "cassandra/operations/configuration/logback": {
        "description": "Cassandra logging configuration with Logback. Configure log levels and appenders.",
        "keywords": "Cassandra logback, logging configuration, log levels"
    },
    "cassandra/operations/configuration/snitch-config/index": {
        "description": "Cassandra snitch configuration. Data center and rack awareness settings.",
        "keywords": "Cassandra snitch, rack awareness, data center topology"
    },
    "cassandra/operations/index": {
        "description": "Cassandra operations guide. Day-to-day management and maintenance procedures.",
        "keywords": "Cassandra operations, cluster management, maintenance"
    },

    # Operations - JMX Reference
    "cassandra/operations/jmx-reference/connecting/index": {
        "description": "Connect to Cassandra JMX. Remote JMX setup and authentication configuration.",
        "keywords": "Cassandra JMX connection, remote JMX, JMX authentication"
    },
    "cassandra/operations/jmx-reference/index": {
        "description": "Cassandra JMX reference. MBeans, metrics, and management operations.",
        "keywords": "Cassandra JMX, MBeans reference, JMX metrics"
    },
    "cassandra/operations/jmx-reference/mbeans/index": {
        "description": "Cassandra MBeans reference. All available management beans and operations.",
        "keywords": "Cassandra MBeans, JMX management, MBean operations"
    },
    "cassandra/operations/jmx-reference/metrics/index": {
        "description": "Cassandra JMX metrics reference. Key metrics for monitoring and alerting.",
        "keywords": "Cassandra JMX metrics, monitoring metrics, performance metrics"
    },

    # Operations - Maintenance
    "cassandra/operations/maintenance/index": {
        "description": "Cassandra maintenance procedures. Routine tasks for healthy clusters.",
        "keywords": "Cassandra maintenance, routine maintenance, cluster health"
    },

    # Operations - Monitoring
    "cassandra/operations/monitoring/alerting/index": {
        "description": "Cassandra alerting configuration. Set up alerts for critical metrics.",
        "keywords": "Cassandra alerting, monitoring alerts, metric thresholds"
    },
    "cassandra/operations/monitoring/dashboards/grafana": {
        "description": "Grafana dashboards for Cassandra. Pre-built dashboards for visualization.",
        "keywords": "Cassandra Grafana, dashboards, metrics visualization"
    },
    "cassandra/operations/monitoring/index": {
        "description": "Cassandra monitoring overview. Tools, metrics, and best practices.",
        "keywords": "Cassandra monitoring, cluster monitoring, observability"
    },
    "cassandra/operations/monitoring/key-metrics/index": {
        "description": "Key Cassandra metrics to monitor. Essential metrics for cluster health.",
        "keywords": "Cassandra key metrics, essential metrics, monitoring priorities"
    },
    "cassandra/operations/monitoring/logging/index": {
        "description": "Cassandra logging overview. Log analysis and troubleshooting with logs.",
        "keywords": "Cassandra logging, log analysis, system.log"
    },

    # Operations - Performance
    "cassandra/operations/performance/benchmarking/index": {
        "description": "Cassandra benchmarking guide. Test performance with cassandra-stress.",
        "keywords": "Cassandra benchmarking, cassandra-stress, performance testing"
    },
    "cassandra/operations/performance/hardware/index": {
        "description": "Cassandra hardware recommendations. CPU, memory, storage, and network specs.",
        "keywords": "Cassandra hardware, server specs, hardware requirements"
    },
    "cassandra/operations/performance/index": {
        "description": "Cassandra performance tuning guide. Optimize throughput and latency.",
        "keywords": "Cassandra performance, tuning guide, optimization"
    },
    "cassandra/operations/performance/jvm-tuning/index": {
        "description": "Cassandra JVM tuning guide. Garbage collection and memory optimization.",
        "keywords": "Cassandra JVM tuning, GC tuning, memory optimization"
    },
    "cassandra/operations/performance/os-tuning/index": {
        "description": "Operating system tuning for Cassandra. Linux kernel and file system settings.",
        "keywords": "Cassandra OS tuning, Linux tuning, kernel settings"
    },
    "cassandra/operations/performance/query-optimization/index": {
        "description": "Cassandra query optimization. Improve CQL query performance.",
        "keywords": "Cassandra query optimization, CQL performance, slow queries"
    },

    # Operations - Repair
    "cassandra/operations/repair/concepts": {
        "description": "Cassandra repair concepts. Anti-entropy repair and consistency maintenance.",
        "keywords": "Cassandra repair concepts, anti-entropy, Merkle trees"
    },
    "cassandra/operations/repair/index": {
        "description": "Cassandra repair overview. Keep data consistent across replicas.",
        "keywords": "Cassandra repair, data consistency, repair operations"
    },
    "cassandra/operations/repair/options-reference": {
        "description": "Cassandra repair options reference. All nodetool repair flags and settings.",
        "keywords": "Cassandra repair options, nodetool repair flags, repair settings"
    },
    "cassandra/operations/repair/scheduling": {
        "description": "Cassandra repair scheduling. Automate repair with schedulers.",
        "keywords": "Cassandra repair scheduling, automated repair, repair scheduler"
    },
    "cassandra/operations/repair/strategies": {
        "description": "Cassandra repair strategies. Full vs incremental, subrange repairs.",
        "keywords": "Cassandra repair strategies, incremental repair, subrange repair"
    },

    # Operations - Troubleshooting
    "cassandra/operations/troubleshooting/index": {
        "description": "Cassandra troubleshooting guide. Diagnose and resolve common issues.",
        "keywords": "Cassandra troubleshooting, diagnosis, problem resolution"
    },

    # Reference
    "cassandra/reference/index": {
        "description": "Cassandra reference documentation. Project resources, links, and official guides.",
        "keywords": "Cassandra reference, documentation, project resources"
    },

    # Tools
    "cassandra/tools/cassandra-stress/index": {
        "description": "Cassandra-stress tool guide. Load testing and benchmarking Cassandra.",
        "keywords": "cassandra-stress, load testing, benchmarking tool"
    },
    "cassandra/tools/cqlsh/index": {
        "description": "CQLSH command-line shell for Cassandra. Interactive CQL query interface.",
        "keywords": "cqlsh, CQL shell, command line, interactive queries"
    },

    # Tools - CQLAI
    "cassandra/tools/cqlai/ai-features/ai-providers/index": {
        "description": "CQLAI AI providers configuration. Connect to OpenAI, Anthropic, and other models.",
        "keywords": "CQLAI AI providers, OpenAI, Anthropic, LLM configuration"
    },
    "cassandra/tools/cqlai/ai-features/index": {
        "description": "CQLAI AI features overview. Natural language queries and intelligent suggestions.",
        "keywords": "CQLAI AI features, natural language, intelligent suggestions"
    },
    "cassandra/tools/cqlai/commands/index": {
        "description": "CQLAI commands reference. All available shell commands and shortcuts.",
        "keywords": "CQLAI commands, shell commands, command reference"
    },
    "cassandra/tools/cqlai/configuration/index": {
        "description": "CQLAI configuration guide. Set up connections and customize behavior.",
        "keywords": "CQLAI configuration, setup, connection config"
    },
    "cassandra/tools/cqlai/data-import-export/index": {
        "description": "CQLAI data import and export. Load and extract data with various formats.",
        "keywords": "CQLAI import export, data loading, CSV, JSON"
    },
    "cassandra/tools/cqlai/features/index": {
        "description": "CQLAI features overview. All capabilities of the AI-powered CQL shell.",
        "keywords": "CQLAI features, shell capabilities, feature overview"
    },
    "cassandra/tools/cqlai/getting-started/index": {
        "description": "Getting started with CQLAI. Quick setup and first queries.",
        "keywords": "CQLAI getting started, quick start, first queries"
    },
    "cassandra/tools/cqlai/index": {
        "description": "CQLAI documentation. AI-powered CQL shell for Apache Cassandra.",
        "keywords": "CQLAI documentation, AI CQL shell, Cassandra tool"
    },
    "cassandra/tools/cqlai/installation/index": {
        "description": "CQLAI installation guide. Install on Linux, macOS, and Windows.",
        "keywords": "CQLAI installation, install CQLAI, setup guide"
    },
    "cassandra/tools/cqlai/parquet/index": {
        "description": "CQLAI Parquet support. Import and export Parquet files with Cassandra.",
        "keywords": "CQLAI Parquet, Parquet import, columnar data"
    },
    "cassandra/tools/cqlai/quickstart": {
        "description": "CQLAI quickstart guide. Get productive in minutes.",
        "keywords": "CQLAI quickstart, quick start, getting productive"
    },
    "cassandra/tools/cqlai/troubleshooting": {
        "description": "CQLAI troubleshooting guide. Common issues and solutions.",
        "keywords": "CQLAI troubleshooting, common issues, problem solving"
    },

    # Troubleshooting
    "cassandra/troubleshooting/common-errors/index": {
        "description": "Common Cassandra errors reference. Error messages and resolutions.",
        "keywords": "Cassandra errors, common errors, error messages"
    },
    "cassandra/troubleshooting/common-errors/read-timeout": {
        "description": "Cassandra ReadTimeout error. Causes and solutions for read timeouts.",
        "keywords": "Cassandra ReadTimeout, read timeout error, timeout troubleshooting"
    },
    "cassandra/troubleshooting/common-errors/write-timeout": {
        "description": "Cassandra WriteTimeout error. Causes and solutions for write timeouts.",
        "keywords": "Cassandra WriteTimeout, write timeout error, timeout troubleshooting"
    },
    "cassandra/troubleshooting/playbooks/add-node": {
        "description": "Add node troubleshooting playbook. Debug node bootstrap issues.",
        "keywords": "add node troubleshooting, bootstrap issues, node problems"
    },
    "cassandra/troubleshooting/playbooks/compaction-issues": {
        "description": "Compaction issues troubleshooting playbook. Diagnose compaction problems.",
        "keywords": "compaction troubleshooting, compaction issues, stuck compaction"
    },
    "cassandra/troubleshooting/playbooks/decommission-node": {
        "description": "Decommission node troubleshooting playbook. Handle decommission failures.",
        "keywords": "decommission troubleshooting, node removal, decommission issues"
    },
    "cassandra/troubleshooting/playbooks/gc-pause": {
        "description": "GC pause troubleshooting playbook. Diagnose garbage collection issues.",
        "keywords": "GC pause troubleshooting, garbage collection, JVM GC issues"
    },
    "cassandra/troubleshooting/playbooks/gossip-failures": {
        "description": "Gossip failures troubleshooting playbook. Debug cluster communication.",
        "keywords": "gossip troubleshooting, gossip failures, cluster communication"
    },
    "cassandra/troubleshooting/playbooks/handle-full-disk": {
        "description": "Full disk troubleshooting playbook. Handle disk space emergencies.",
        "keywords": "full disk troubleshooting, disk space, storage emergency"
    },
    "cassandra/troubleshooting/playbooks/high-cpu": {
        "description": "High CPU troubleshooting playbook. Diagnose CPU-bound issues.",
        "keywords": "high CPU troubleshooting, CPU issues, performance problems"
    },
    "cassandra/troubleshooting/playbooks/high-memory": {
        "description": "High memory troubleshooting playbook. Debug memory pressure issues.",
        "keywords": "high memory troubleshooting, memory issues, heap pressure"
    },
    "cassandra/troubleshooting/playbooks/index": {
        "description": "Cassandra troubleshooting playbooks index. Runbooks for common issues.",
        "keywords": "troubleshooting playbooks, runbooks, operational guides"
    },
    "cassandra/troubleshooting/playbooks/large-partition": {
        "description": "Large partition troubleshooting playbook. Handle oversized partitions.",
        "keywords": "large partition troubleshooting, partition size, hot partitions"
    },
    "cassandra/troubleshooting/playbooks/recover-from-oom": {
        "description": "OOM recovery troubleshooting playbook. Recover from out-of-memory crashes.",
        "keywords": "OOM recovery, out of memory, crash recovery"
    },
    "cassandra/troubleshooting/playbooks/repair-failures": {
        "description": "Repair failures troubleshooting playbook. Debug failed repair operations.",
        "keywords": "repair failures troubleshooting, failed repair, repair issues"
    },
    "cassandra/troubleshooting/playbooks/replace-dead-node": {
        "description": "Replace dead node troubleshooting playbook. Node replacement procedures.",
        "keywords": "replace node troubleshooting, dead node, node replacement"
    },
    "cassandra/troubleshooting/playbooks/schema-disagreement": {
        "description": "Schema disagreement troubleshooting playbook. Resolve schema conflicts.",
        "keywords": "schema disagreement, schema conflict, metadata issues"
    },
    "cassandra/troubleshooting/playbooks/slow-queries": {
        "description": "Slow queries troubleshooting playbook. Diagnose query performance.",
        "keywords": "slow queries troubleshooting, query performance, latency issues"
    },
    "cassandra/troubleshooting/playbooks/tombstone-accumulation": {
        "description": "Tombstone accumulation troubleshooting playbook. Handle tombstone warnings.",
        "keywords": "tombstone troubleshooting, tombstone accumulation, delete markers"
    },

    # Other remaining files
    "data-platforms/index": {
        "description": "AxonOps supported data platforms. Cassandra and Kafka monitoring overview.",
        "keywords": "data platforms, AxonOps platforms, Cassandra, Kafka"
    },
    "installation/kubernetes/index": {
        "description": "AxonOps Kubernetes installation. Deploy monitoring in K8s clusters.",
        "keywords": "AxonOps Kubernetes, K8s installation, container deployment"
    },
    "installation/kubernetes/minikube": {
        "description": "AxonOps Minikube installation. Local Kubernetes development setup.",
        "keywords": "AxonOps Minikube, local Kubernetes, development environment"
    },
    "kafka/index": {
        "description": "Kafka management with AxonOps. Broker monitoring, topic management, and more.",
        "keywords": "Kafka management, AxonOps Kafka, broker monitoring, topics"
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

    for key, meta in CASSANDRA_META.items():
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
