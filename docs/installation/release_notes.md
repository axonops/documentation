---
title: "Release 2026-02-03"
description: "AxonOps release notes. Latest features, improvements, and bug fixes."
meta:
  - name: keywords
    content: "release notes, AxonOps updates, changelog, new features"
---

## Release 2026-02-03

* axon-server: 2.0.20
    * Scheduled repair improvements, and Kafka monitoring enhancements.
* axon-dash: 2.0.23
    * Kafka management fixes and scheduled repair configuration.
* axon-agent: 2.0.16
    * Security updates and Kafka monitoring improvements.

### Fixes

* [Server] Fix segmented scheduled repairs not completing all segments.
* [Server] Fix deadlock in enhanced log collectors cleanup.
* [Server] Fix goroutine leak in repairs caused by error storms and premature timeout tracking.
* [Server] Fix misleading error response when Kafka Connect cluster has no connectors defined.
* [Server] Update Go version to address security vulnerabilities.
* [Dash] Fix Kafka topic configs not displaying for all config source types.
* [Dash] Fix misleading error response when no connectors are defined in Kafka Connect cluster.
* [Dash] Fix unnecessary dashboard template saves when editing widgets and add Save/Cancel buttons.
* [Dash] Fix Kafka Connect operations visibility for read-only users.
* [Agent] Update Go version to address security vulnerabilities (CVE-2025-61726, CVE-2025-61728).

### New Features

* [Server] Add maximum duration setting for scheduled repairs with alert on timeout.
* [Server] Add partition reassignment status tracking for Kafka topics.
* [Server] Alert when Kafka agent is configured with incorrect broker location.
* [Server] Expand schema registry support with monitoring capabilities.
* [Server] Add node type filter option for service checks in Kafka clusters.
* [Server] Support setting licence key via environment variable.
* [Server] Improve log tailing to detect and report when monitored log files become unavailable.
* [Dash] Add maximum duration setting for scheduled repairs with alert on timeout.
* [Dash] Add node type filter option for service checks in Kafka clusters.
* [Dash] Improve log tailing to detect and report when monitored log files become unavailable.
* [Agent] Automate Strimzi and K8ssandra container builds on new agent releases.
* [Agent] Alert when Kafka agent is configured with incorrect broker location.
* [Agent] Add partition reassignment status tracking for Kafka topics.

## Release 2026-01-29

* axon-agent: 2.0.15
    * Log collection improvements and Schema Registry monitoring support.

### Fixes

* [Agent] Fix rated metrics not displaying for new installs.
* [Agent] Fix edge cases in log collection when files are unavailable or deleted.

### New Features

* [Agent] Move log collector alerts to the agent for improved file monitoring.
* [Agent] Add support for node type field on health checks (requires axon-server upgrade).
* [Agent] Expand Schema Registry support with Prometheus metrics scraping.

## Release 2026-01-22

* axon-cassandra5.0-agent: 1.0.13
    * Kubernetes compatibility and metric filtering improvements.

### Fixes

* [Cassandra 5 Agent] Improve compatibility with K8ssandra deployments.
* [Cassandra 5 Agent] Filter out transient repair metrics to reduce collection overhead.

## Release 2026-01-15

* axon-dash: 2.0.22
    * Fix for self-hosted deployments.

### Fixes

* [Dash] Fix startup failure due to new configuration logic.

## Release 2026-01-13

!!! danger "Elasticsearch Upgrade Required"
    Requires Elasticsearch 7.9 or later. On-premise customers with restricted Elasticsearch permissions may need to grant additional `manage_ilm` permissions for data stream and ILM management.

* axon-server: 2.0.19
    * Elasticsearch DataStreams migration, Kafka improvements, and stability fixes for repairs.
* axon-dash: 2.0.22
    * Kafka management improvements, dashboard customization, and various UI fixes.
* AxonOps agent: 2.0.14
    * Fix for metric calculations.

### Fixes

* [Server] Fix Kafka topics not displaying associated consumer groups.
* [Server] Update dependencies to address security vulnerabilities.
* [Server] Fix Grafana integration support.
* [Server] Improve stability for non-segmented scheduled repairs.
* [Server] Stop repairs gracefully when timestamp validation errors occur.
* [Server] Fix crash caused by concurrency issue during repairs.
* [Server] Fix race condition when saving cluster data.
* [Dash] Fix clipboard copy functionality for older browsers.
* [Dash] Update Next.js to version 15.5.7 for security fixes.
* [Dash] Fix backup restore API payload.
* [Dash] Fix timezone display names.
* [Dash] Fix dashboard filter text search.
* [Dash] Fix topic sorting by cleanup policy.
* [Dash] Fix issues with the time navigation jump back button.
* [Dash] Fix control positioning in Node Details popup.
* [Dash] Prepare for Next.js v16 by migrating from deprecated environment variable methods.
* [Dash] Fix validation on the Silence Alerts form.
* [Dash] Increase API proxy timeout to 2 minutes for longer operations.
* [Dash] Update Next.js to version 15.5.9 for security fixes.
* [Dash] Fix issue loading Kafka dashboard templates.
* [Dash] Fix log viewer scrolling behavior.
* [Agent] Fix calculation and downsampling of rated metrics.

