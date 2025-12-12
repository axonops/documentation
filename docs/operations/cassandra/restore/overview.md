---
description: "Cassandra restore overview with AxonOps. Restore from backups to recover data."
meta:
  - name: keywords
    content: "Cassandra restore, data recovery, AxonOps restore, backup restore"
---

AxonOps provides the ability to restore from local snapshots and remote backups.

The Restore feature is accessible via ***Operations > Restore***

!!! infomy 

    [![restore](../../../img/cass_backups/restore.png)](../../../img/cass_backups/restore.png)



> Note that **axonops** user will need temporary write access on Cassandra data folders to be able to perform the restoration.

To restore Cassandra, click on the backup you wish to restore.


This will provide the details of that backup and the ability to start the restoration by clicking the `LOCAL RESTORE` or `REMOTE RESTORE` 
button depending on if you prefer to restore from the local snapshot or the remote backup (if remote backups were configured).
Here you can also select a subset of nodes to restore via the checkboxes in the Nodes list.

!!! infomy 

    [![restore](../../../img/cass_backups/restore1.png)](../../../img/cass_backups/restore1.png)

Follow the links below for some more detailed backup restore scenarios

[Restore a single node - same IP address](restore-node-same-ip.md)

[Replace a node - different IP address](restore-node-different-ip.md)

[Restore whole cluster - same IP addresses](restore-cluster-same-ip.md)
