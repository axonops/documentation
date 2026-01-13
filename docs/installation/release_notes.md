---
title: "Release 2025-08-29"
description: "AxonOps release notes. Latest features, improvements, and bug fixes."
meta:
  - name: keywords
    content: "release notes, AxonOps updates, changelog, new features"
---

## Release 2025-01-13

* axon-server: 2.0.17
    * Elasticsearch DataStreams migration, Kafka improvements, and stability fixes for repairs.
    * **Note:** Requires Elasticsearch 7.9 or later. On-premise customers with restricted Elasticsearch permissions may need to grant additional permissions for data stream and ILM management.
* axon-dash: 2.0.19
    * Kafka management improvements, dashboard customization, and various UI fixes.
* axon-agent: 2.0.14
    * Fix for metric calculations.

### Fixes

* [Server] Fix Kafka topics not displaying associated consumer groups.
* [Server] Update dependencies to address security vulnerabilities.
* [Server] Update dependencies to address additional security vulnerabilities.
* [Server] Fix Grafana integration support. Note: Multiple organization IDs are no longer supported.
* [Server] Improve stability for non-segmented scheduled repairs.
* [Server] Stop repairs gracefully when timestamp validation errors occur.
* [Server] Fix crash caused by concurrency issue during repairs.
* [Server] Fix race condition when saving cluster data.
* [Dash] Hide the add plugin button for Kafka Connect until functionality is available.
* [Dash] Fix clipboard copy functionality for older browsers.
* [Dash] Remove unnecessary Actions column from cluster view table.
* [Dash] Update Next.js to version 15.5.7 for security fixes.
* [Dash] Fix backup restore API payload.
* [Dash] Fix timezone display names.
* [Dash] Fix dashboard filter text search.
* [Dash] Fix topic sorting by cleanup policy.
* [Dash] Fix issues with the time navigation jump back button.
* [Dash] Prepare for Next.js v16 by migrating from deprecated environment variable methods.
* [Dash] Fix validation on the Silence Alerts form.
* [Dash] Increase API proxy timeout to 2 minutes for longer operations.
* [Dash] Update Next.js to version 15.5.9 for security fixes.
* [Dash] Fix issue loading Kafka dashboard templates.
* [Dash] Fix log viewer scrolling behavior.
* [Dash] Fix control positioning in Node Details popup.
* [Agent] Fix calculation and downsampling of rated metrics.

### New Features

* [Server] Migrate to Elasticsearch DataStreams for improved events storage.
* [Server] Add ability to delete and truncate Kafka topic records.
* [Server] Add support for `*.table` wildcard pattern in Adaptive Repair table exclusions.
* [Server] Use the events retention time as the default rollover time for ILM data streams.
* [Dash] Allow freeform topic entry on Kafka ACLs form.
* [Dash] Filter Kafka Connectors by connection state.
* [Dash] Add `*.table` wildcard pattern support for Adaptive Repair table exclusions.
* [Dash] Introduce improved table component, currently available for Service Checks.
* [Dash] Add support for creating custom filters on dashboards.
* [Dash] Add ability to delete and truncate Kafka topic records.
* [Dash] Add horizontal scrolling to logs viewer.
* [Dash] Display detailed information for Kafka Connect task failures.
* [Dash] Add option to replace existing dashboards during import.
* [Dash] Improve time picker interface.
* [Dash] Increase maximum length of health check names to 100 characters.


## Release 2025-08-29

* axon-server: 2.0.10
    * Fix ordering when displaying event logs.

### Fixes

* [Server] Fix event log sorting with a faster tie-breaker mechanism.

## Release 2025-08-28

* axon-server: 2.0.9
    * Update dashboard templates for select installations.

### Fixes

* [Server] Update dashboard templates to support missing thread pool metrics for certain installations.

## Release 2025-08-21

* axon-server: 2.0.8
    * Prevents erroneously raised snapshot errors.
* axon-agent: 2.0.7
    * Strengthen connection management and environment variable configurations for Kafka agent.

### Fixes

* [Server] Stop `clearing snapshot timed out` errors and prevent erroneously raised alerts.
* [Agent] Remove duplicate environment variables used to configure Kafka cluster name. Fixes an issue when running with Strimzi.
* [Agent] Reconnect idle Kafka agent connections instead of treating them as failed or terminated connections.

## Release 2025-08-20

* axon-server: 2.0.7
    * Fixes status messaging for backup/repairs as well as select thread pool metrics.

### Fixes

