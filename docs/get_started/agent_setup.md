<script>
function updateOS() {
  var ele = document.getElementsByName('osFamily');
  for(i = 0; i < ele.length; i++) {
      if(ele[i].checked)
      // document.getElementById("result").innerHTML = "Choosen: "+ele[i].value;
      window.location.href = ele[i].value;
  }
}

function updateCas() {
  var ele = document.getElementsByName('casFamily');
  for(i = 0; i < ele.length; i++) {
      if(ele[i].checked)
      window.location.href = ele[i].value;
  }
}
</script>
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

## Setup the AxonOps repository on your Operating system

### Select the OS Family. 
<label>
  <input type="radio" name="osFamily" value="/get_started/agent_setup/#__tabbed_1_1" onChange="updateOS()">
  <img src="/get_started/debian.png" class="skip-lightbox" width="180px">
</label>
<label>
  <input type="radio" name="osFamily" value="/get_started/agent_setup/#__tabbed_1_2" onChange="updateOS()">
  <img src="/get_started/red_hat.png" class="skip-lightbox" width="180px">
</label>

===+ "Debian / Ubuntu"
    ```bash
    curl https://packages.axonops.com/apt/repo-signing-key.gpg | sudo apt-key add -
    echo "deb https://packages.axonops.com/apt axonops-apt main" | sudo tee /etc/apt/sources.list.d/axonops-apt.list
    sudo apt-get update
    ```

=== "RedHat / CentOS"
    ```bash
    sudo tee /etc/yum.repos.d/axonops-yum.repo << EOL
    [axonops-yum]
    name=axonops-yum
    baseurl=https://packages.axonops.com/yum/
    enabled=1
    repo_gpgcheck=0
    gpgcheck=0
    EOL
    sudo yum makecache
    ```

## Install Cassandra Agent

### Select the Cassandra Version
<label>
  <input type="radio" name="casFamily" value="/get_started/agent_setup/#__tabbed_3_1" onChange="updateCas()">
  <img src="/get_started/cas_3.png" class="skip-lightbox" width="180px">
</label>
<label>
  <input type="radio" name="casFamily" value="/get_started/agent_setup/#__tabbed_3_2" onChange="updateCas()">
  <img src="/get_started/cas_3_11.png" class="skip-lightbox" width="180px">
</label>
<label>
  <input type="radio" name="casFamily" value="/get_started/agent_setup/#__tabbed_3_3" onChange="updateCas()">
  <img src="/get_started/cas_4.png" class="skip-lightbox" width="180px">
</label>
<label>
  <input type="radio" name="casFamily" value="/get_started/agent_setup/#__tabbed_3_4" onChange="updateCas()">
  <img src="/get_started/cas_4_1.png" class="skip-lightbox" width="180px">
</label>

===+ "Debian / Ubuntu"
    ===+ "Cassandra 3.0"
        ```
        sudo apt-get install axon-cassandra3.0-agent
        ```
    
    === "Cassandra 3.11"
        ```
        sudo apt-get install axon-cassandra3.11-agent
        ```
    
    === "Cassandra 4.0"
        ```
        sudo apt-get install axon-cassandra4.0-agent
        ```

    === "Cassandra 4.1"
        ```
        sudo apt-get install axon-cassandra4.1-agent
        ```

=== "RedHat / CentOS"
    === "Cassandra 3.0"
        ```
        sudo yum install axon-cassandra3.0-agent
        ```
    
    === "Cassandra 3.11"
        ```
        sudo yum install axon-cassandra3.11-agent
        ```
    
    === "Cassandra 4.0"
        ```
        sudo yum install axon-cassandra4.0-agent
        ```

    === "Cassandra 4.1"
        ```
        sudo yum install axon-cassandra4.1-agent
        ```

## Agent Configuration

Update and copy the below code snippet into /etc/axonops/axon-agent.yml file.

Please update the **key** and **org** values by logging into [console.axonops.cloud](https://console.axonops.cloud){target="_blank"}

* **Organization(org)** name is next to the logo in the console
* **Agent Keys(key)** found in Agent Setup

![](agent_keys.png)

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
sudo chmod 0644 /etc/axonops/axon-agent.yml
```

## Cassandra Configuration

Edit cassandra-env.sh, usually located in your Cassandra install path such as /<Cassandra Installation Directory>/conf/cassandra-env.sh, and append the following line at the end of the file:

=== "Cassandra 3.0"
    ```
    JVM_OPTS="$JVM_OPTS -javaagent:/usr/share/axonops/axon-cassandra3.0-agent.jar=/etc/axonops/axon-agent.yml"
    ```

=== "Cassandra 3.11"
    ```
    JVM_OPTS="$JVM_OPTS -javaagent:/usr/share/axonops/axon-cassandra3.11-agent.jar=/etc/axonops/axon-agent.yml"
    ```

=== "Cassandra 4.0"
    ```
    JVM_OPTS="$JVM_OPTS -javaagent:/usr/share/axonops/axon-cassandra4.0-agent.jar=/etc/axonops/axon-agent.yml"
    ```

=== "Cassandra 4.1"
    ```
    JVM_OPTS="$JVM_OPTS -javaagent:/usr/share/axonops/axon-cassandra4.1-agent.jar=/etc/axonops/axon-agent.yml"
    ```

**NB.** Make sure that this configuration will not get overridden by an automation tool.

## Add AxonOps user to Cassandra user group and Cassandra user to AxonOps group
```
sudo usermod -aG <your_cassandra_group> axonops
sudo usermod -aG axonops <your_cassandra_user>
```

## Start/Restart Cassandra

To load the Axon java agent and Cassandra config changes please,

* Start the Cassandra service if stopped. 
* Restart the Cassandra service if already running.

## Start axon-agent

```
sudo systemctl start axon-agent
```


Once the Agents have been setup please use the [Using AxonOps](/cluster/cluster-overview/) to familiarise yourself with AxonOps UI.