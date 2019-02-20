AxonOps provide scheduled backup and restore functionnality for your Cassandra cluster.

!!! infomy 

    [![backup](/img/cass_backups/backups.png)](/img/cass_backups/backups.png)


## Scheduled backup

You can initiate three types of scheduled backup:

* Immediate scheduled backup: these will trigger immediately **once**

* Simple scheduled backup: these will trigger base on the selected schedule **repeatedly**

!!! infomy 

    [![backup](/img/cass_backups/backups2.png)](/img/cass_backups/backups2.png)

* Cron schedule backup: Same as **simple scheduled backup** but the schedule will be based on a Cron expression

!!! infomy 

    [![backup](/img/cass_backups/backups3.png)](/img/cass_backups/backups3.png)

> The following capture presents two backups, a local only and a local and remote backup:

!!! infomy 

    [![backup](/img/cass_backups/backups5.png)](/img/cass_backups/backups5.png)

> And the details of the local and remote backup on the `Restore` page:

!!! infomy 

    [![backup](/img/cass_backups/backups4.png)](/img/cass_backups/backups4.png)


## Restore


> Note that **axonops** user will need temporary write access on Cassandra data folders to be able to proceed the restoration.

To restore Cassandra, click on a relevant backup.

!!! infomy 

    [![restore](/img/cass_backups/restore.png)](/img/cass_backups/restore.png)

This will provide the details of that backup and the ability to start the restoration by clicking the `Restore` button.

!!! infomy 

    [![restore](/img/cass_backups/restore1.png)](/img/cass_backups/restore1.png)
