---
title: "Restore a backup to a different cluster"
description: "Restore Cassandra data to a different cluster. Cross-cluster data migration."
meta:
  - name: keywords
    content: "restore different cluster, data migration, cross-cluster, Cassandra"
search:
  boost: 8
---

# Restore a backup to a different cluster

Follow this procedure to restore an AxonOps backup from remote storage onto a different cluster.

AxonOps Agent version 1.0.60 and later includes a command-line tool which can be used to restore a backup created by
AxonOps from remote storage (e.g. S3, GCS). This tool connects directly to your remote storage and does not require an
AxonOps server or an active AxonOps Cloud account in order to function.

AxonOps Agent version 2.0.12 and later includes the ability to restore commit logs onto a different cluster.

Follow the [setup and configuration guide](restore-tool-setup.md) to get started.

## Listing available backups

To list the backups available in the remote storage bucket, you can run `axon-cassandra-restore` with the `--list` option [after setting up](restore-tool-setup.md#storage-config-and-storage-config-file-options) your `--storage-config-file`.

For example, to list remote backups, you could use a command similar to the following:

```bash
/usr/share/axonops/axon-cassandra-restore \
    --storage-config-file /path/to/remote_storage_config_file.json \
    --org-id myaxonopsorg \
    --list
```

The restore tool will scan the specified S3 bucket for AxonOps backups and will display the date and backup ID for any backups it finds, for example:

```bash
Org ID:    myaxonopsorg
Cluster:   testcluster
Time                   Backup ID
2023-09-14 14:30 UTC   c67cea2a-5310-11ee-b686-bed50b9335ec
2023-09-15 14:31 UTC   2c1d9aca-5312-11ee-b686-bed50b9335ec
2023-09-16 14:30 UTC   91be5007-5313-11ee-b686-bed50b9335ec
2023-09-17 14:31 UTC   f75f13d9-5314-11ee-b686-bed50b9335ec
2023-09-18 14:30 UTC   5cffc1e6-5316-11ee-b686-bed50b9335ec
```

If you pass the `--verbose` option when listing backups, it will show a list of nodes and tables in each backup, for example:

```bash

Org ID:    myaxonopsorg
Cluster:   testcluster
Time:      2023-09-14 14:30 UTC
Backup ID: c67cea2a-5310-11ee-b686-bed50b9335ec

Host:   026346a0-dc89-4235-ae34-552fcd453b42
Tables: system.prepared_statements, system.transferred_ranges_v2, system_distributed.repair_history, system_schema.types, system_traces.sessions, system.compaction_history, system.available_ranges_v2, system.batches, system.size_estimates, system_schema.aggregates, system.IndexInfo, system_auth.resource_role_permissons_index, system_schema.views, test.test, system.paxos, system.local, system.peers, system.peers_v2, system.table_estimates, system_auth.network_permissions, system_auth.roles, system_distributed.view_build_status, system.built_views, system_schema.triggers, system.peer_events, system.repairs, keyspace1.table1, system.sstable_activity, keyspace1.table2, system.transferred_ranges, system_auth.role_permissions, system_distributed.parent_repair_history, system.available_ranges, system_schema.dropped_columns, system_schema.columns, system_schema.keyspaces, system.view_builds_in_progress, system_auth.role_members, system_schema.functions, system_schema.indexes, system_schema.tables, system_traces.events, system.peer_events_v2

Host:   84759df0-8a19-497e-965f-200bdb4c1c9b
Tables: system_traces.events, system.available_ranges_v2, system.peer_events, system_auth.resource_role_permissons_index, system_auth.role_members, system_schema.types, system.IndexInfo, system.sstable_activity, system_distributed.view_build_status, system_schema.indexes, system.batches, system.transferred_ranges, system_schema.keyspaces, system_schema.tables, system_traces.sessions, system_distributed.repair_history, system_schema.aggregates, system.available_ranges, system.compaction_history, system.paxos, system.peers_v2, system.view_builds_in_progress, system.size_estimates, keyspace1.table1, system_auth.roles, system_schema.dropped_columns, test.test, system_auth.role_permissions, system_distributed.parent_repair_history, system.local, system.peer_events_v2, system.repairs, system.table_estimates, system_auth.network_permissions, system.peers, system_schema.triggers, system_schema.views, system.built_views, system.prepared_statements, system.transferred_ranges_v2, system_schema.columns, system_schema.functions, keyspace1.table2

Host:   94ed3811-12ce-487f-ac49-ae31299efa31
Tables: system.peers_v2, system.view_builds_in_progress, system_auth.resource_role_permissons_index, system_auth.role_permissions, system_schema.aggregates, system_schema.indexes, test.test, system.available_ranges_v2, system_distributed.parent_repair_history, system_schema.keyspaces, system_traces.sessions, system_auth.role_members, system_auth.network_permissions, system_schema.dropped_columns, system_schema.types, system.repairs, system.size_estimates, system_auth.roles, system_schema.tables, system_schema.views, system.paxos, system.table_estimates, system.transferred_ranges, system.peers, system.prepared_statements, system.sstable_activity, system.peer_events_v2, system.batches, system.built_views, system.compaction_history, system_traces.events, system.IndexInfo, system.local, keyspace1.table2, system.peer_events, system.transferred_ranges_v2, system_distributed.repair_history, system_distributed.view_build_status, system_schema.columns, system_schema.functions, system.available_ranges, system_schema.triggers, keyspace1.table1
```

Scanning for backups can take a long time depending on the storage type and the amount of data. 

You can use command-line options to restrict the search to a specific cluster, set of hosts, backup, and/or table(s):

```bash
/usr/share/axonops/axon-cassandra-restore \
  --storage-config-file /path/to/remote_storage_config_file.json \
  --org-id myaxonopsorg \
  --source-cluster testcluster \
  --source-hosts 026346a0-dc89-4235-ae34-552fcd453b42,84759df0-8a19-497e-965f-200bdb4c1c9b,94ed3811-12ce-487f-ac49-ae31299efa31 \
  --backup-id 2c1d9aca-5312-11ee-b686-bed50b9335ec \
  --tables keyspace1.table1,keyspace1.table2 \
  --verbose \
  --list
```

## Restoring a Backup

The `axon-cassandra-restore` tool can perform the following operations to restore a backup from remote storage:

1. [Download SSTables](#downloading-a-backup-to-a-local-directory) from remote storage.
1. [Import](#download-and-import-a-backup-using-sstableloader) downloaded SSTables into a target cluster using `sstableloader`.
1. [Create](#importing-cql-schemas-during-the-restore) table schemas in a target cluster.
1. [Download commitlogs](#point-in-time-restore-onto-a-different-cluster) to enable command-line based point-in-time restores.

The default behaviour is to only download the SSTables to a local directory.

### Downloading a backup to a local directory

This command will download the backup with ID `2c1d9aca-5312-11ee-b686-bed50b9335ec` for the 3 hosts listed in the `--list` output above into the local directory `/opt/cassandra/axonops-restore`:

```bash
/usr/share/axonops/axon-cassandra-restore \
  --storage-config-file /path/to/remote_storage_config_file.json \
  --org-id myaxonopsorg \
  --source-cluster testcluster \
  --source-hosts 026346a0-dc89-4235-ae34-552fcd453b42,84759df0-8a19-497e-965f-200bdb4c1c9b,94ed3811-12ce-487f-ac49-ae31299efa31 \
  --backup-id 2c1d9aca-5312-11ee-b686-bed50b9335ec \
  --local-sstable-dir /opt/cassandra/axonops-restore \
  --restore
```

The SSTables will be restored into directories named `{local-sstable-dir}/{host-id}/keyspace/table/` and from here
you can copy/move the files to another location or import them into a cluster using `sstableloader`.

### Download and import a backup using SSTableLoader

The above example highlights how to download the backed up files into a local directory, but it does not import them into a new cluster. The `axon-cassandra-restore` tool can load the downloaded backup files into the new cluster by passing
the `--use-sstable-loader`, `--cassandra-bin-dir`, and `--sstable-loader-options` command-line arguments.

> NOTE: Keyspaces must exist in the target cluster. If you did not create the tables remember to add the option `--restore-schema` to the command line. See [Importing CQL schemas during the restore](#importing-cql-schemas-during-the-restore).

For example, this command will download the same backup files as the previous example but it will also run `sstableloader`
to import the downloaded files into a new cluster with contact points 10.0.0.1, 10.0.0.2, and 10.0.0.3:

```bash
/usr/share/axonops/axon-cassandra-restore \
  --storage-config-file /path/to/remote_storage_config_file.json \
  --org-id myaxonopsorg \
  --source-cluster testcluster \
  --source-hosts 026346a0-dc89-4235-ae34-552fcd453b42,84759df0-8a19-497e-965f-200bdb4c1c9b,94ed3811-12ce-487f-ac49-ae31299efa31 \
  --backup-id 2c1d9aca-5312-11ee-b686-bed50b9335ec \
  --local-sstable-dir /opt/cassandra/axonops-restore \
  --restore /
  --use-sstable-loader \
  --cassandra-bin-dir /opt/cassandra/bin \
  --sstable-loader-options "-d 10.0.0.1,10.0.0.2,10.0.0.3 -u cassandra -pw cassandra"
```

> NOTE: If you are using an Apache Cassandra version installed using either the Debian or RedHat package manager, use `--cassandra-bin-dir /usr/bin` when specifying the bin directory.

### Importing CQL schemas during the restore

When a backup is imported to a cluster using `sstableloader`, it assumes the destination tables already exist and will skip the import for any undefined tables. However, it is possible to create any missing table schemas as part of the restore operation since AxonOps stores the current table schema with each backup. This can be enabled with the `--restore-schema` and `--cqlsh-options` arguments to `axon-cassandra-restore`.

Building on the example above, this command will download the files from the backup, create the schema for any missing
tables, and import the downloaded data with `sstableloader`:

```bash
/usr/share/axonops/axon-cassandra-restore \
  --storage-config-file /path/to/remote_storage_config_file.json \
  --org-id myaxonopsorg \
  --source-cluster testcluster \
  --source-hosts 026346a0-dc89-4235-ae34-552fcd453b42,84759df0-8a19-497e-965f-200bdb4c1c9b,94ed3811-12ce-487f-ac49-ae31299efa31 \
  --backup-id 2c1d9aca-5312-11ee-b686-bed50b9335ec \
  --local-sstable-dir /opt/cassandra/axonops-restore \
  --restore /
  --use-sstable-loader \
  --cassandra-bin-dir /opt/cassandra/bin \
  --sstable-loader-options "-d 10.0.0.1,10.0.0.2,10.0.0.3 -u cassandra -pw cassandra" \
  --restore-schema \
  --cqlsh-options "-u cassandra -p cassandra 10.0.0.1"
```

> NOTE: This will not create missing keyspaces. You must ensure that the target keyspaces already exist in the destination cluster before running the restore command.

#### Restore to a different table

> This feature is available in AxonOps Agent v1.0.61 or later

When restoring a single table from a backup, it is possible to use the `--dest-table` argument to load the restored data into table with a different name and/or keyspace to the original table. If you also supply the `--restore-schema` option, the new table will be created as part of the restore process.

This example shows restoring the table `keyspace1.table1` into a table named `table1_restored` in keyspace `restoreks`:

```bash
/usr/share/axonops/axon-cassandra-restore \
  --storage-config-file /path/to/remote_storage_config_file.json \
  --org-id myaxonopsorg \
  --source-cluster testcluster \
  --source-hosts 026346a0-dc89-4235-ae34-552fcd453b42,84759df0-8a19-497e-965f-200bdb4c1c9b,94ed3811-12ce-487f-ac49-ae31299efa31 \
  --backup-id 2c1d9aca-5312-11ee-b686-bed50b9335ec \
  --local-sstable-dir /opt/cassandra/axonops-restore \
  --restore /
  --use-sstable-loader \
  --cassandra-bin-dir /opt/cassandra/bin \
  --sstable-loader-options "-d 10.0.0.1,10.0.0.2,10.0.0.3 -u cassandra -pw cassandra" \
  --restore-schema \
  --cqlsh-options "-u cassandra -p cassandra 10.0.0.1" \
  --tables keyspace1.table1 \
  --dest-table restoreks.table1_restored
```

> NOTE: The destination keyspace must already exist before running the restore command.

### Point-in-time restore onto a different cluster

In cases where a quick disaster recovery is needed, or a development/debug cluster with a copy of the most up-to-date production information is needed, we can use the following approach.

In order for this feature, which was added with AxonOps Agent version 2.0.12, to work properly:

* A Backup must be performed on the live cluster after all nodes have upgraded to AxonOps Agent 2.0.12, or later.
* The Backups must contain all system tables, as well as any target keyspace/tables.
* Due to a current limitation of a single `path` parameter within the [storage configuration options](restore-tool-setup.md#storage-config-and-storage-config-file-options), the Base Remote Path setting for both the Backup and Commitlog Archiving should be identical.

To prepare the new cluster, we must first shutdown the Cassandra process on the new cluster and remove all of the on-disk data. Below is an example for shutting down a packaged-based installation of Cassandra using the default data directories:

```bash
# safely shutdown Cassandra
nodetool flush
nodetool drain
service cassandra stop

# CAUTION: delete all Cassandra data on disk within the NEW cluster
cd /var/lib/cassandra/
rm -rf commitlog/* data/* hints/* saved_caches/*
```

On the new cluster, we must update the `cluster_name` within the `cassandra.yaml` to match the `cluster_name` within the backups. You can find the `cassandra.yaml` within `/etc/cassandra/cassandra.yaml` if using the default packaged-based installation path.

> NOTE: Since the live cluster and restored cluster will have the same `cluster_name`, it is **highly** recommended that all nodes within the live cluster are firewalled away from all the nodes within the restoration cluster. While we do not restore the `peers` and `peers_v2` tables in an effort to prevent conflicts over token ownership across the two clusters, an isolated network setup is **highly** recommended.

Building on the previous examples, we'll run a similar command that adds:

* `--threads` to increase the number of parallel downloads
* `--table-uuids` to append the UUID suffix to the table directory names
* `--set-owner` to set the Linux file system owners of the restored data files and directories
* `--no-host-dir` to remove the host UUID from the file path to more cleanly restore to a Cassandra cluster's data directories
* `--local-sstable-dir` to restore the SSTables to Cassandra's data directory

Additionally, we will restore the commit logs to support point-in-time restores through `axon-cassandra-restore` by using:

* `--restore-commitlogs` to also restore any new commit logs since the target backup/snapshot
* `--local-commitlog-dir` to restore the commit logs to Cassandra's commitlog directory

Note that this command should use a single Source Host ID as [found within Cluster Overview within the AxonOps dashboard](restore-tool-setup.md/#finding-the-source-host-ids).

```bash
AGENT_ID=026346a0-dc89-4235-ae34-552fcd453b42

/usr/share/axonops/axon-cassandra-restore \
  --storage-config-file /restore-server \
  --org-id myaxonopsorg \
  --source-cluster testcluster \
  --source-hosts "${AGENT_ID}"  \
  --backup-id 2c1d9aca-5312-11ee-b686-bed50b9335ec \
  --restore \
  --threads 20 \
  --table-uuids \
  --set-owner cassandra \
  --no-host-dir \
  --local-sstable-dir /var/lib/cassandra/data \
  --restore-commitlogs \
  --local-commitlog-dir /var/lib/cassandra/commitlog
```

Once all nodes have been restored individually, we can start the new Cassandra cluster into a previous state:

```bash
service cassandra start
```
