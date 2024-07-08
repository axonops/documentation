#### Prerequisites

Backups are enabled and setup. For more on how to setup backups please follow the guide [here](/operations/cassandra/backup/overview/)

#### Steps:

In the AxonOps Dashboard on the left hand menu navigate to Operations --> Backups

<img src="/pitr/pitr_left_backup.png" width="200">

On the top tab select Commitlog Archiving.

<img src="/pitr/pitr_top_commitlog.png" width="700">

#### Configuration

Complete the fields with the required value and click <img src="/pitr/create_configuration.png" width="150">

#### Fields 

- **```Data Centers (Mandatory)```**
    
    The Cassandra Cluster DC that you want to enable Commitlog Archiving.

- **```Retention (Mandatory)```**
    
    The amount of time in hours(h), days(d), weeks(w), month(M) or year(y) that you want to archive the commit logs for.

- **```Remote Storage```**

    The following options are available for Remote storage locations.

    - AWS S3
    - Google Cloud Storage
    - local filesystem
    - Microsoft Azure Blob Storage
    - S3 Compatible
    - SFTP/SSH
    
- **```Base Remote Path```**

    This is the name of the storage buckets, you can also add subfolders if using shared storage buckets or saving multiple clusters to the same bucket. By default AxonOps will save the backups to /bucket/folder/org/clustertype/clustername/host-id/

    The org/clustertype/clustername/host-id/ will match the top breadcrump navigation in your AxonOps Dashboard.

