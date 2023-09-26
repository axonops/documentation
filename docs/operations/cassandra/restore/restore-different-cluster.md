# Restore a backup to a different cluster

*Follow this procedure to restore an AxonOps backup from remote storage onto a different cluster*

> NOTE: This facility is only available for backups created using AxonOps Agent version 1.0.58 or later

AxonOps Agent from version 1.0.58 onwards includes a command-line tool which can be used to restore a backup created by
AxonOps from remote storage (e.g. S3, GCS). This tool connects directly to your remote storage and does not require an
AxonOps server or an active AxonOps Cloud account in order to function.

## Installing the Cassandra Restore Tool

The AxonOps Cassandra Restore tool is included in the AxonOps Agent package.

#### Installing on Debian / Ubuntu
```bash
apt-get install curl gnupg
curl https://packages.axonops.com/apt/repo-signing-key.gpg | sudo apt-key add -
echo "deb https://packages.axonops.com/apt axonops-apt main" | sudo tee /etc/apt/sources.list.d/axonops-apt.list
sudo apt-get update
sudo apt-get install axon-agent
```

#### Installing on CentOS / RedHat
```bash
sudo tee /etc/yum.repos.d/axonops-yum.repo << EOL
[axonops-yum]
name=axonops-yum
baseurl=https://packages.axonops.com/yum/
enabled=1
repo_gpgcheck=0
gpgcheck=0
EOL
sudo yum install axon-agent
```

After the package has been installed you can find the Cassandra Restore Tool at `/usr/share/axonops/axon-cassandra-restore`.

Run the tool with `--help` to see the available options:
```bash
~# /usr/share/axonops/axon-cassandra-restore --help
Usage of /usr/share/axonops/axon-cassandra-restore:
  -i, --backup-id string                UUID of the backup to restore
      --cassandra-bin-dir string        Where the Cassandra binary files are stored (e.g. /opt/cassandra/bin)
      --cqlsh-options string            Options to pass to cqlsh when restoring a table schema
  -h, --help                            Show command-line help
  -l, --list                            List backups available in remote storage
  -d, --local-sstable-dir string        A local directory in which to store sstables downloaded from backup storage
      --org-id string                   ID of the AxonOps organisation from which the backup was created
  -r, --restore                         Restore a backup from remote storage
      --restore-schema                  Set this when using --use-sstable-loader to restore the CQL schema for each table. Keyspaces must already exist.
  -c, --source-cluster string           The name of the cluster from which to restore
  -s, --source-hosts string             Comma-separated list containing host IDs for which to restore backups
      --sstable-loader-options string   Options to pass to sstableloader when restoring a backup
      --storage-config string           JSON-formatted remote storage configuration
  -t, --tables string                   Comma-separated list of keyspace.table to restore. Defaults to all tables if omitted.
      --use-sstable-loader              Use sstableloader to restore the backup. Requires --sstable-loader-options and --cassandra-bin-dir.
  -v, --verbose                         Show verbose output when listing backups
      --version                         Show version information and exit
```

## Listing the available backups

> NOTE: The host IDs used in this tool are the ID given to each host by AxonOps and do not relate to the Cassandra
> host ID. You can find the AxonOps host ID by selecting the node on the Cluster Overview page of the AxonOps dashboard
> and looking at the Agent ID field.

To list the backups available in the remote storage bucket you can run the tool with the `--list` option.
For example to list the backups in an Amazon S3 bucket you could use a command similar to this:

```bash
/usr/share/axonops/axon-cassandra-restore --list \
  --org-id myaxonopsorg \
  --storage-config '{"type":"s3","path":"/axonops-cassandra-backups","access_key_id":"MY_AWS_ACCESS_KEY","secret_access_key":"MY_AWS_SECRET_ACCESS_KEY","region":"eu-west-3"}'
```
The restore tool will then scan the specified S3 bucket for AxonOps backups and it will display the
date and backup ID for any backups it finds:
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
If you pass the `--verbose` option when listing backups it will show the list of nodes and tables in each backup,
for example:
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

Scanning for backups can take a long time depending on the storage type and the amount of data, so you can use
command-line options to restrict the search. For example this will restrict the search to a specific backup, 
cluster, hosts and tables:
```bash
/usr/share/axonops/axon-cassandra-restore --list \
  --verbose \
  --org-id myaxonopsorg \
  --storage-config '{"type":"s3","path":"/axonops-cassandra-backups","access_key_id":"MY_AWS_ACCESS_KEY","secret_access_key":"MY_AWS_SECRET_ACCESS_KEY","region":"eu-west-3"}' \
  --backup-id 2c1d9aca-5312-11ee-b686-bed50b9335ec \
  --source-cluster testcluster \
  --source-hosts 026346a0-dc89-4235-ae34-552fcd453b42,84759df0-8a19-497e-965f-200bdb4c1c9b
  --tables keyspace1.table1,keyspace1.table2
```

## Restoring a Backup

The `axon-cassandra-restore` tool can perform the following operations to restore a backup from remote storage:
1. Download the sstable files from the bucket
2. Create table schemas in the target cluster
3. Import the downloaded sstable files into the target cluster using `sstableloader`

The default behaviour is to only download the sstable files to a local directory.

### Downloading a backup to a local directory

