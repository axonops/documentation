---
title: "Installing the Cassandra Restore Tool"
description: "Install and configure the AxonOps Cassandra Restore Tool for backup recovery."
meta:
  - name: keywords
    content: "Cassandra restore tool, AxonOps backup recovery, axon-cassandra-restore"
---

# Installing the Cassandra Restore Tool

The AxonOps Cassandra Restore tool is included in the AxonOps Agent package.

#### Installing on Debian / Ubuntu

```bash
sudo apt-get update
sudo apt-get install -y curl gnupg ca-certificates
curl -L https://packages.axonops.com/apt/repo-signing-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/axonops.gpg
echo "deb [arch=arm64,amd64 signed-by=/usr/share/keyrings/axonops.gpg] https://packages.axonops.com/apt axonops-apt main" | sudo tee /etc/apt/sources.list.d/axonops-apt.list
sudo apt-get update
sudo apt-get install AxonOps agent
```

#### Installing on CentOS / Red Hat

```bash
sudo tee /etc/yum.repos.d/axonops-yum.repo << EOL
[axonops-yum]
name=axonops-yum
baseurl=https://packages.axonops.com/yum/
enabled=1
repo_gpgcheck=0
gpgcheck=0
EOL
sudo yum install AxonOps agent
```

After the package has been installed you can find the Cassandra Restore Tool at `/usr/share/axonops/axon-cassandra-restore`.

Run the tool with `--help` to see the available options:
```
~# /usr/share/axonops/axon-cassandra-restore --help
ERROR: You must specify exactly one of --restore, --list or --verify
Usage of /usr/share/axonops/axon-cassandra-restore:
  -i, --backup-id string                UUID of the backup to restore
      --cassandra-bin-dir string        Where the Cassandra binary files are stored (e.g. /opt/cassandra/bin)
      --commitlog-end int               End time for commitlog restore as Unix timestamp in milliseconds. Defaults to current time if not specified.
      --commitlog-start int             Start time for commitlog restore as Unix timestamp in milliseconds. Defaults to snapshot time if restoring a snapshot.
      --cqlsh-options string            Options to pass to cqlsh when restoring a table schema
      --dest-table string               The name of the destination table for the restore in keyspace.table format. Requires --tables with a single source table.
      --dir-mode string                 Octal permissions for restored directories (default: 0750)
      --file-mode string                Octal permissions for restored files (default: 0640)
  -h, --help                            Show command-line help
      --legacy-scan-mode                Force using the slower legacy scan mode to find backups created by older versions of AxonOps
  -l, --list                            List backups available in remote storage
      --local-commitlog-dir string      Directory to download commitlog segments into
  -d, --local-sstable-dir string        A local directory in which to store sstables downloaded from backup storage
      --no-host-dir                     Don't create a directory for each host when restoring files. Only valid if downloading the backup for a single host.
      --org-id string                   ID of the AxonOps organisation from which the backup was created
  -r, --restore                         Restore a backup from remote storage
      --restore-commitlogs              Download commitlog segments from remote storage
      --restore-peerlist                Enable restoring the system.peers and system.peers_v2 tables (disabled by default)
      --restore-schema                  Set this when using --use-sstable-loader to restore the CQL schema for each table. Keyspaces must already exist.
      --set-owner string                Set ownership of restored files/directories (user, user.group, or user:group). Requires root.
  -e, --skip-existing-files             Don't download files that already exist in the local destination path
  -c, --source-cluster string           The name of the cluster from which to restore
  -s, --source-hosts string             Comma-separated list containing host IDs for which to restore backups
      --sstable-loader-options string   Options to pass to sstableloader when restoring a backup
      --storage-config string           JSON-formatted remote storage configuration
      --storage-config-file string      Path to a file containing JSON-formatted remote storage configuration
      --table-uuids                     Include table UUIDs as a suffix in the directory name when restoring
  -t, --tables string                   Comma-separated list of keyspace.table to restore. Defaults to all tables if omitted.
      --threads int                     Number of parallel operations to run (default: 1) (default 1)
      --use-sstable-loader              Use sstableloader to restore the backup. Requires --sstable-loader-options and --cassandra-bin-dir.
  -v, --verbose                         Show verbose output when listing backups
      --verify                          Check if all required files are available to restore a backup
      --version                         Show version information and exit
```

## Finding the Source Host IDs

The `--source-hosts` IDs used by `axon-cassandra-restore` are the IDs given to each host by AxonOps and do **not** relate to the Cassandra host ID as seen in `nodetool info`. 

You can find the AxonOps host ID by selecting the node on the `Cluster Overview` page of the AxonOps dashboard and looking at the `Agent ID` field.

## Storage Config and Storage Config File options

> **The `--storage-config-file` option was added to v1.0.95 and later of AxonOps Agent**

The `axon-cassandra-restore` tool has two options when passing the remote storage configuration:

* reference a [pre-populated JSON file](#storage-config-file-examples) to `--storage-config-file`
* pass a [JSON-formatted string](#storage-config-examples) to `--storage-config`

> **NOTE:** You can only use one of the options when restoring a backup. 

### Storage Config File Examples

This method is ideal when restoring across multiple nodes in a cluster and when running verification tests since this file can easily be transferred across nodes and simplifies the command line arguments.

Most parameters are straightforward and match the settings found in the AxonOps Backup GUI, including the `path` parameter which matches the `Base Remote Path` setting.

Below are some example files that can be passed into the `--storage-config-file` argument.

#### Local filesystem
```json
{
  "type": "local",
  "path": "/backups/cassandra"
}
```
#### Amazon S3
```json
{
  "type": "s3",
  "path": "/axonops-cassandra-backups",
  "access_key_id": "MY_AWS_ACCESS_KEY",
  "secret_access_key": "MY_AWS_SECRET_ACCESS_KEY",
  "region": "eu-west-3"
}
```
#### Azure Blob Storage
```json
{
  "type": "azureblob",
  "account": "MY_AZURE_ACCOUNT_NAME",
  "key": "MY_AZURE_STORAGE_KEY"
}
```
#### Google Cloud Storage
```json
{
  "type": "googlecloudstorage",
  "location": "us",
  "service_account_credentials": "ESCAPED_JSON_PRIVATE_KEY"
}
```
#### SSH/SFTP
```json
{
  "type": "sftp",
  "host": "<sftp_server_hostname>",
  "port": "22",
  "path": "/backup/path",
  "user": "<sftp_username>",
  "key_file": "~/private/key/file"
}
```
#### SSH/SFTP with password
```json
{
  "type": "sftp",
  "host": "<sftp_server_hostname>",
  "port": "22",
  "path": "/backup/path",
  "user": "<sftp_username>",
  "pass": "<sftp_password>"
}
```

### Storage Config Examples

This legacy command-line option configures the type of remote storage and the credentials required for access in an in-line format.

Here are some examples of the most common storage types that can be passed to `--storage-config`.

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
#### SSH/SFTP
```sh
--storage-config '{"type":"sftp","host":"<sftp_server_hostname>","port":"22","path":"/backup/path","user":"<sftp_username>","key_file":"~/private/key/file"}'
```
#### SSH/SFTP with password
```sh
--storage-config '{"type":"sftp","host":"<sftp_server_hostname>","port":"22","path":"/backup/path","user":"<sftp_username>","pass":"<sftp_password>"}'
```
