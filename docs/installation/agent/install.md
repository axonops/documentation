---
hide:
  - toc
---

# AxonOps agent installation

This agent will enable metrics, logs and events collection along with adaptive repairs and/or backups.

See [Installing axon-agent for Cassandra in Docker](./docker.md) if you are running Cassandra under Docker.

## AxonOps Agent is a available for the followig versions of Apache Casssandra and Apache Kafka

### Cassandra
* Apache Cassandra 3.0.x
* Apache Cassandra 3.11.x
* Apache Cassandra 4.0.x
* Apache Cassandra 4.1.x
* Apache Cassandra 5.0.x

### Kafka
* Apache Kafa 2.x
* Apache Kafa 3.x


## Step 1 - Setup the AxonOps repository and install AxonOps Agent

{!dynamic_pages/axon_agent/os.md!}

### Select the Service you want to configure 
<label>
  <input type="radio" id="Cassandra" name="Service" onChange="updateService()" checked=true />
  <img src="/get_started/cassandra.png" class="skip-lightbox" width="180px" height="180px">
</label>
<label>
  <input type="radio" id="Kafka" name="Service" onChange="updateService()" />
  <img src="/get_started/kafka.png" class="skip-lightbox" width="180px" height="180px">
</label>

<div id="CassandraDiv" name="service_div">
    {!installation/agent/agent_setup_cassandra.md!}
</div>

<div id="KafkaDiv" name="service_div" style="display:none">
    {!installation/agent/agent_setup_kafka.md!}
</div>

## Step 7 - Start axon-agent
``` bash
sudo systemctl start axon-agent
```

<div id="CassandraDiv" name="service_div">

<h2>(Optional) Step 8 - Cassandra Remote Backups or Restore Prerequisites</h2>
<ul>
<li><p>If you plan to use AxonOps remote backup functionality, <strong>axonops</strong> user will require <strong>read</strong> access on Cassandra <strong>data</strong> folder.</p>
</li>
<li><p>As well if you plan to Restore data with AxonOps,  <strong>axonops</strong> user will require <strong>write</strong> access to Cassandra <strong>data</strong> folder. We recommend to only provide temporary write access to <strong>axonops</strong> when required.</p>
</li>
</ul>
<br/>
<br/>
<h4>Cassandra agent Package details</h4>
<ul>
<li>Configuration: <code>/etc/axonops/axon-agent.yml</code></li>
<li>Binary: <code>/usr/share/axonops/axon-cassandra{version}-agent.jar</code></li>
<li>Version number: <code>/usr/share/axonops/axon-cassandra{version}-agent.version</code></li>
<li>Copyright : <code>/usr/share/doc/axonops/axon-cassandra{version}-agent/copyright</code></li>
<li>Licenses : <code>/usr/share/axonops/licenses/axon-cassandra{version}-agent/</code></li>
</ul>
<h4>axon-agent Package details (dependency of Cassandra agent)</h4>
<ul>
<li>Configuration: <code>/etc/axonops/axon-agent.yml</code></li>
<li>Binary: <code>usr/share/axonops/axon-agent</code></li>
<li>Logs : <code>/var/log/axonops/axon-agent.log</code></li>
<li>Systemd service: <code>/usr/lib/systemd/system/axon-agent.service</code></li>
</ul>
</div>

<div id="KafkaDiv" name="service_div" style="display:none">
<br/>
<br/>
<h4>Kafka agent Package details</h4>
<ul>
<li>Configuration: <code>/etc/axonops/axon-agent.yml</code></li>
<li>Binary: <code>/usr/share/axonops/axon-kafka{version}-agent.jar</code></li>
<li>Version number: <code>/usr/share/axonops/axon-kafka{version}-agent.version</code></li>
<li>Copyright : <code>/usr/share/doc/axonops/axon-kafka{version}-agent/copyright</code></li>
<li>Licenses : <code>/usr/share/axonops/licenses/axon-kafka{version}-agent/</code></li>
</ul>
<h4>axon-agent Package details (dependency of Kafka agent)</h4>
<ul>
<li>Configuration: <code>/etc/axonops/axon-agent.yml</code></li>
<li>Binary: <code>usr/share/axonops/axon-agent</code></li>
<li>Logs : <code>/var/log/axonops/axon-agent.log</code></li>
<li>Systemd service: <code>/usr/lib/systemd/system/axon-agent.service</code></li>
</ul>
</div>


