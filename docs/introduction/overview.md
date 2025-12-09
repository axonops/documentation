# Introduction to AxonOps

<style>
  video {
    max-width: 100%;
    width: 100%;
    display: block;
  }
</style>

<script>
  document.addEventListener('DOMContentLoaded', function() {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('presales')) {
      document.body.classList.add('presales-mode');
    }
  });
</script>

<div style="position: relative; padding-top: 56.25%;">
  <iframe
    src="https://customer-e7nrn6nt0ozdk9tl.cloudflarestream.com/76769890028e91aa27d91f6562448394/iframe?muted=true&preload=true&loop=true&autoplay=true&poster=https%3A%2F%2Fcustomer-e7nrn6nt0ozdk9tl.cloudflarestream.com%2F76769890028e91aa27d91f6562448394%2Fthumbnails%2Fthumbnail.jpg%3Ftime%3D%26height%3D600"
    loading="lazy"
    style="border: none; position: absolute; top: 0; left: 0; height: 100%; width: 100%;"
    allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
    allowfullscreen="true"
  ></iframe>
</div>

AxonOps is a comprehensive platform for managing and monitoring Apache Cassandra and Apache Kafka. From observability and alerting to automated operations like repairs, backups, and rolling restarts, AxonOps provides everything you need to run production clusters confidently without requiring deep distributed systems expertise on your team.


## Unified Observability

### Cluster View

<div style="position: relative; padding-top: 56.25%;">
  <iframe
    src="https://customer-e7nrn6nt0ozdk9tl.cloudflarestream.com/5e1b6de8a7c6cee94a389ca23a753fad/iframe?muted=true&preload=true&loop=true&autoplay=true&poster=https%3A%2F%2Fcustomer-e7nrn6nt0ozdk9tl.cloudflarestream.com%2F5e1b6de8a7c6cee94a389ca23a753fad%2Fthumbnails%2Fthumbnail.jpg%3Ftime%3D%26height%3D600"
    loading="lazy"
    style="border: none; position: absolute; top: 0; left: 0; height: 100%; width: 100%;"
    allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
    allowfullscreen="true"
  ></iframe>
</div>


The Cluster Overview gives you instant visibility into node health, service status, and cluster configuration, whether you're troubleshooting an incident at 3 AM or planning capacity expansion. AxonOps provides a unified topology view that visualizes your entire distributed infrastructure in a single intuitive interface, eliminating the need for SSH sessions, manual host inventories, and jumping between disparate tools.

This consolidated perspective transforms cluster management from a scattered, knowledge intensive task into a straightforward visual experience that any team member can navigate, regardless of their Cassandra or Kafka expertise. Learn more about [Cluster View](cluster-view.md).


### Dashboards

<div style="position: relative; padding-top: 56.25%;">
  <iframe
    src="https://customer-e7nrn6nt0ozdk9tl.cloudflarestream.com/036eec9c63346ec5978d6603c975374f/iframe?muted=true&preload=true&loop=true&autoplay=true&poster=https%3A%2F%2Fcustomer-e7nrn6nt0ozdk9tl.cloudflarestream.com%2F036eec9c63346ec5978d6603c975374f%2Fthumbnails%2Fthumbnail.jpg%3Ftime%3D%26height%3D600"
    loading="lazy"
    style="border: none; position: absolute; top: 0; left: 0; height: 100%; width: 100%;"
    allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
    allowfullscreen="true"
  ></iframe>
</div>

Understanding what's actually happening inside your Cassandra and Kafka clusters shouldn't require assembling a patchwork of monitoring tools or spending months figuring out which metrics matter. AxonOps delivers pre-configured dashboards built from decades of real world production experience across enterprises, startups, and everything in between, spanning diverse geographical deployments and use cases.

These aren't generic monitoring templates. Every dashboard reflects hard won knowledge about what actually indicates trouble, which metrics correlate during incidents, and how to organize information so you can diagnose issues in minutes instead of hours. The result is immediate operational intelligence without the trial and error, giving your team the insight that typically takes years of Cassandra battle scars to develop. Learn more about [Dashboards](dashboards.md).


### Event Logs

<div style="position: relative; padding-top: 56.25%;">
  <iframe
    src="https://customer-e7nrn6nt0ozdk9tl.cloudflarestream.com/996ed10f1b950ee926f14df9d931b01a/iframe?muted=true&preload=true&loop=true&autoplay=true&poster=https%3A%2F%2Fcustomer-e7nrn6nt0ozdk9tl.cloudflarestream.com%2F996ed10f1b950ee926f14df9d931b01a%2Fthumbnails%2Fthumbnail.jpg%3Ftime%3D%26height%3D600"
    loading="lazy"
    style="border: none; position: absolute; top: 0; left: 0; height: 100%; width: 100%;"
    allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
    allowfullscreen="true"
  ></iframe>
