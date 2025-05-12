<h2>Step 2 - Install Kafka Agent </h2>

{!dynamic_pages/axon_agent/kafka_agent.md!}

<blockquote>
<p>Note: This will install the AxonOps Kafka agent and its dependency: <strong>axon-agent</strong></p>
</blockquote>

<h2>Step 3 - Agent Configuration </h2>

<p>Update the AxonOps Agent Service file:</p>

```shell
echo "kafka" > /var/lib/axonops/agent_service
```

<p>Update the highlighted lines in <code>/etc/axonops/axon-agent.yml</code>:</p>

These need to match the config that you have in your axon-server.yml setup.

{!dynamic_pages/axon_agent/kafka_agent_config.md!}