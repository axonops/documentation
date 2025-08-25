Follow the process below to install AxonOps within air-gapped systems.

{!installation/air-gapped/dynamic_page.md!}

## Configure Software

Once installed, ensure the `axon-server` and `axon-dash` are configured
correctly by:

* ensuring the target software is not running,
* configuring the relevant
configuration file,
* and restarting the target service.

```bash
{!installation/air-gapped/configure-software.sh!}
```

## Install Agent

On the Cassandra machine, run the following commands to configure `axon-agent` and
ensure Cassandra loads the agent. Use the instructions found [here](../agent/install.md)
to:

* configure `axon-agent`
* and configure Cassandra to load the agent.

```bash
{!installation/air-gapped/install-agent.sh!}
```