</div>

When something goes wrong in a distributed system, the answer is usually buried in log files scattered across dozens or hundreds of nodes. AxonOps brings all your Cassandra and Kafka logs into a unified search interface, letting you hunt down authentication failures, schema changes, compaction events, and errors without SSH-ing into individual servers or maintaining separate log aggregation infrastructure.

The real power comes from correlation. Spot a latency spike in a dashboard? Click directly into the time window and search logs from that exact moment across your entire cluster. Filter by datacenter, rack, node, severity, or regex patterns to pinpoint root causes fast, turning what used to be hours of investigation into focused diagnostics so you can get back to shipping features instead of fighting fires. Learn more about [Event Logs](event-logs.md).


## Active Monitoring

### Alerts

<div style="position: relative; padding-top: 56.25%;">
  <iframe
    src="https://customer-e7nrn6nt0ozdk9tl.cloudflarestream.com/0d6c7a294bb18a5567a7eeaba7d8c43d/iframe?muted=true&preload=true&loop=true&autoplay=true&poster=https%3A%2F%2Fcustomer-e7nrn6nt0ozdk9tl.cloudflarestream.com%2F0d6c7a294bb18a5567a7eeaba7d8c43d%2Fthumbnails%2Fthumbnail.jpg%3Ftime%3D%26height%3D600"
    loading="lazy"
    style="border: none; position: absolute; top: 0; left: 0; height: 100%; width: 100%;"
    allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
    allowfullscreen="true"
  ></iframe>
</div>

The difference between a well monitored system and alert fatigue is knowing what deserves attention and routing it to the right people at the right time. AxonOps lets you define metric thresholds directly from dashboard charts and route notifications through your existing workflow tools like PagerDuty, Slack, ServiceNow, or OpsGenie based on severity and alert type.

Stop configuring complex alerting rules across multiple systems or waking up the entire team for every minor blip. Intelligent routing means backup failures go to your operations team, performance degradation alerts your database specialists, and informational events flow to Slack channels where they belong, keeping everyone informed without the noise. Learn more about [Alerts](alerts.md).


### Service Checks

<div style="position: relative; padding-top: 56.25%;">
  <iframe
    src="https://customer-e7nrn6nt0ozdk9tl.cloudflarestream.com/e00ec30b7f79bf65cf6ab8786d819329/iframe?muted=true&preload=true&loop=true&autoplay=true&poster=https%3A%2F%2Fcustomer-e7nrn6nt0ozdk9tl.cloudflarestream.com%2Fe00ec30b7f79bf65cf6ab8786d819329%2Fthumbnails%2Fthumbnail.jpg%3Ftime%3D%26height%3D600"
    loading="lazy"
    style="border: none; position: absolute; top: 0; left: 0; height: 100%; width: 100%;"
    allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
    allowfullscreen="true"
  ></iframe>
</div>

Metrics tell you how your system is performing, but service checks tell you if it's actually working. AxonOps provides proactive health monitoring through customizable shell scripts, HTTP endpoint checks, and TCP connectivity tests that run continuously across your infrastructure, surfacing issues before they cascade into outages.

These checks are automatically deployed to your agents without manual configuration on every node, giving you Red/Amber/Green confidence indicators at a glance. Whether you're validating that your application endpoints respond correctly, ensuring backup scripts execute successfully, or confirming connectivity to external services, service checks close the gap between system metrics and real world availability. Learn more about [Service Checks](service-checks.md).


### Integrations

<div style="position: relative; padding-top: 56.25%;">
  <iframe
    src="https://customer-e7nrn6nt0ozdk9tl.cloudflarestream.com/4b772c370349eeeb7b54d4bb2e9d172a/iframe?muted=true&preload=true&loop=true&autoplay=true&poster=https%3A%2F%2Fcustomer-e7nrn6nt0ozdk9tl.cloudflarestream.com%2F4b772c370349eeeb7b54d4bb2e9d172a%2Fthumbnails%2Fthumbnail.jpg%3Ftime%3D%26height%3D600"
    loading="lazy"
    style="border: none; position: absolute; top: 0; left: 0; height: 100%; width: 100%;"
    allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
    allowfullscreen="true"
  ></iframe>
</div>

Effective monitoring should amplify your existing operational processes, not force you to abandon the tools your teams already rely on. AxonOps integrates with PagerDuty and OpsGenie for incident management, Slack and Microsoft Teams for collaboration, ServiceNow for ticketing, and SMTP for email notifications, fitting seamlessly into the way your organization already works.

