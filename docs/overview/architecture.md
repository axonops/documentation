# Architecture

## Before
Our deployment model with the use of open source tools 

!!! infomy 

    [![digitalis.io_monitoring_before](/img/digitalis.io_stack.png)](/img/digitalis.io_stack.png)

## AxonOps Deployment Model
As you can see from the diagram below, we have massively simplified the stack with AxonOps.

!!! infomy 

    [![AxonOps_Deployment_Model](/img/AxonOps_Deployment_Model.png)](/img/AxonOps_Deployment_Model.png)


You can also use a **CQL** datastore such as **Cassandra**, **Elassandra**, or **Scylla** to store the metrics.
We recommand storing metrics on a CQL store on 100+ nodes clusters to improve your experience navigating the metrics dashboards.