### New Features

* [Server] Migrate to Elasticsearch DataStreams for improved events storage.
* [Server] Add ability to delete and truncate Kafka topic records.
* [Server] Add support for `*.table` wildcard pattern in Adaptive Repair table exclusions.
* [Dash] Allow freeform topic entry on Kafka ACLs form.
* [Dash] Filter Kafka Connectors by connection state.
* [Dash] Add `*.table` wildcard pattern support for Adaptive Repair table exclusions.
* [Dash] Introduce improved table component for Service Checks.
* [Dash] Add support for creating custom filters on dashboards.
* [Dash] Add ability to delete and truncate Kafka topic records.
* [Dash] Add horizontal scrolling to logs viewer.
* [Dash] Display detailed information for Kafka Connect task failures.
* [Dash] Add option to replace existing dashboards during import.
* [Dash] Improve time picker interface.
* [Dash] Increase maximum length of health check names to 100 characters.

## Release 2025-12-12

* AxonOps agent: 2.0.12
    * Command-line restore tool enhancements and security updates.

### Fixes

* [Agent] Update dependencies and Go version to address security vulnerabilities.
* [Agent] Increase timeout when requesting settings from axon-server.

### New Features

* [Agent] Add option to allow segmented full repairs after running incremental repairs.
* [Agent] Add support for truncating Kafka topics.
* [Agent] Store node-level manifests for backups to speed up command-line restores.
* [Agent] Append timestamp to archived commitlog filenames.
* [Agent] Add parallelism, ownership, permissions, and commitlog restore options to `axon-cassandra-restore` tool.

## Release 2025-11-18

* AxonOps agent: 2.0.11
    * Kafka connector and S3 backup fixes.
* axon-cassandra5.0-agent: 1.0.11
    * Cassandra 5 metrics fix.

### Fixes

* [Agent] Fix error message when restarting Kafka connectors.
* [Agent] Fix S3 multipart upload errors.
* [Cassandra 5 Agent] Fix batch metrics for Cassandra 5.

## Release 2025-11-13

* axon-server: 2.0.16
    * Stability improvements for repairs, backups, and silence windows.
* axon-dash: 2.0.16
    * Kafka Connect UI and Scheduled Repair History.

### Fixes

* [Server] Fix error message when deleting backups from the database.
* [Server] Increase the Elasticsearch request timeout.
* [Server] Fix conflicting API endpoint for Kafka cluster info.
* [Server] Fix silence windows at the DC and Rack level.
* [Server] Fix concurrent map access error when serializing repairs.
* [Server] Fix display of paused backup schedules.
* [Server] Fix EOF errors in repairs.
* [Server] Improve safety of axon-server restarts.
* [Server] Fix authentication on Kafka Connect API endpoints.
* [Dash] Use more efficient method to get Kafka consumer groups.
* [Dash] Fix error when clicking on alerts in charts.
* [Dash] Use new endpoints to get metric label names and values.

### New Features

* [Server] Add integration type and name to audit logs for alerting routes.
* [Server] Improve events for scheduled repairs.
* [Dash] Add Kafka Connect UI.
* [Dash] Add Scheduled Repair History view.

## Release 2025-11-11

* axon-kafka-java-agent: 1.0.4
    * Confluent compatibility fix.

### Fixes

* [Kafka Java Agent] Fix library conflict with Confluent 7.4.12 and later.

## Release 2025-11-05

* axon-server: 2.0.15
    * Kafka schema and consumer group improvements, backup schedule fix.
* axon-dash: 2.0.15
    * Kafka consumer group fixes and configuration comparison.

### Fixes

* [Server] Fix error restarting Kafka Connect tasks when connect cluster has a different name.
* [Server] Reduce noise from Kafka consumer group debug messages.
* [Server] Fix deadlock when editing backup schedules.
* [Dash] Tweak backup status display.
* [Dash] Fix rounding tokens in repair failed token ranges view.
* [Dash] Hide the Retry Upload button on local-only backups.
* [Dash] Fix Kafka consumer groups partition assignment display.

### New Features

* [Server] Add support for raw format schemas in Kafka Schema Registry.
* [Server] Add lightweight API endpoint to list Kafka consumer groups.
* [Dash] Make actions easier to find in Cluster Overview.
* [Dash] Add configuration comparison feature for Kafka brokers.
* [Dash] Add button to navigate to parent dashboard from alerts.

## Release 2025-10-30

* AxonOps agent: 2.0.10
    * Kafka logging improvements, proxy support, and security updates.

### Fixes

* [Agent] Reduce noise in logs from Kafka transaction processing messages.
* [Agent] Update dependencies to address security vulnerabilities.
* [Agent] Skip `repaired_at` timestamp checks for non-segmented repairs.

### New Features

* [Agent] Add environment variables for configuring Schema Registry connection.
* [Agent] Add support for scraping Prometheus endpoints via a proxy.

## Release 2025-10-22

