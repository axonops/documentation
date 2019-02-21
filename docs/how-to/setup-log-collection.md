AxonOps dashboards provides a comprehensive set of charts with an embedded view for logs and events. The goal is to correlate metrics with logs/events as you can zoom in the logs histogram or metrics charts to drill down both results. 

[Log collection](../../how-to/setup-log-collection.md) is  defined in the bottom part of that page.

> Note: Currently this configuration is shared accross all the clusters but we will provide a dedicated configuration (per cluster) soon.

!!! infomy 

    [![logs](/img/howto/logs.png)](/img/howto/logs.png)

The default setup will collect Cassandra system.log, axon-agent.log and axon-java-agent.log.
You can update the path of your cassandra system.log if it's located in a different folder by updating the **filename** field. The **newlineregex** is used by the log collector to handle multilines logs. Default **newlineregex** should be ok unless you've customized cassandra logs.

Once all is setup, you should see events from the agents and logs from the log files you've specified.

!!! infomy 

    [![logs](/img/dashboards/cassandra/dashboards.png)](/img/dashboards/cassandra/dashboards.png)

You can edit that configuration by clicking the wheel icon on the top right of the log view:

!!! infomy 

    [![logs](/img/howto/logs2.png)](/img/howto/logs2.png)

