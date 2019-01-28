## Ovewview

When monitoring Cassandra there are 


Apache Cassandra is a highly scalable open source distributed database management system written in Java.  However, many aspects of Cassandra performance, consistency, and availability depend on the capabilities of the underlying Java runtime platform. The Java garbage collection process freezes the application while memory is defragmented and compacted, resulting in arbitrary Cassandra pauses that lead to response time inconsistency, increased time to data consistency, and can even trigger serious conditions like cascading node failures, where multiple stalled Cassandra nodes trigger cluster-level outages and crashes. 


> Noticed:  To be able to view your healthcheck services you must  [setup][0].

## AxonDash HealthChecks

On the Axonops application menu, click `Healthchecks`, a list of all your **Nodes** will appear

 

[0]: /monitoring/healthchecks/configurations/




!!! infomy 

    [![healthchecks_overview](/img/healthchecks_overview.png)](/img/healthchecks_overview.png)

### Healthchecks

####  By Node

To view all the `services` for eah **Node** select `Nodes` tab and `click` on `node's name`to expand the node service's.

!!! infomy 

    [![healthchecks_by_node](/img/healthchecks_by_node.png)](/img/healthchecks_by_node.png)


the services will apprear with `status`:

##### Ok Status

> Status: **OK** the service has been passed.

!!! infomy 

    [![status_ok](/img/status_ok.png)](/img/status_ok.png)

##### Error Status

> Status: **Error** the service has been failed and the reason will appear.
        
!!! infomy 
        
    [![status_error](/img/status_error.png)](/img/status_error.png)

#### By Service

To view all the `Nodes` for eah **Service** select `Services` tab and `click` on `service  name`to expand it.

!!! infomy 

    [![healthchecks_by_service](/img/healthchecks_by_service.png)](/img/healthchecks_by_service.png)

##### Ok Status

 > Status: **OK** the `service ` has been completed successfully for the `Node`.
    
!!! infomy 
    
        [![node_completed](/img/node_completed.png)](/img/node_completed.png)
    
##### Error Status
    
> Status: **Error** the `service` has been failed for the `Node` and the reason will appear.
            
!!! infomy 
    
    [![node_failed](/img/node_failed.png)](/img/node_failed.png)