AxonOps provide scheduled backup and restore functionality for your Cassandra data.

The functionality is accessible via ***Operations > Backups***

!!! infomy 

    [![backup](./1.JPG)](./1.JPG)


## Scheduled backup

You can initiate three types of scheduled backup:

* Immediate scheduled backup: these will trigger immediately **once**

* Simple scheduled backup: these will trigger based on the selected schedule **repeatedly**

!!! infomy 

    [![backup](/img/cass_backups/backups2.png)](/img/cass_backups/backups2.png)

* Cron schedule backup: Same as **simple scheduled backup** but the schedule will be based on a Cron expression

!!! infomy 

    [![backup](/img/cass_backups/backups3.png)](/img/cass_backups/backups3.png)

> The following capture presents two backups, a local only and a local and remote backup:

!!! infomy 

    [![backup](/img/cass_backups/backups5.png)](/img/cass_backups/backups5.png)

> And the details of the local and remote backup:

!!! infomy 

    [![backup](./2.JPG)](./2.JPG)

###  Remote backups 

> Note that **axonops** user will need read access on Cassandra data folders to be able to perform a remote backup.


The available remote options are:

* AWS S3
* Google Cloud Storage
* Microsoft Azure Blob Storage
* SFTP/SSH
* local filesystem

example of the AWS S3 remote interface:

!!! infomy 

    [![backup](./3.JPG)](./3.JPG)

