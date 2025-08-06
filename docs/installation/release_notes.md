# Release 2024-08-06

* Axon Server: 2.0.5
* Axon Agent: 2.0.6
* Axon Dash: 2.0.9

## Bug Fixes / Hardening

* [Axon Server] Handle race condition seen where restarting axon-server while running adaptive repairs would cancel the repair.
* [Axon Agent] Add `--validate` to `axon-cassandra-restore` tooling that verifies all files referenced by a backup manifest are still accessible.
* [Axon Agent] Redesign log collectors to avoid throwing too many open files errors and use inotify file handles efficiently.
* [Axon Dash] Remove broken metrics tab from the Kafka broker view.
* [Axon Dash] Ensure all alerts are displayed on the Alerts dashboard timeline.

## Customer Requests

* [Axon Server] Failed backups have been downgraded from Critical (red) alerts to Warning (yellow) alerts, reserving Critical alerts for operational issues.
* [Axon Dash] Improve Firefox compatibilty.
* [Axon Dash] Disable auto-saving of adaptive repair settings and add ability to revert settings.

## New Features

* [Axon Server, Axon Agent] Add Prometheus scraper support to the axon-agent.
* [Axon Server] Replace the `elastic_hosts` configuration key with the forward-looking `search_db` key in the default axon-server.yml.
* [Axon Server] Retrieve Kafka configuration and broker ID values from the JVM and display then within the UI and APIs.
* [Axon Dash] Add deeplinking URLs for better Workbench support.
* [Axon Dash] New fluid progress animation for adaptive repairs.
