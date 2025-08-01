<br/>
<br/>

<div class="w3-bar w3-light-grey">
  <button class="w3-bar-item w3-button tabSelected w3-grey" id="Broker" onclick="selectKafkaType(event,'Broker')">Kafka Broker</button>
  <button class="w3-bar-item w3-button tabSelected" id="Zookeeper" onclick="selectKafkaType(event,'Zookeeper')">Zookeeper</button>
  <button class="w3-bar-item w3-button tabSelected" id="KRaftBroker" onclick="selectKafkaType(event,'KRaftBroker')">KRaft Broker</button>
  <button class="w3-bar-item w3-button tabSelected" id="KRaftController" onclick="selectKafkaType(event,'KRaftController')">KRaft Controller</button>
  <button class="w3-bar-item w3-button tabSelected" id="Connect" onclick="selectKafkaType(event,'Connect')">Kafka Connect</button>
</div>
<div id="Broker" class="axon_kafka_dynamic_s1">

```yaml hl_lines="7 8 9"
axon-server:
  hosts: "agents.axonops.cloud" # AxonOps SaaS
  # hosts: "${AXONOPS_SERVER_HOSTS}" # AxonOps Server On-Premise Endpoint
  # port: 1888 # AxonOps Server On-Premise Port (Default is 1888)

axon-agent:
  key: "<THIS_IS_A_DUMMY_KEY_PLEASE_UPDATE>"
  org: "<THIS_IS_A_DUMMY_ORG_NAME_PLEASE_UPDATE>"
  cluster_name: "<THIS_IS_A_DUMMY_CLUSTER_NAME_PLEASE_UPDATE>"
  tls:
    mode: "TLS" # disabled, TLS
    #skipVerify: false # Disables CA and Hostname verification
    #caFile: "path_to_certs_on_axon_agent_node.crt" # required if skipVerify is not set and you are using a self-signed cert
    #certFile: "path_to_certs_on_axon_agent_node.crt"
    #keyFile: "path_to_key_file_on_axon_agent_node.key"
# Specify the NTP server IP addresses or hostnames configured for your hosts
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

kafka:
  node_type: "broker" # broker, kraft-broker, kraft-controller, zookeeper, connect
  # rack: "testrack" # Auto-detected from Kafka config, optionally override the rack to group nodes in AxonOps
  kafka_client:
    brokers: ["<host_listener_ip_address_or_fqdn>:<port>>"] # 10.0.0.2:9092 or 10.20.30.40:9094 or this_is_my_server.domain.com:9093
    # Authentication Settings
    sasl:
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
      # For gssapi support
      # gssapi:
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
```
</div>

<div id="Zookeeper" class="axon_kafka_dynamic_s1" style="display:none">

```yaml hl_lines="7 8 9"
axon-server:
  hosts: "agents.axonops.cloud" # AxonOps SaaS
  # hosts: "${AXONOPS_SERVER_HOSTS}" # AxonOps Server On-Premise Endpoint
  # port: 1888 # AxonOps Server On-Premise Port (Default is 1888)

axon-agent:
  key: "<THIS_IS_A_DUMMY_KEY_PLEASE_UPDATE>"
  org: "<THIS_IS_A_DUMMY_ORG_NAME_PLEASE_UPDATE>"
  cluster_name: "<THIS_IS_A_DUMMY_CLUSTER_NAME_PLEASE_UPDATE>"
  tls:
    mode: "TLS" # disabled, TLS
    #skipVerify: false # Disables CA and Hostname verification
    #caFile: "path_to_certs_on_axon_agent_node.crt" # required if skipVerify is not set and you are using a self-signed cert
    #certFile: "path_to_certs_on_axon_agent_node.crt"
    #keyFile: "path_to_key_file_on_axon_agent_node.key"

# Specify the NTP server IP addresses or hostnames configured for your hosts
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

kafka:
  node_type: "zookeeper" # broker, kraft-broker, kraft-controller, zookeeper, connect
  # rack: "testrack" # Optionally specify a rack to group nodes in AxonOps
```
</div>

<div id="KRaftBroker" class="axon_kafka_dynamic_s1" style="display:none">

