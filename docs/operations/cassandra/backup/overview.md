---
title: "Scheduled Backups"
description: "Cassandra backup overview with AxonOps. Automated backup features and options."
meta:
  - name: keywords
    content: "Cassandra backup overview, automated backup, AxonOps backup"
---

AxonOps provides scheduled backup funtionality for your Cassandra data to local and remote storage options.

The Backup feature is accessible via ***Operations > Backups***.

!!! infomy
    [![backup](imgs/backup-overview.jpg)](imgs/backup-overview.jpg)


## Scheduled Backups

You can initiate three types of scheduled backup:

* Immediate scheduled backup: will trigger backup immediately **once**.

* Cron schedule backup: triggered based on the selected schedule and based on a Cron expression.

!!! infomy
    [![backup](imgs/cronjobs.png)](imgs/cronjobs.png)

## Remote Backups

Backups can be created and stored locally and/or remotely.

!!! infomy
    [![backup](imgs/remote-backups.png)](imgs/remote-backups.png)

Backups can be stored to:

* AWS S3
* Google Cloud Storage
* Local filesystem
* Microsoft Azure Blog Storage
* S3 Compatible storage systems
* SFTP/SSH servers

!!! infomy
    [![backup](imgs/remote-options.png)](imgs/remote-options.png)