* [Server] Fix critical issue in backup and repair messaging (introduced in axon-server 2.0.4).
* [Server] Fix select dashboard thread pool templates.

## Release 2025-08-15

* axon-dash: 2.0.6
    * Fixes a couple of rare race conditions seen at startup.

### Fixes

* [Server] Fix race condition getting org details during startup.
* [Server] Fix race condition getting license details during startup.

## Release 2025-08-11

* axon-dash: 2.0.10
    * Fixes for user permissions and editing Alert Definitions.

### Fixes

* [Dash] Fix permissions issue when a user has multiple roles assigned.
* [Dash] Fix issue with certain strings causing blank fields when editing Alert Definitions.

## Release 2025-08-06

* axon-server: 2.0.5
    * Mainly new features and simple bug fixes.
* axon-agent: 2.0.6
    * Introduction of new, efficient log collector. Tested thoroughly with edge cases.
* axon-dash: 2.0.9
    * Fixes for adaptive repairs and Alerts dashboard timeline, along with new features.

### Fixes

* [Server] Handle race condition seen where restarting axon-server while running adaptive repairs would cancel the repair.
* [Agent] Redesign log collectors to avoid throwing too many open files errors and use inotify file handles efficiently.
* [Dash] Remove broken metrics tab from the Kafka broker view.
* [Dash] Ensure all alerts are displayed on the Alerts dashboard timeline.

### Customer Requests

* [Server] Failed backups have been downgraded from Critical (red) alerts to Warning (yellow) alerts, reserving Critical alerts for operational issues.
* [Dash] Improve Firefox compatibilty.
* [Dash] Disable auto-saving of adaptive repair settings and add ability to revert settings.

### New Features

* [Server] Replace the `elastic_hosts` configuration key with the forward-looking `search_db` key in the default axon-server.yml.
* [Agent] Add `--validate` to `axon-cassandra-restore` tooling that verifies all files referenced by a backup manifest are still accessible.
* [Dash] Add deeplinking URLs for better Workbench support.
* [Dash] New fluid progress animation for adaptive repairs.

## Release 2025-07-28

* axon-server: 2.0.4
    * Internal messages for repairs and backups have changed.
* axon-agent: 2.0.5
    * Internal messages for repairs and backups have changed.
    * OpenSearch support required changes that could have affected Elasticsearch access
      code. Routinely tested with our nightly builds.
* axon-dash: 2.0.8
    * Mainly internal changes and bug fixes.

### Fixes

* [Server, Agent] Improve resilience of repair and backup messages.
* [Server] Update Go and dependencies to eliminate known security vulnerabilities.
* [Server] Fix issues displayed when there are no failed adapative repair segments.
* [Agent] Fix concurrency issues for service checks.
* [Agent] Fix security issues when `disable_command_exec` is set to `true`.
* [Dash] Ensure the default shell that appears in the dashboard matches the backend `/bin/sh`.
* [Dash] Fix tooltip for button to kill the Kafka process.
* [Dash] No longer rely on externally-hosted fonts.
* [Dash] No longer present non-functioning integration actions to read-only users.
* [Dash] Fix internal permissions logic.
* [Dash] Remove unused internal dashboard template model definition.
* [Dash] Upgrade AppImage.

### Customer Requests

* [Server] Make alert emails user friendly.
* [Server] Add ability to log alerts to file for ingestion by external log readers.

### New Features

* [Server] Introduce OpenSearch support.
* [Dash] Filters can now be customized on new dashboards.
* [Dash] Allow restoring snapshots to new keyspace/tables when the keyspace/table no longer exists.

## Release 2025-07-01

* axon-dash: 2.0.7

### Fixes

* [Dash] Allow deleting dashboards that contain widgets.
* [Dash] Remove PDF dependency preventing axon-dash RPM package installation on RHEL 9.

### Customer Requests

* [Dash] Improve Firefox compatibility by no longer using experimental Javascript features.

## Release 2025-06-26

* axon-kafka3-agent: 1.0.2

### Fixes

* [Kafka Agent] Remove override within the agent configuration and apply it the codebase.

## Release 2025-06-24

* axon-agent: 2.0.4
* axon-kafka3-agent: 1.0.1
* axon-kafka2-agent: 1.0.1

### Fixes

* [Agent] Improve log collector logic and reliability.
* [Agent] Update Go and dependencies to eliminate known security vulnerabilities.

### New Features

* [Agent, Kafka Agent] Allow Kafka Agent to be configured solely with environment variables.
