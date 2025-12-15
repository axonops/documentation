---
title: "Re-using an existing Host ID"
description: "Reuse host ID in AxonOps when replacing nodes. Maintain monitoring history across node replacements."
meta:
  - name: keywords
    content: "reuse host ID, node replacement, monitoring history, AxonOps"
---

# Re-using an existing Host ID

Each agent connected to the AxonOps server is assigned a unique host ID that is used internally to associate metrics and events with the node. If a Cassandra host dies and is replaced by another one with the same IP and token range then normally a new host ID will be generated and the replacement server will appear as a new machine in AxonOps. In this situation it is possible to re-use the same host ID so AxonOps sees the replacement server as the same as the original one.

You can find the host ID of a node in the AxonOps GUI by going to Cluster Overview and selecting a node. In Graph View the host ID is shown next to the hostname in the details panel and in List View it is shown as Agent ID at the top of the details popup. If the old server's filesystem is still accessible you can also find the host ID stored in `/var/lib/axonops/hostId`.

Follow these steps to start up a replacement server using the old host ID:

1. Install axon-agent on the replacement server
2. Stop axon-agent if it is running then delete these files if they exist: `/var/lib/axonops/hostId`, `/var/lib/axonops/local.db`
3. Create a new file at `/var/lib/axonops/hostId` containing the host ID you wish to use
4. Start axon-agent