* axon-kafka-agent: 1.0.3
    * Configuration reporting improvements.

### New Features

* [Kafka Agent] Send Kafka configurations as part of node inventory.

## Release 2025-10-20

* axon-server: 2.0.14
    * Kafka improvements, Adaptive Repair fixes, and security updates.
* axon-dash: 2.0.14
    * PromQL fix and Adaptive Repair configuration options.

### Fixes

* [Server] Fix metrics filtering.
* [Server] Remove duplicated table name in repair alerts.
* [Server] Fix issues with Kafka primary node selection.
* [Server] Update dependencies to address security vulnerabilities.
* [Server] Fix saving and loading Adaptive Repair progress, segment timeout and retry handling.
* [Dash] Fix PromQL interpolation when excluding empty labels.
* [Dash] Fix missing Kafka topics in display.

### New Features

* [Server] Add environment variables for configuring schema registry support.
* [Server] Add environment variables for configuring `search_db` options.
* [Server] Add ability to restart Kafka Connect tasks.
* [Server] Cache Kafka API responses.
* [Dash] Click on a node to filter logs and events for that node.
* [Dash] Add Adaptive Repair segment timeout field.

## Release 2025-10-07

* axon-server: 2.0.13
    * Repair timeout handling and event improvements.
* axon-dash: 2.0.13
    * Kafka consumer group improvements and various fixes.

### Fixes

* [Server] Improve repair timeout handling when a node is down.
* [Server] Fix erroneous timeout errors after stopping or resetting adaptive repairs.
* [Dash] Fix sorting of Kafka consumer groups by state.
* [Dash] Fix display of "Preparing Rebalance" Kafka consumer group state.
* [Dash] Fix display of ISR alerts on Kafka Topics page.
* [Dash] Improve node selection behavior on Silence Alerts page.
* [Dash] Fix Adaptive Repair view collapsing unexpectedly.
* [Dash] Fix exception when clicking on alerts in the Alerts Dashboard.
* [Dash] Fix text box focus on Cluster Overview page.
* [Dash] Fix missing events in Adaptive Repair history.

### New Features

* [Server] Add table name to repair plan start, end, and failed events and alerts.
* [Dash] Add UI to modify Kafka consumer group offsets.
* [Dash] Improve backup operations buttons.
* [Dash] Show start, stop, and reset events in Adaptive Repair history.

## Release 2025-10-01

* axon-server: 2.0.12
    * Improved repair logging and alerting.
* axon-dash: 2.0.12
    * Font loading fixes and Kafka performance improvement.

### Fixes

* [Dash] Fix font loading for SaaS and Linux desktop clients.
* [Dash] Use more efficient API call to get Kafka consumer group details.
* [Dash] Fix PromQL query interpolation.

### New Features

* [Server] Log an event when a repair segment completes successfully after a previous failure.
* [Server] Include the table name in "repair plan ended with errors" alert messages.

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
* AxonOps agent: 2.0.7
    * Strengthen connection management and environment variable configurations for Kafka agent.

### Fixes

* [Server] Stop `clearing snapshot timed out` errors and prevent erroneously raised alerts.
* [Agent] Remove duplicate environment variables used to configure Kafka cluster name. Fixes an issue when running with Strimzi.
* [Agent] Reconnect idle Kafka agent connections instead of treating them as failed or terminated connections.

## Release 2025-08-20

* axon-server: 2.0.7
    * Fixes status messaging for backup/repairs as well as select thread pool metrics.

### Fixes

* [Server] Fix critical issue in backup and repair messaging.
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
* AxonOps agent: 2.0.6
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
* [Dash] Improve Firefox compatibility.
* [Dash] Disable auto-saving of adaptive repair settings and add ability to revert settings.

### New Features

* [Server] Replace the `elastic_hosts` configuration key with the forward-looking `search_db` key in the default axon-server.yml.
* [Agent] Add `--validate` to `axon-cassandra-restore` tooling that verifies all files referenced by a backup manifest are still accessible.
* [Dash] Add deeplinking URLs for better Workbench support.
* [Dash] New fluid progress animation for adaptive repairs.

## Release 2025-07-28

* axon-server: 2.0.4
    * Internal messages for repairs and backups have changed.
* AxonOps agent: 2.0.5
    * Internal messages for repairs and backups have changed.
    * OpenSearch support required changes that could have affected Elasticsearch access
      code. Routinely tested with our nightly builds.
* axon-dash: 2.0.8
    * Mainly internal changes and bug fixes.

### Fixes

* [Server, Agent] Improve resilience of repair and backup messages.
* [Server] Update Go and dependencies to eliminate known security vulnerabilities.
* [Server] Fix issues displayed when there are no failed adaptive repair segments.
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

* AxonOps agent: 2.0.4
* axon-kafka3-agent: 1.0.1
* axon-kafka2-agent: 1.0.1

### Fixes

* [Agent] Improve log collector logic and reliability.
* [Agent] Update Go and dependencies to eliminate known security vulnerabilities.

### New Features

* [Agent, Kafka Agent] Allow Kafka Agent to be configured solely with environment variables.
