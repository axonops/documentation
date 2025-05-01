<h2>Step 2 - Install Kafka Agent </h2>

{!dynamic_pages/axon_agent/kafka_agent.md!}

<h2>Step 3 - Agent Configuration </h2>

<p>Update the following highlighted lines from <code>/etc/axonops/axon-agent.yml</code>:</p>

<p>Please update the <strong>key</strong> and <strong>org</strong> values, they can be viewed by logging into <a href="https://console.axonops.cloud" target="_blank">console.axonops.cloud</a></p>
<ul>
<li><strong>Organization(org)</strong> name is next to the logo in the console</li>
<li><strong>Agent Keys(key)</strong> found in Agent Setup</li>
</ul>
<p><img src="/get_started/agent_keys.png" /></p>

If there is a Dedicated NTP server in your Organization please uncomment and update the NTP section. 

{!dynamic_pages/axon_agent/kafka_agent_config.md!}