---
title: "Snapshot Import"
description: "Import existing Cassandra snapshots into AxonOps for restore workflows."
meta:
  - name: keywords
    content: "Cassandra snapshot import, AxonOps restore, snapshot management"
---

# Snapshot Import

Snapshot import lets you bring existing Cassandra snapshots under AxonOps management so they can be restored through the UI.

## When to use snapshot import

- You created snapshots manually (or via another tool) and want to restore with AxonOps.
- You migrated data directories and need AxonOps to recognize snapshots.

## How it works

AxonOps maps a snapshot directory into its internal snapshot catalog so it can be selected from the Restore view. The agent updates the snapshot structure and permissions to align with AxonOps restore workflows.

## Requirements

- The snapshot directories exist under the configured Cassandra data paths.
- axon-agent has filesystem access to the snapshot directories.

## Notes

- Snapshot import does not upload data to remote storage.
- For point-in-time restore, enable commit log archiving and use the PITR workflow.
