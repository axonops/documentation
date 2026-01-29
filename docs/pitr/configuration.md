---
title: "Prerequisites"
description: "Configure point-in-time restore for Cassandra. Commitlog archiving setup."
meta:
  - name: keywords
    content: "PITR configuration, commitlog archiving, point-in-time setup"
---

# Prerequisites

Backups are enabled and set up. For more on how to set up backups, see [Backup overview](../operations/cassandra/backup/overview.md).

## Steps

In the AxonOps Dashboard on the left-hand menu, navigate to **Operations > Backups**.

<img src="/pitr/pitr_left_backup.png" width="200" alt="pitr_left_backup">

On the top tab, select **Commitlog Archiving**.

<img src="/pitr/pitr_top_commitlog.png" width="700" alt="pitr_top_commitlog">

## Configuration

Complete the fields with the required values and click the **Create configuration** button.

## Fields

- **Data Centers (Mandatory)**
    
    The Cassandra Cluster DC that you want to enable Commitlog Archiving.

- **Retention (Mandatory)**
    
    The amount of time in hours (h), days (d), weeks (w), months (M), or years (y) that you want to archive commit logs for.

- **Remote Storage**

    The following options are available for remote storage locations:

    - AWS S3
    - Google Cloud Storage
    - Local filesystem
    - Microsoft Azure Blob Storage
    - S3 Compatible
    - SFTP/SSH
    
- **Base Remote Path**

    This is the name of the storage bucket. You can also add subfolders if using shared buckets or saving multiple clusters to the same bucket. By default AxonOps saves backups to `/bucket/folder/org/clustertype/clustername/host-id/`.

    The `org/clustertype/clustername/host-id/` path matches the top breadcrumb navigation in the AxonOps Dashboard.
