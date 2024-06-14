# Architecture

## Before
Our deployment model with the use of open source tools 

!!! infomy 

    [![axonops_ltd_monitoring_before](/img/axonops_ltd_stack.png)](/img/axonops_ltd_stack.png)

## AxonOps Deployment Model
As you can see from the diagram below, we have massively simplified the stack with AxonOps.

!!! infomy 

    [![AxonOps_Deployment_Model](/img/AxonOps_Deployment_Model.png)](/img/AxonOps_Deployment_Model.png)


You can also use a **CQL** datastore such as **Cassandra**, **Elassandra**, or **Scylla** to store the metrics.
We recommend storing metrics on a CQL store on 100+ nodes clusters to improve your experience navigating the metrics dashboards.



