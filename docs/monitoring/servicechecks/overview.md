## Overview

Service Checks in AxonOps allows you to configure custom checks using three types of check invocations:

1. Shell Script
2. HTTP endpoint check
3. TCP endpoint check

These checks are configured on the server side in the GUI, but pushed down dynamically to the agents and executed on the agents. There is no need to deploy the check scripts to individual servers like you may do with Nagios.

Any changes made and saved are automatically pushed down to the agents.


> Notice: To be able to view your service checks you must [setup][0].

## AxonDash Service Checks

On the Axonops application menu, click `Service Checks`, a list of all your **Nodes** will appear

 

[0]: /monitoring/servicechecks/configurations/




!!! infomy 

    [![servicechecks_overview](/img/servicechecks_overview.png)](/img/servicehecks_overview.png)

### Service Checks
There are 2 dimensional views to the service health status - by node or by service.

####  By Node

To view all the `services` for eah **Node** select `Nodes` tab and `click` on `node's name`to expand the node service's.

!!! infomy 

    [![servicechecks_by_node](/img/servicechecks_by_node.png)](/img/servicechecks_by_node.png)


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

To view all the `Nodes` for eah **Service** select `Services` tab and `click` on `service name`to expand it.

!!! infomy 

    [![servicechecks_by_service](/img/servicechecks_by_service.png)](/img/servicechecks_by_service.png)

##### Ok Status

 > Status: **OK** the `service` has been completed successfully for the `Node`.
    
!!! infomy 
    
        [![node_completed](/img/node_completed.png)](/img/node_completed.png)
    
##### Error Status
    
> Status: **Error** the `service` has been failed for the `Node` and the reason will appear.
            
!!! infomy 
    
    [![node_failed](/img/node_failed.png)](/img/node_failed.png)