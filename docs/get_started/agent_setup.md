---
hide:
  - toc
---

# Axon Agent Setup
<!-- ![](agent_steps.png) -->

## AxonOps Cloud Agent Network Requirements

AxonOps agent connects securely to the following AxonOps Cloud service endpoint;

``` { .bash .no-copy }
https://agents.axonops.cloud
```

The TLS HTTPS connection initiated by the agent is upgraded to a WebSocket connection and thus requires WebSocket support in your corporate infrastructure, such as a secure web proxy service.

If you have a DNS based security policy then you will be required to allow outbound access to the following domain.

``` { .bash .no-copy }
agents.axonops.cloud
```

If you have an IP address based security policy you will be required to open access to the IP address ranges provided in the following links.

``` { .bash .no-copy }
https://agents.axonops.cloud/ips-v4
https://agents.axonops.cloud/ips-v6
```

In order to test your connectivity execute the following command:

``` { .bash .copy }
curl https://agents.axonops.cloud/test.html
```

You should expect the following response:

*AxonOps Agent Test Page*

## Setup the AxonOps repository and install AxonOps Agent

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

<div id="CassandraDiv" name="service_div" markdown="1">

{!get_started/agent_setup_cassandra.md!}

</div>

<div id="KafkaDiv" name="service_div" style="display:none" markdown="1">

{!get_started/agent_setup_kafka.md!}

</div>

## Start axon-agent

```
sudo systemctl start axon-agent
```

Once the Agents have been setup please use the [Using AxonOps](/cluster/cluster-overview/) to familiarise yourself with AxonOps UI.