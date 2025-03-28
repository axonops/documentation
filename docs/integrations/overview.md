AxonOps provide various integrations for the notifications.

The functionality is accessible via ***Settings > Integrations***

The current integrations are:

* SMTP
* Pagerduty
* Slack
* Microsoft Teams
* ServiceNow
* OpsGennie
* Generic webhooks

!!! infomy 

![](2022-09-20-11-08-58.png)



###  Routing
AxonOps provide a rich routing mechanism for the notifications.

The current routing options are:

* Global - this will route all the notifications
* Metrics - notifications about the alerts on metrics
* Backups - notifications about the backups / restore
* Service Checks - notifications about the service checks / health checks
* Nodes - notifications raised from the nodes
* Commands - notifications from generic tasks
* Repairs - notifications from Cassandra repairs
* Rolling Restart - notification from the rolling restart feature

Each severity (`info, warning, error`) can be routed independently 

   ![](./routing.JPG)

### Errors per routing mechanism and severity levels

#### Backup

| **Source** | **Severity**   | **Description**                                                          |
| :--------- | :------------- | :----------------------------------------------------------------------- |
| Backup     | Critical	      | Any error that is returned from the 3rd party remote location providers. |
| Backup     | Warning	      | Clear local snapshots timed out                                          |
| Backup     | Warning	      | Unable to find local snapshot                                            |
| Backup     | Warning	      | Local backup process erros                                               |
| Backup     | Warning	      | Clear remote snapshot timed out                                          |
| Backup     | Warning	      | Remote backup process errors                                             |
| Backup     | Warning	      | Unable to find remote snapshot                                           |
| Backup     | Warning	      | Clear remote snapshot timed out                                          |
| Backup     | Warning	      | Backup not triggered (Backups paused)                                    |
| Backup     | Warning	      | Failed to create backup                                                  |
| Backup     | Warning	      | Failed to create remote config for backups                               |
| Backup     | Warning	      | Create cassandra snapshot failed                                         |
| Backup     | Warning	      | Snapshot request timed out                                               |
| Backup     | Warning	      | Cassandra node is inactive                                               |
| Backup     | Info	          | Local backup created successfully                                        |
| Backup     | Info	          | Backup deleted succesfully                                               |

#### Repair

| **Source** | **Severity**   | **Description**                                                          |
| :--------- | :------------- | :----------------------------------------------------------------------- |
| Repair     | Critical	      | Update repairs error, can be casued by tables being created or removed while a repair is running  |
| Repair     | Critical	      | Any error that is generated by Cassandra for a repair processes                                   |
| Repair     | Critical	      | Repair job is over 60% complete and the estimated time to completion is after gc_grace deadline   |
| Repair     | Warning	      | Repair job is over 40% complete and the estimated time to completion is after gc_grace deadline   |
| Repair     | Warning	      | Repair segment failed                                                                             |
| Repair     | Warning	      | Repair segment timed out                                                                          |
| Repair     | Warning	      | Cassandra repair error after n-amount of retries                                                  |
| Repair     | Warning	      | Repair unit errors                                                                                |
| Repair     | Warning	      | Repair errors for nonexistent correlation ID                                                      |
| Repair     | Warning	      | Repair request timed out after n-amount of attempts to connect to host                            |

