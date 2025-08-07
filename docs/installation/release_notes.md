## Release 2024-08-06

* Axon Server: 2.0.5
    * Risk: Low.
    * Mainly new features and simple bug fixes.
* Axon Agent: 2.0.6
    * Risk: Medium.
    * Introduction of new, efficient log collector. Tested thoroughly with edge cases.
* Axon Dash: 2.0.9
    * Risk: Low.
    * Fixes for adaptive repairs and Alerts dashboard timeline, along with new features.

### Bug Fixes / Hardening

* [Server] Handle race condition seen where restarting axon-server while running adaptive repairs would cancel the repair.
* [Agent] Redesign log collectors to avoid throwing too many open files errors and use inotify file handles efficiently.
* [Dash] Remove broken metrics tab from the Kafka broker view.
* [Dash] Ensure all alerts are displayed on the Alerts dashboard timeline.

### Customer Requests

* [Server] Failed backups have been downgraded from Critical (red) alerts to Warning (yellow) alerts, reserving Critical alerts for operational issues.
* [Dash] Improve Firefox compatibilty.
* [Dash] Disable auto-saving of adaptive repair settings and add ability to revert settings.

### New Features

* [Server, Agent] Add Prometheus scraper support to the axon-agent.
* [Server] Replace the `elastic_hosts` configuration key with the forward-looking `search_db` key in the default axon-server.yml.
* [Server] Retrieve Kafka configuration and broker ID values from the JVM and display then within the UI and APIs.
* [Agent] Add `--validate` to `axon-cassandra-restore` tooling that verifies all files referenced by a backup manifest are still accessible.
* [Dash] Add deeplinking URLs for better Workbench support.
* [Dash] New fluid progress animation for adaptive repairs.

## Release 2024-07-28

* Axon Server: 2.0.4
    * Risk: Medium.
    * Internal messages for repairs and backups have changed.
* Axon Agent: 2.0.5
    * Risk: Medium.
    * Internal messages for repairs and backups have changed.
    * OpenSearch support required changes that could have affected Elasticsearch access
      code. Routinely tested with our nightly builds.
* Axon Dash: 2.0.8
    * Risk: Low.
    * Mainly internal changes and bug fixes.

### Bug Fixes / Hardening

* [Server, Agent] Improve resilience of repair and backup messages.
* [Server] Update Go and dependencies to eliminate known security vulnerabilities.
* [Server] Fix nil pointer dereference in MQTT broker.
* [Server] Fix issues displayed when there are no failed adapative repair segments.
* [Server] Disable call home to minimize collected data.
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

## Release 2024-07-01

* Axon Dash: 2.0.7
    * Risk: Low.

### Bug Fixes / Hardening

* [Dash] Allow deleting dashboards that contain widgets.
* [Dash] Remove PDF dependency preventing Axon Dash RPM package installation on RHEL 9.

### Customer Requests

* [Dash] Improve Firefox compatibility by no longer using experimental Javascript features.

## Release 2024-06-26

* Axon Kafka Agent: 1.0.2
    * Risk: Low.

### Bug Fixes / Hardening

* [Kafka Agent] Remove override within the agent configuration and apply it the codebase.

## Release 2024-06-24

* Axon Agent: 2.0.4
    * Risk: Low.
* Axon Kafka Agent: 1.0.1
    * Risk: Low.

### Bug Fixes / Hardening

* [Agent] Improve log collector logic and reliability.
* [Agent] Update Go and dependencies to eliminate known security vulnerabilities.

### New Features

* [Agent, Kafka Agent] Allow Kafka Agent to be configured solely with environment variables.
