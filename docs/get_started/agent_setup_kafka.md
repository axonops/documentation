## Install Kafka Agent

{!dynamic_pages/axon_agent/kafka_agent.md!}

## Agent Configuration

Update the `key` and `org` values within the highlighted lines of
`/etc/axonops/axon-agent.yml` below.

The values can be found by logging into
[console.axonops.cloud](https://console.axonops.cloud){target="_blank"}:

* Organization (`org`) can be found next to the logo at the top of the console.
* Agent Keys (`key`) can be found within Agent setup > Agent keys.

![Console Screenshot](agent_keys.png)

If there is a Dedicated NTP server in your Organization please uncomment and update the NTP section.

{!dynamic_pages/axon_agent/kafka_agent_config.md!}