Sophisticated routing lets you send different alert types to different destinations based on severity and category. Critical backup failures can page your on-call team through PagerDuty while informational repair completions flow to a Slack channel, ensuring the right information reaches the right people through the channels they already monitor. Learn more about [Integrations](integrations.md).


## Automated Operations

### Rolling Restarts

<div style="position: relative; padding-top: 56.25%;">
  <iframe
    src="https://customer-e7nrn6nt0ozdk9tl.cloudflarestream.com/34fda982a8e0799038feeb849cbd1e95/iframe?muted=true&preload=true&loop=true&autoplay=true&poster=https%3A%2F%2Fcustomer-e7nrn6nt0ozdk9tl.cloudflarestream.com%2F34fda982a8e0799038feeb849cbd1e95%2Fthumbnails%2Fthumbnail.jpg%3Ftime%3D%26height%3D600"
    loading="lazy"
    style="border: none; position: absolute; top: 0; left: 0; height: 100%; width: 100%;"
    allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
    allowfullscreen="true"
  ></iframe>
</div>

Restarting a distributed cluster for configuration changes, upgrades, or patches shouldn't mean hours of manual server access and hoping you remembered the correct sequence. AxonOps orchestrates rolling restarts across your Cassandra and Kafka clusters with configurable parallelism at the datacenter, rack, and node levels, executing restarts safely while maintaining cluster availability.

Schedule restarts for maintenance windows or execute them immediately when needed. Customize the restart scripts to fit your environment, and let AxonOps handle the orchestration. What used to require careful runbooks and multiple engineers becomes a guided operation that runs reliably every time. Learn more about [Rolling Restarts](rolling-restarts.md).


## Cassandra Operations

### Repairs

<div style="position: relative; padding-top: 56.25%;">
  <iframe
    src="https://customer-e7nrn6nt0ozdk9tl.cloudflarestream.com/910960f7e4e6fa708c2325d09c0ea45e/iframe?muted=true&preload=true&loop=true&autoplay=true&poster=https%3A%2F%2Fcustomer-e7nrn6nt0ozdk9tl.cloudflarestream.com%2F910960f7e4e6fa708c2325d09c0ea45e%2Fthumbnails%2Fthumbnail.jpg%3Ftime%3D%26height%3D600"
    loading="lazy"
    style="border: none; position: absolute; top: 0; left: 0; height: 100%; width: 100%;"
    allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
    allowfullscreen="true"
  ></iframe>
</div>

Cassandra repairs are essential for data integrity, but they're notoriously difficult to execute correctly without impacting production performance. AxonOps Adaptive Repair eliminates the guesswork with intelligent, hands-free automation that continuously monitors your cluster's workload and adjusts repair velocity in real time based on CPU utilization, query latencies, and I/O patterns.

This isn't a scheduled job that runs blindly. Adaptive Repair slows down when it detects load and speeds up when resources are available, ensuring repairs complete within gc_grace_seconds without affecting your applications. Your data stays consistent, your SLAs stay green, and your team stays focused on building products instead of babysitting repair jobs. Learn more about [Repairs](repairs.md).


### Backups

<div style="position: relative; padding-top: 56.25%;">
  <iframe
    src="https://customer-e7nrn6nt0ozdk9tl.cloudflarestream.com/7f63f96656425c695ec2f0a0428ef79a/iframe?muted=true&preload=true&loop=true&autoplay=true&poster=https%3A%2F%2Fcustomer-e7nrn6nt0ozdk9tl.cloudflarestream.com%2F7f63f96656425c695ec2f0a0428ef79a%2Fthumbnails%2Fthumbnail.jpg%3Ftime%3D%26height%3D600"
    loading="lazy"
    style="border: none; position: absolute; top: 0; left: 0; height: 100%; width: 100%;"
    allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
    allowfullscreen="true"
  ></iframe>
</div>

Data loss isn't an option, but configuring reliable backup strategies across distributed Cassandra clusters traditionally requires custom scripts, careful scheduling, and constant validation. AxonOps provides GUI-driven backup configuration with support for AWS S3, Google Cloud Storage, Azure Blob Storage, SFTP, and local storage, letting you schedule immediate or recurring backups without writing a single line of code.

Beyond simple backups, AxonOps includes point-in-time recovery through automated commitlog archiving, giving you the ability to restore to any precise moment. Whether you need to recover a single node, rebuild an entire cluster, or restore to a different environment altogether, the process is streamlined and reliable, turning disaster recovery from a dreaded procedure into a confident operational capability. Learn more about [Backups](backups.md).


## Kafka Monitoring

### Broker Monitoring

