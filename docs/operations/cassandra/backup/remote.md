---
title: "Remote backups"
description: "Remote backup destinations for Cassandra in AxonOps. Cloud storage options."
meta:
  - name: keywords
    content: "remote backup, cloud backup, Cassandra backup destinations"
---

# Remote Backups

> Note that the AxonOps user needs read access to Cassandra data folders to perform a remote backup.

When selecting remote backups there are some basic configuration presets.

![remote_backup_basic_config](./remote_backup_basic_config.png)

#### Transfers (File Transfer Parallelism)

The number of file transfers to run in parallel. It can be beneficial to set this to a smaller number if the remote is timing out. You can set this to a larger number or leave it at 0 if you have plenty of bandwidth and a fast remote.

#### TPS Limit 

If you are getting errors from the cloud storage provider, start adjusting this limit.

The default is 0.

Storage provider errors consist of getting you banned or imposing rate limits.

A transaction includes, but is not limited to, PUT/GET/POST calls to the storage backend.

Different Storage providers have different limits. 

* Amazon S3 has a limit of 5,500 GET requests per second per partitioned prefix.[More here](https://docs.aws.amazon.com/athena/latest/ug/performance-tuning-s3-throttling.html)
* Google Cloud Storage has an approximate limit of 1,000 READ and 5,000 WRITE requests per second.[More here](https://cloud.google.com/storage/docs/request-rate)
* Azure Blob Storage has a limit of 20,000 requests per second per storage account. [More here](https://learn.microsoft.com/en-us/azure/storage/common/scalability-targets-standard-account?toc=%2Fazure%2Fstorage%2Fblobs%2Ftoc.json)

#### Bandwidth Limit

This will allow you to set a limit on how much data you want to transfer to your Storage provider during backups. 
Note that the units are bytes per second, not bits per second. Connections are typically measured in bits per second, so divide by 8. For example, if you have a 10 Mbit/s connection and you want AxonOps to use half of it (5 Mbit/s), set the limit to 0.625 MB/s.

In most modern storage systems the value is not normally this low but if you have a VPN Gateway connection setup between an on-premise cluster and a storage provider that has a 100MB connection you could potentially limit how much of the pipe gets used by backups. 

#### The available remote options are:

* AWS S3
* Google Cloud Storage
* Local filesystem
* Microsoft Azure Blob Storage
* S3 Compatible
* SFTP/SSH
