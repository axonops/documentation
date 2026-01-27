---
title: "Scheduled Backups"
description: "Cassandra backup overview with AxonOps. Automated backup features and options."
meta:
  - name: keywords
    content: "Cassandra backup overview, automated backup, AxonOps backup"
---

# Scheduled Backups

AxonOps provides scheduled backup functionality for your Cassandra data to local and remote storage options.

The Backup feature is accessible via ***Operations > Backups***.

[![backup](imgs/backup-overview.jpg)](imgs/backup-overview.jpg)


## Scheduled Backups

You can initiate two types of scheduled backup:

* Immediate backup: triggers a backup immediately, once.

* Cron schedule backup: triggered based on the selected schedule and based on a Cron expression.

[![backup](imgs/cronjobs.png)](imgs/cronjobs.png)

## Remote Backups

Backups can be created and stored locally and/or remotely.

[![backup](imgs/remote-backups.png)](imgs/remote-backups.png)

Backups can be stored to:

* AWS S3
* Google Cloud Storage
* Local filesystem
* Microsoft Azure Blob Storage
* S3 Compatible storage systems
* SFTP/SSH servers

[![backup](imgs/remote-options.png)](imgs/remote-options.png)
