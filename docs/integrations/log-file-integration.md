---
title: "Send Notifications to Log Files"
description: "Configure log file output in AxonOps. Write alerts to log files."
meta:
  - name: keywords
    content: "log file integration, alert logging, file output"
search:
  boost: 8
---

# Send Notifications to Log Files

Unlike the other integrations, the Log Files Integration is configured by adding the `alert_log` key to your `axon-server.yml`, typically located at `/etc/axonops/axon-server.yml`.

When `alert_log.enabled` is `true`, logs will be written to `alert_log.path` for consumption by external services like Splunk.

```yaml
alert_log:
  enabled: true
  path: /var/log/axonops/axon-server-alert.log
  max_size_mb: 50
  max_files: 5
```

`max_size_mb` and `max_files` are used to define how log rotation is handled.