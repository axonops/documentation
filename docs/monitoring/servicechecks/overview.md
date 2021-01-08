Service Checks in AxonOps allows you to configure custom checks using three types of checks:

1. Shell Scripts
2. HTTP endpoint checks
3. TCP endpoint checks


The functionality is accessible via ***Service Checks*** menu

You can list the service checks by **node**:
![](./0.JPG)

Or by **services**:
![](./1.JPG)

You can click on a row to view all the `services` for a given **Node**.

!!! infomy 
![](./3.JPG)

the services will apprear with `status`:

##### Ok Status

> Status: **OK** the service has been passed.

!!! infomy 

    [![status_ok](/img/status_ok.png)](/img/status_ok.png)

##### Error Status

> Status: **Error** the service has been failed and the reason will appear.
        
!!! infomy 
        
    [![status_error](/img/status_error.png)](/img/status_error.png)



These checks are configured on the server side in the GUI and pushed down dynamically to the agents for execution. There is no need to deploy the check scripts to individual servers like you may do for instance with Nagios.

To setup the checks, go to  ***Settings > Service Checks*** and click on one of the `+` buttons

![](./2.JPG)
> Any changes made and saved are automatically pushed down to the agents. The status will show once the check has been executed on the agent so it might take some time depending on the interval you have specified within the Service Checks. Although the first execution of the checks will be spread across 30 seconds to prevent running all the checks at the same time.




> Notice: To be able to view your service checks you must [setup][0].



In the left-hand AxonOps application menu, click `Service Checks`, a list of all your **Nodes** will appear


[0]: /monitoring/servicechecks/configurations/


!!! infomy 

    [![servicechecks_overview](/img/servicechecks_overview.png)](/img/servicehecks_overview.png)




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