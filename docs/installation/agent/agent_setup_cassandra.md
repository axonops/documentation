## Install Cassandra Agent

{!dynamic_pages/axon_agent/cassandra_agent.md!}

## Agent Configuration

Update the following lines within `/etc/axonops/axon-agent.yml`.

The highlighted lines should match the `host` and `org` keys found within
`/etc/axonops/axon-server.yml`.

```yaml hl_lines="2 6"
axon-server:
    hosts: "axon-server_endpoint" # Your axon-server IP or hostname, e.g. axonops.mycompany.com
    port: 1888 # The default axon-server port is 1888

AxonOps agent:
    org: "my-company" # Your organisation name
    # SSL/TLS Settings from AxonOps Agent to AxonOps Server
    tls:
        mode: "disabled" # disabled, TLS
        # Only set below if mode is TLS
        skipVerify: false # Disables CA and Hostname verification
        caFile: "path_to_certs_on_axon_agent_node.crt" # required if skipVerify is not set and you are using a self-signed cert
        certFile: "path_to_certs_on_axon_agent_node.crt"
        keyFile: "path_to_key_file_on_axon_agent_node.key"

NTP:
    host: "ntp.mycompany.com" # Your NTP server IP address or hostname 
```

### Ensure Proper Agent Configuration Permissions

After editing the file, ensure the file permissions for `/etc/axonops/axon-agent.yml` are set correctly by
running the following commmand:

```bash
sudo chmod 0640 /etc/axonops/axon-agent.yml
```

## Configure Cassandra

{!dynamic_pages/axon_agent/java.md!}

## Apply Changes to Cassandra

To load the AxonOps Java Agent and Cassandra config changes, run the following command:

```bash
{!installation/axon-agent/scripts/restart-cassandra.sh!}
```