```yaml hl_lines="7 8 9"
axon-server:
  hosts: "agents.axonops.cloud" # AxonOps SaaS
  # hosts: "${AXONOPS_SERVER_HOSTS}" # AxonOps Server On-Premise Endpoint
  # port: 1888 # AxonOps Server On-Premise Port (Default is 1888)

axon-agent:
  key: "<THIS_IS_A_DUMMY_KEY_PLEASE_UPDATE>"
  org: "<THIS_IS_A_DUMMY_ORG_NAME_PLEASE_UPDATE>"
  cluster_name: "<THIS_IS_A_DUMMY_CLUSTER_NAME_PLEASE_UPDATE>"
  tls:
    mode: "TLS" # disabled, TLS
    #skipVerify: false # Disables CA and Hostname verification
    #caFile: "path_to_certs_on_axon_agent_node.crt" # required if skipVerify is not set and you are using a self-signed cert
    #certFile: "path_to_certs_on_axon_agent_node.crt"
    #keyFile: "path_to_key_file_on_axon_agent_node.key"

# Specify the NTP server IP addresses or hostnames configured for your hosts
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

kafka:
  node_type: "kraft-broker" # broker, kraft-broker, kraft-controller, zookeeper, connect
  # rack: "testrack" # Auto-detected from Kafka config, optionally override the rack to group nodes in AxonOps
  kafka_client:
    brokers: ["<host_listener_ip_address_or_fqdn>:<port>>"] # 10.0.0.2:9092 or 10.20.30.40:9094 or this_is_my_server.domain.com:9093
    # Authentication Settings
    sasl:
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
      # For gssapi support
      # gssapi:
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
```
</div>

<div id="KRaftController" class="axon_kafka_dynamic_s1" style="display:none">

```yaml hl_lines="7 8 9"
axon-server:
  hosts: "agents.axonops.cloud" # AxonOps SaaS
  # hosts: "${AXONOPS_SERVER_HOSTS}" # AxonOps Server On-Premise Endpoint
  # port: 1888 # AxonOps Server On-Premise Port (Default is 1888)

axon-agent:
  key: "<THIS_IS_A_DUMMY_KEY_PLEASE_UPDATE>"
  org: "<THIS_IS_A_DUMMY_ORG_NAME_PLEASE_UPDATE>"
  cluster_name: "<THIS_IS_A_DUMMY_CLUSTER_NAME_PLEASE_UPDATE>"
  tls:
    mode: "TLS" # disabled, TLS
    #skipVerify: false # Disables CA and Hostname verification
    #caFile: "path_to_certs_on_axon_agent_node.crt" # required if skipVerify is not set and you are using a self-signed cert
    #certFile: "path_to_certs_on_axon_agent_node.crt"
    #keyFile: "path_to_key_file_on_axon_agent_node.key"

# Specify the NTP server IP addresses or hostnames configured for your hosts
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

kafka:
  node_type: "kraft-controller" # broker, kraft-broker, kraft-controller, zookeeper, connect
  # rack: "testrack" # Auto-detected from Kafka config, optionally override the rack to group nodes in AxonOps
  kafka_client:
    brokers: ["<host_listener_ip_address_or_fqdn>:<port>>"] # 10.0.0.2:9092 or 10.20.30.40:9094 or this_is_my_server.domain.com:9093
    # Authentication Settings
    sasl:
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
      # For gssapi support
      # gssapi:
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
```
</div>

<div id="Connect" class="axon_kafka_dynamic_s1" style="display:none">

```yaml hl_lines="7 8 9"
axon-server:
  hosts: "agents.axonops.cloud" # AxonOps SaaS
  # hosts: "${AXONOPS_SERVER_HOSTS}" # AxonOps Server On-Premise Endpoint
  # port: 1888 # AxonOps Server On-Premise Port (Default is 1888)

axon-agent:
  key: "<THIS_IS_A_DUMMY_KEY_PLEASE_UPDATE>"
  org: "<THIS_IS_A_DUMMY_ORG_NAME_PLEASE_UPDATE>"
  cluster_name: "<THIS_IS_A_DUMMY_CLUSTER_NAME_PLEASE_UPDATE>"
  tls:
    mode: "TLS" # disabled, TLS
    #skipVerify: false # Disables CA and Hostname verification
    #caFile: "path_to_certs_on_axon_agent_node.crt" # required if skipVerify is not set and you are using a self-signed cert
    #certFile: "path_to_certs_on_axon_agent_node.crt"
    #keyFile: "path_to_key_file_on_axon_agent_node.key"

# Specify the NTP server IP addresses or hostnames configured for your hosts
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

kafka:
  node_type: "connect" # broker, kraft-broker, kraft-controller, zookeeper, connect
  # rack: "testrack" # Optionally specify a rack to group nodes in AxonOps
```
</div>

<!-- Set the Axon-Agent File Permissions -->
Set file permissions on /etc/axonops/axon-agent.yml file by executing the following command

