
**Cluster Overview** is the home page and provides an overview of your cluster health, including **OS**, **Cassandra** and **JVM**.

The information is automatically extracted by the AxonOps agent and it is pushed to AxonOps server. There is no need to configure anything on the agent or the server side for this information to be populated in the Cluster Overview dashboard.


## Viewing cluster overview

On the Axonops application menu, select `Cluster Overview`.

!!! infomy

    [![cluster_overview](/img/cluster_overview.png)](/img/cluster_overview.png) 

`click` on **DC** (data centre) to view the information for **OS**, **Cassandra**, **JVM** .

 
> a pop-up menu will appear with all the details.

!!! infomy

    [![cluster_details](/img/cluster_details.png)](/img/cluster_details.png) 


### OS Details
Operating System Details section shows general information including:

* General Information
* CPU
* Memory
* Swap
* Disk volumes

!!! infomy

    [![os_details](/img/os_details.png)](/img/os_details.png) 


### Cassandra Details
Cassandra Details view shows the details from cassandra.yaml loaded into Cassandra. There is a search field available near the top to filter the parameters.

!!! infomy

    [![cassandra_details](/img/cassandra_details.png)](/img/cassandra_details.png)

### JVM Details
JVM Details section shows the general information about the JVM, including the version and some configurations such as the heap and Garbage Collection settings.
!!! infomy

    [![jvm_details](/img/jvm_details.png)](/img/jvm_details.png)