---
title: "Overview"
description: "Rolling restart for Kafka with AxonOps. Zero-downtime broker restarts."
meta:
  - name: keywords
    content: "rolling restart, Kafka restart, zero downtime, broker restart"
---

# Overview

AxonOps provides a rolling restart feature for Kafka.

The feature is accessible via **Operations > Rolling Restart**.


[![rollingrestart](./1.png)](./1.png)

> The **AxonOps** user requires permissions to stop and start the Kafka service. Add the **AxonOps** user to sudoers, for example:
```bash
#/etc/sudoers.d/axonops
axonops ALL=NOPASSWD: /sbin/service kafka *, /usr/bin/systemctl * kafka*
```



You can start an **immediate** rolling restart or **schedule** it.

The **script** field lets you customize the predefined script executed by the AxonOps agent during the restart process.

You can also specify different degrees of parallelism for the restart: **DC**, **Rack**, and **Node**.

For example, to **restart one entire rack** at once across the cluster, you can set a large **Node parallelism** (greater than the number of nodes in the rack, for example 999).
```bash
DC parallelism: 1
Rack parallelism: 1
Node parallelism: 999
```


To **restart one entire rack across each DC**:
```bash
DC parallelism: 999
Rack parallelism: 1
Node parallelism: 999
```


