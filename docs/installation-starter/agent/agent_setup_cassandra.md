<h2>Step 2 - Install Cassandra Agent</h2>

{!dynamic_pages/axon_agent/cassandra_agent.md!}

<blockquote>
<p>Note: This will install the AxonOps Cassandra agent and its dependency: <strong>axon-agent</strong></p>
</blockquote>

<h2>Step 3 - Agent Configuration</h2>

<p>Update the following highlighted lines from <code>/etc/axonops/axon-agent.yml</code>:</p>

These need to match the config that you have in your axon-server.yml setup.

``` yaml hl_lines="2 6"
axon-server:
    hosts: "axon-server_endpoint" # Your axon-server IP or hostname, e.g. axonops.mycompany.com
    port: 1888 # The default axon-server port is 1888

axon-agent:
    org: "my-company" # Your organisation name
    # SSL/TLS Settings from AxonOps Agent to AxonOps Server
    tls:
        mode: "disabled" # disabled, TLS

NTP:
    host: "ntp.mycompany.com" # Your NTP server IP address or hostname 
```

Set file permissions on /etc/axonops/axon-agent.yml file by executing the following command

```
sudo chmod 0640 /etc/axonops/axon-agent.yml
```

<h2>Step 4 - Configure Cassandra</h2>

{!dynamic_pages/axon_agent/java.md!}

<blockquote>
<p><strong>NB.</strong> Make sure that this configuration will not get overridden by an automation tool.</p>
</blockquote>

<h2>Step 5 - Add axonops user to Cassandra user group and Cassandra user to axonops group</h2>

``` bash
sudo usermod -aG <your_cassandra_group> axonops
sudo usermod -aG axonops <your_cassandra_user>
```

<h2>Step 6 - Start/Restart Cassandra</h2>

To load the AxonOps Java Agent and Cassandra config changes please,

- Start the Cassandra service if stopped.
- Restart the Cassandra service if already running.