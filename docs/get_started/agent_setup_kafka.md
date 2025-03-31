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

```yaml
kafka:
    node_type: "kraft-controller" # broker, kraft-broker, kraft-controller, zookeeper, connect
    config:
      kafka:
        brokers: ["host_listener_address:9092"]
        # Authentication Settings
        sasl:
          enabled: true
          username: <THIS_IS_A_DUMMY_USERNAME_PLEASE_UPDATE>
          password: <THIS_IS_A_DUMMY_PASSWORD_PLEASE_UPDATE>
          mechanism: PLAIN # SCRAM-SHA-256, SCRAM-SHA-512, OAUTHBEARER, GSSAPI
          # For oauth support
          # oauth:
          #   token:
          #   clientId:
          #   clientSecret:
          #   tokenEndpoint:
          #   scope:
          # For gsappi support
          # gsappi:
          #   authType:
          #   keyTabPath:
          #   kerberosConfigPath:
          #   serviceName:
          #   username:
          #   password:
          #   realm:
          #   enableFast: true
        # SSL settings for connection to Kafka
        tls:
          enabled: true
          caFilepath: <THIS_IS_A_DUMMY_CA_PATH_PLEASE_UPDATE>
          insecureSkipTlsVerify: false
# Optionally restrict which commands can be executed by axon-agent.
# If "true", only scripts placed in scripts_location can be executed by axon-agent.
# disable_command_exec: false
# If disable_command_exec is true then axon-agent is only allowed to execute scripts
# under this path
# scripts_location: /var/lib/axonops/scripts/
```

Set file permissions on /etc/axonops/axon-agent.yml file by executing the following command

```
sudo chmod 0644 /etc/axonops/axon-agent.yml
```

<h2>Step 4 - Configure Kafka</h2>

{!dynamic_pages/axon_agent/kafka_java.md!}

<blockquote>
<p><strong>NB.</strong> Make sure that this configuration will not get overridden by an automation tool.</p>
</blockquote>

<h2>Step 5 - Add axonops user to Kafka user group and Kafka user to axonops group</h2>
```
sudo usermod -aG <your_kafka_group> axonops
sudo usermod -aG axonops <your_kafka_user>
```

<h2>Step 6 - Start/Restart Kafka</h2>

To load the Axon java agent and Kafka config changes please,

<ul>
<li>Start the Kafka service if stopped. </li>
<li>Restart the Kafka service if already running.</li>
</ul>