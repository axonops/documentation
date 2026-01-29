---
title: "AxonOps Agent Set up"
hide:
  - toc
---

# AxonOps Agent Set up
<!-- ![agent_steps](agent_steps.png) -->

## AxonOps Cloud Agent Network Requirements

The AxonOps agent connects securely to the following AxonOps Cloud service endpoint:

``` { .bash .no-copy }
https://agents.axonops.cloud
```

The TLS HTTPS connection initiated by the agent is upgraded to a WebSocket connection and thus requires WebSocket support in your corporate infrastructure, such as a secure web proxy service.

If you have a DNS-based security policy, you must allow outbound access to the following domain.

``` { .bash .no-copy }
agents.axonops.cloud
```

If you have an IP address-based security policy, you must open access to the IP address ranges provided in the following links.

``` { .bash .no-copy }
https://agents.axonops.cloud/ips-v4
https://agents.axonops.cloud/ips-v6
```

To test connectivity, execute the following command:

``` { .bash .copy }
curl https://agents.axonops.cloud/test.html
```

You should expect the following response:

*AxonOps Agent Test Page*

## Set up the AxonOps repository and install the AxonOps agent

{!dynamic_pages/axon_agent/os.md!}

### Select the service you want to configure
<label>
  <input type="radio" id="Cassandra" name="Service" onChange="updateService()" checked=true />
  <img src="/get_started/cassandra.png" class="skip-lightbox" width="180px" height="180px" alt="cassandra">
</label>
<label>
  <input type="radio" id="Kafka" name="Service" onChange="updateService()" />
  <img src="/get_started/kafka.png" class="skip-lightbox" width="180px" height="180px" alt="kafka">
</label>

<div id="CassandraDiv" name="service_div" markdown="1">

{!get_started/agent_setup_cassandra.md!}

</div>

<div id="KafkaDiv" name="service_div" style="display:none" markdown="1">

{!get_started/agent_setup_kafka.md!}

</div>

## AxonOps agent behind a proxy

If your network does not have direct internet access and it requires a proxy to connect to the AxonOps Server, follow
[these instructions](proxy.md).

## Start the AxonOps agent

```
sudo systemctl start axon-agent
```

Once the agent is set up, use the [Using AxonOps](../cluster/cluster-overview.md) guide to familiarize yourself with the AxonOps UI.
