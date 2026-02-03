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

axon-agent:
    org: "my-company" # Your organisation name
    # SSL/TLS Settings from AxonOps Agent to AxonOps Server
    tls:
        mode: "disabled" # disabled, TLS
        # Only set below if mode is TLS
        skipVerify: false # Disables CA and Hostname verification
        caFile: "path_to_certs_on_axon_agent_node.crt" # required if skipVerify is not set and you are using a self-signed cert
        certFile: "path_to_certs_on_axon_agent_node.crt"
        keyFile: "path_to_key_file_on_axon_agent_node.key"
    # Command execution restrictions (see below for details)
    # disable_command_exec: false
    # scripts_location: /var/lib/axonops/scripts/

NTP:
    host: "ntp.mycompany.com" # Your NTP server IP address or hostname
```

### Command Execution Security

The axon-agent can execute commands on the host system to perform operations such as repairs, backups, and restarts. These options allow configuration of the command execution security posture based on organisational requirements:

| Option | Default | Description |
|--------|---------|-------------|
| `disable_command_exec` | `false` | When set to `true`, the agent only executes scripts located in the `scripts_location` directory. |
| `scripts_location` | `/var/lib/axonops/scripts/` | The directory containing permitted scripts when `disable_command_exec` is enabled. |

Three command execution modes are available:

| Mode | Configuration | Description |
|------|---------------|-------------|
| **Full access** | `disable_command_exec: false` | The agent can execute commands sent from AxonOps. This is the default. |
| **Permitted scripts only** | `disable_command_exec: true` with scripts in `scripts_location` | The agent only executes scripts placed in the designated directory. |
| **No execution** | `disable_command_exec: true` with empty `scripts_location` | The agent cannot execute any commands. |

!!! example "Permitted Scripts Only"
    ```yaml
    axon-agent:
        org: "my-company"
        disable_command_exec: true
        scripts_location: /var/lib/axonops/scripts/
    ```

    With this configuration, only scripts placed in `/var/lib/axonops/scripts/` can be executed by the agent.

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