```shell
sudo chmod 0640 /etc/axonops/axon-agent.yml
```

<!-- Step 4 -->
<div id="Broker" class="axon_kafka_dynamic_s2">
<h2>Configure Kafka</h2>

Edit kafka-server-start.sh, usually located in your Kafka install path such as: 

<p><code>/&lt;Kafka_Home&gt;/bin/kafka-server-start.sh</code></p>
</div>

<div id="Zookeeper" class="axon_kafka_dynamic_s2" style="display:none">
<h2>Configure Zookeeper</h2>

Edit zookeeper-server-start.sh, usually located in your Zookeeper install path such as: 

<p><code>/&lt;Zookeeper_Home&gt;/bin/zookeeper-server-start.sh</code></p>
</div>

<div id="KRaftBroker" class="axon_kafka_dynamic_s2" style="display:none">
<h2>Configure KRaft Broker</h2>

Edit kafka-server-start.sh, usually located in your Kafka install path such as: 

<p><code>/&lt;Kafka_Home&gt;/bin/kafka-server-start.sh</code></p>
</div>

<div id="KRaftController" class="axon_kafka_dynamic_s2" style="display:none">
<h2>Configure KRaft Controller</h2>

Edit kafka-server-start.sh, usually located in your Kafka install path such as: 

<p><code>/&lt;Kafka_Home&gt;/bin/kafka-server-start.sh</code></p>
</div>

<div id="Connect" class="axon_kafka_dynamic_s2" style="display:none">
<h2>Configure Connect</h2>

Edit connect-distributed.sh, usually located in your Kafka install path such as: 

<p><code>/&lt;Kafka_Home&gt;/bin/connect-distributed.sh </code></p>
</div>
<!-- Load Dynamic Java section -->
{!dynamic_pages/axon_agent/kafka_java.md!}
<!-- Step 4 end -->
<blockquote>
<p><strong>NB.</strong> Make sure that this configuration will not get overridden by an automation tool.</p>
</blockquote>

 <!-- Step 5 to 6 -->
<div id="Broker" class="axon_kafka_dynamic_s5">
<h2>Add axonops user to Kafka user group and Kafka user to axonops group</h2>
```
sudo usermod -aG <your_kafka_group> axonops
sudo usermod -aG axonops <your_kafka_user>
```

<h2>Start/Restart Kafka</h2>

To load the AxonOps Java Agent and Kafka config changes please either start the Kafka service if stopped restart the Kafka service if already running.
</div>

<div id="Zookeeper" class="axon_kafka_dynamic_s5" style="display:none">
<h2>Add axonops user to Zookeeper user group and Zookeeper user to axonops group</h2>
```
sudo usermod -aG <your_zookeeper_group> axonops
sudo usermod -aG axonops <your_zookeeper_user>
```

<h2>Start/Restart Zookeeper</h2>

To load the AxonOps Java Agent and Zookeeper config changes please either start the Zookeeper service if stopped or restart the Zookeeper service if already running.
</div>

<div id="KRaftBroker" class="axon_kafka_dynamic_s5" style="display:none">
<h2>Add axonops user to KRaft Broker user group and KRaft Broker user to axonops group</h2>
```
sudo usermod -aG <your_kraft_group> axonops
sudo usermod -aG axonops <your_kraft_user>
```

<h2>Start/Restart KRaft Broker</h2>

To load the AxonOps Java Agent and Kafka KRaft config changes please either start the Kafka KRaft service if stopped or restart the Kafka KRaft service if already running.
</div>

<div id="KRaftController" class="axon_kafka_dynamic_s5" style="display:none">
<h2>Add axonops user to KRaft Controller user group and KRaft Controller user to axonops group</h2>
```
sudo usermod -aG <your_kraft_group> axonops
sudo usermod -aG axonops <your_kraft_user>
```

<h2>Start/Restart KRaft Controller</h2>

To load the AxonOps Java Agent and Kafka KRaft config changes please either start the Kafka KRaft service if stopped or restart the Kafka KRaft service if already running.
</div>

<div id="Connect" class="axon_kafka_dynamic_s5" style="display:none">
<h2>Add axonops user to Kafka Connect user group and Kafka Connect user to axonops group</h2>
```
sudo usermod -aG <your_connect_group> axonops
sudo usermod -aG axonops <your_connect_user>
```

<h2>Start/Restart Kafka Connect</h2>

To load the AxonOps Java Agent and Kafka Connect config changes please either:

* Start the Kafka Connect service if stopped.
* Restart the Kafka Connect service if already running.

</div>