This command will download the backup with ID `2c1d9aca-5312-11ee-b686-bed50b9335ec` for the 3 hosts listed in the
`--list` output above into the local directory `/opt/cassandra/axonops-restore`
```bash
/usr/share/axonops/axon-cassandra-restore \
  --restore \
  --org-id myaxonopsorg \
  --storage-config '{"type":"s3","path":"/axonops-cassandra-backups","access_key_id":"MY_AWS_ACCESS_KEY","secret_access_key":"MY_AWS_SECRET_ACCESS_KEY","region":"eu-west-3"}' \
  --source-cluster testcluster \
  --backup-id 2c1d9aca-5312-11ee-b686-bed50b9335ec \
  --source-hosts 026346a0-dc89-4235-ae34-552fcd453b42,84759df0-8a19-497e-965f-200bdb4c1c9b,94ed3811-12ce-487f-ac49-ae31299efa31 \
  --local-sstable-dir /opt/cassandra/axonops-restore
```
The sstable files will be restored into directories named `{local-sstable-dir}/{host-id}/keyspace/table/` and from here
you can copy/move the files to another location or import them into a cluster using `sstableloader`.

### Download and import a backup in a single operation

The above example shows how to download the backed up files into a local directory but it does not import them into
a new cluster. You can make the `axon-cassandra-restore` tool do this for you after it downloads the files by passing
the `--use-sstable-loader`, `--cassandra-bin-dir` and `--sstable-loader-options` command-line arguments.

For example this command will download the same backup files as the previous example but it will also run `sstableloader`
to import the downloaded files into a new cluster with contact points 10.0.0.1, 10.0.0.2 and 10.0.0.3:
```bash
/usr/share/axonops/axon-cassandra-restore \
  --restore \
  --org-id myaxonopsorg \
  --storage-config '{"type":"s3","path":"/axonops-cassandra-backups","access_key_id":"MY_AWS_ACCESS_KEY","secret_access_key":"MY_AWS_SECRET_ACCESS_KEY","region":"eu-west-3"}' \
  --source-cluster testcluster \
  --backup-id 2c1d9aca-5312-11ee-b686-bed50b9335ec \
  --source-hosts 026346a0-dc89-4235-ae34-552fcd453b42,84759df0-8a19-497e-965f-200bdb4c1c9b,94ed3811-12ce-487f-ac49-ae31299efa31 \
  --local-sstable-dir /opt/cassandra/axonops-restore \
  --use-sstable-loader \
  --cassandra-bin-dir /opt/cassandra/bin \
  --sstable-loader-options "-d 10.0.0.1,10.0.0.2,10.0.0.3 -u cassandra -pw cassandra"
```

#### Importing CQL schemas during the restore

When a backup is imported to a cluster using `sstableloader` it assumes that the destination tables already exist and
will skip the import for any that are missing. AxonOps backs up the current table schema with each backup so it is
possible to create any missing tables as part of the restore operation. This can be enabled with the `--restore-schema`
and `--cqlsh-options` arguments to `axon-cassandra-restore`.

Building on the example above this command will download the files from the backup, create the schema for any missing
tables, and import the downloaded data with `sstableloader`:
```bash
/usr/share/axonops/axon-cassandra-restore \
  --restore \
  --org-id myaxonopsorg \
  --storage-config '{"type":"s3","path":"/axonops-cassandra-backups","access_key_id":"MY_AWS_ACCESS_KEY","secret_access_key":"MY_AWS_SECRET_ACCESS_KEY","region":"eu-west-3"}' \
  --source-cluster testcluster \
  --backup-id 2c1d9aca-5312-11ee-b686-bed50b9335ec \
  --source-hosts 026346a0-dc89-4235-ae34-552fcd453b42,84759df0-8a19-497e-965f-200bdb4c1c9b,94ed3811-12ce-487f-ac49-ae31299efa31 \
  --local-sstable-dir /opt/cassandra/axonops-restore \
  --use-sstable-loader \
  --cassandra-bin-dir /opt/cassandra/bin \
  --sstable-loader-options "-d 10.0.0.1,10.0.0.2,10.0.0.3 -u cassandra -pw cassandra" \
  --restore-schema \
  --cqlsh-options `-u cassandra -p cassandra 10.0.0.1`
```
> NOTE: This will not create missing keyspaces. You must ensure that the target keyspaces already exist in the
> destination cluster before running the restore command.

## Storage Config Examples

The AxonOps Cassandra restore tool can restore backups from any remote storage supported by AxonOps for backups. The
`--storage-config` command-line option configures the type of remote storage and the credentials required for access.

Here are some examples of the most common storage types:

#### Local filesystem
```bash
--storage-config '{"type":"local","path":"/backups/cassandra"}'
```
#### Amazon S3
```bash
--storage-config '{"type":"s3","path":"/axonops-cassandra-backups","access_key_id":"MY_AWS_ACCESS_KEY","secret_access_key":"MY_AWS_SECRET_ACCESS_KEY","region":"eu-west-3"}'
```
#### Azure Blob Storage
```bash
--storage-config '{"type":"azureblob","account":"MY_AZURE_ACCOUNT_NAME","key":"MY_AZURE_STORAGE_KEY"}'
```
#### Google Cloud Storage
```bash
--storage-config '{"type":"googlecloudstorage","location":"us","service_account_credentials":"ESCAPED_JSON_PRIVATE_KEY"}'
```
