###  Local backup settings

On the Axonops application menu, click `Operations` and select `Backups > Configurations`.
Then select `General Settings` tab.

!!! infomy 

    [![backup](/img/cass_backups/backups_conf0.png)](/img/cass_backups/backups_conf0.png)

You can specify the retention as an integer number followed by one of "smhdwMy"

The following present a local backup setup only:

!!! infomy 

    [![backup](/img/cass_backups/backups_conf1.png)](/img/cass_backups/backups_conf1.png)


###  Remote backup 

> Note that **axonops** user will need read access on Cassandra snapshots folders to be able to proceed the remote backup.


The current remote options are:

* local filesystem
* AWS S3

!!! infomy 

    [![backup](/img/cass_backups/backups_conf.png)](/img/cass_backups/backups_conf.png)


!!! infomy 

    [![backup](/img/cass_backups/backups_conf2.png)](/img/cass_backups/backups_conf2.png)
