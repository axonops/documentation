<h2>Install Cassandra Agent </h2>

{!dynamic_pages/axon_agent/cassandra_agent.md!}

<h2>Agent Configuration </h2>

<p>Update the following highlighted lines from <code>/etc/axonops/axon-agent.yml</code>:</p>
<p>Please update the <strong>key</strong> and <strong>org</strong> values, they can be viewed by logging into <a href="https://console.axonops.cloud" target="_blank">console.axonops.cloud</a></p>
<ul>
<li><strong>Organization (org)</strong> name is next to the logo in the console</li>
<li><strong>Agent Keys (key)</strong> found in Agent Setup</li>
</ul>
<p><img src="/get_started/agent_keys.png" /></p>

If there is a Dedicated NTP server in your Organization please uncomment and update the NTP section. 

```
  axon-server:
      hosts: "agents.axonops.cloud"
  
  axon-agent:
      key: <THIS_IS_A_DUMMY_KEY_PLEASE_UPDATE>
      org: <THIS_IS_A_DUMMY_ORG_NAME_PLEASE_UPDATE>

  # Specify the NTP server IP addresses or hostnames configured for your Cassandra hosts
  # if using Cassandra deployed in Kubernetes or if auto-detection fails.
  # The port defaults to 123 if not specified.
  # NTP:
  #    hosts:
  #        - "x.x.x.x:123"
  # Optionally restrict which commands can be executed by axon-agent.
  # If "true", only scripts placed in scripts_location can be executed by axon-agent.
  # disable_command_exec: false
  # If disable_command_exec is true then axon-agent is only allowed to execute scripts
  # under this path
  # scripts_location: /var/lib/axonops/scripts/
```

Set file permissions on /etc/axonops/axon-agent.yml file by executing the following command

```
sudo chmod 0640 /etc/axonops/axon-agent.yml
```

<h2>Configure Cassandra</h2>

{!dynamic_pages/axon_agent/java.md!}

<h2>Start/Restart Cassandra</h2>

To load the AxonOps Java Agent and Cassandra config changes please,

<ul>
<li>Start the Cassandra service if stopped. </li>
<li>Restart the Cassandra service if already running.</li>
</ul>