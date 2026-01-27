---
title: "Air-Gapped Installation"
description: "Install AxonOps in air-gapped environments. Offline package installation and configuration."
meta:
  - name: keywords
    content: "air-gapped install, offline installation, AxonOps"
---

# Air-Gapped Installation

Follow the process below to install AxonOps within air-gapped systems.

{!installation/air-gapped/dynamic_page.md!}

## Configure Software

### Configure Server and Dashboard

Once installed, ensure the `axon-server` and `axon-dash` are configured
correctly by:

* ensuring the target software is not running,
* configuring the relevant
configuration file,
* and restarting the target service.

```bash
{!installation/air-gapped/configure-software.sh!}
```

### Configure and Load Agents

On the Cassandra/Kafka machine, run the following commands to configure `AxonOps agent` and
ensure Cassandra/Kafka loads the agent. Use the instructions found on the
[AxonOps Agent Installation](../agent/install.md) page to:

* configure `AxonOps agent`,
* configure Cassandra/Kafka to load the agent,
* configure the Cassandra/Kafka user groups,
* and restart the Cassandra/Kafka process.

```bash
{!installation/air-gapped/install-agent.sh!}
```

## Upgrading

When upgrading your air-gapped AxonOps installation, simply follow the above
instructions to:

* download the target packages and dependencies on an online machine,
* extract the tarball(s) on the offline machine,
* and run the select `install_dependency` commands.

Feel free to adjust the extracted path to maintain proper versioning accordingly.

After the new versions have been installed, run the following commands to load the new
configuration file changes and restart the select service(s):

```bash
sudo systemctl daemon-reload
sudo systemctl restart $service
```
