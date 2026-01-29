---
title: "Backup Retention and Purge"
description: "AxonOps backup retention and purge behavior. How remote backups are expired and deleted."
meta:
  - name: keywords
    content: "Cassandra backup retention, backup purge, AxonOps backup cleanup"
---

# Backup Retention and Purge

AxonOps enforces retention for remote backups by periodically purging expired backups from the remote storage location.

## How purge works

- The agent tracks backup metadata and retention settings.
- On a scheduled interval, it evaluates which backups are outside retention.
- Expired backups are deleted from remote storage.
- Purge runs per backup location and does not affect active backups.

## What gets deleted

- Snapshot manifests and SSTable objects for expired backups
- Remote-only artifacts for commit log archiving (if enabled)

## Retention strategy guidance

- Keep retention aligned with compliance requirements and recovery objectives.
- Ensure remote storage lifecycle policies do not conflict with AxonOps purge schedules.
- Use a longer retention for critical keyspaces or compliance workloads.

## Troubleshooting

- If purge fails, check remote storage credentials and network access.
- Review AxonOps agent logs for error details.
- Verify that the configured remote path is correct and writable.