<div style="position: relative; padding-top: 56.25%;">
  <iframe
    src="https://customer-e7nrn6nt0ozdk9tl.cloudflarestream.com/1ca32022c98d3d2edb4b7c9f6733a5bd/iframe?muted=true&preload=true&loop=true&autoplay=true&poster=https%3A%2F%2Fcustomer-e7nrn6nt0ozdk9tl.cloudflarestream.com%2F1ca32022c98d3d2edb4b7c9f6733a5bd%2Fthumbnails%2Fthumbnail.jpg%3Ftime%3D%26height%3D600"
    loading="lazy"
    style="border: none; position: absolute; top: 0; left: 0; height: 100%; width: 100%;"
    allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
    allowfullscreen="true"
  ></iframe>
</div>

Comprehensive visibility into controller status, partition distribution, replication health, performance metrics, and system resource utilization organized exactly where you need them. Learn more about [Broker Monitoring](kafka-brokers.md).


### Consumer Tracking

<div style="position: relative; padding-top: 56.25%;">
  <iframe
    src="https://customer-e7nrn6nt0ozdk9tl.cloudflarestream.com/35bddbbd01e800e73f102fe0a6d0bee9/iframe?muted=true&preload=true&loop=true&autoplay=true&poster=https%3A%2F%2Fcustomer-e7nrn6nt0ozdk9tl.cloudflarestream.com%2F35bddbbd01e800e73f102fe0a6d0bee9%2Fthumbnails%2Fthumbnail.jpg%3Ftime%3D%26height%3D600"
    loading="lazy"
    style="border: none; position: absolute; top: 0; left: 0; height: 100%; width: 100%;"
    allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
    allowfullscreen="true"
  ></iframe>
</div>

Real-time lag visibility for every consumer group with alerts on thresholds that matter for your SLAs. Drill into partition assignments and understand which consumers are keeping up versus falling behind. Learn more about [Consumer Tracking](kafka-consumers.md).


### Kafka Connect

<div style="position: relative; padding-top: 56.25%;">
  <iframe
    src="https://customer-e7nrn6nt0ozdk9tl.cloudflarestream.com/91f327a34a384dc22d271c9efe72b83d/iframe?muted=true&preload=true&loop=true&autoplay=true&poster=https%3A%2F%2Fcustomer-e7nrn6nt0ozdk9tl.cloudflarestream.com%2F91f327a34a384dc22d271c9efe72b83d%2Fthumbnails%2Fthumbnail.jpg%3Ftime%3D%26height%3D600"
    loading="lazy"
    style="border: none; position: absolute; top: 0; left: 0; height: 100%; width: 100%;"
    allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
    allowfullscreen="true"
  ></iframe>
</div>

Comprehensive monitoring showing worker status, task health, connector throughput, and error rates for your data integration pipelines. Learn more about [Kafka Connect](kafka-connect.md).


## Kafka Operations

### Topic Management

<div style="position: relative; padding-top: 56.25%;">
  <iframe
    src="https://customer-e7nrn6nt0ozdk9tl.cloudflarestream.com/19db702178db8f95c0b6adc7b627072d/iframe?muted=true&preload=true&loop=true&autoplay=true&poster=https%3A%2F%2Fcustomer-e7nrn6nt0ozdk9tl.cloudflarestream.com%2F19db702178db8f95c0b6adc7b627072d%2Fthumbnails%2Fthumbnail.jpg%3Ftime%3D%26height%3D600"
    loading="lazy"
    style="border: none; position: absolute; top: 0; left: 0; height: 100%; width: 100%;"
    allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
    allowfullscreen="true"
  ></iframe>
</div>

GUI-driven topic creation, configuration editing, cloning, and deletion without command line complexity. View partition distribution, ISR status, and current consumers for any topic. Learn more about [Topic Management](kafka-topics.md).


### ACL Administration

<div style="position: relative; padding-top: 56.25%;">
  <iframe
    src="https://customer-e7nrn6nt0ozdk9tl.cloudflarestream.com/0d161e3395ab1f452e27c6e5125a9573/iframe?muted=true&preload=true&loop=true&autoplay=true&poster=https%3A%2F%2Fcustomer-e7nrn6nt0ozdk9tl.cloudflarestream.com%2F0d161e3395ab1f452e27c6e5125a9573%2Fthumbnails%2Fthumbnail.jpg%3Ftime%3D%26height%3D600"
    loading="lazy"
    style="border: none; position: absolute; top: 0; left: 0; height: 100%; width: 100%;"
    allow="accelerometer; gyroscope; autoplay; encrypted-media; picture-in-picture;"
    allowfullscreen="true"
  ></iframe>
</div>

Intuitive interface for security governance. View existing ACLs organized by resource, create access rules specifying principals and operations, configure permissions with full context about access being granted. Learn more about [ACL Administration](kafka-acls.md).

