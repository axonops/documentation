Repairs must be completed regularly to maintain Cassandra nodes.

AxonOps provides two mechanisms to ease management of repairs in Cassandra:

* Adaptive Repair Service
* Scheduled Repairs

## Adaptive Repair Service

Since AxonOps collects performance metrics and logs, we built an "Adaptive" repair system which regulates the velocity (parallelism and pauses between each subrange repair) based on performance trending data. The regulation of repair velocity takes input from various metrics including CPU utilization, query latencies, Cassandra thread pools pending statistics, and IOwait percentage, while tracking the repair schedule based on `gc_grace_seconds` for each table.

The idea of this is to achieve the following:

* Completion of repair within `gc_grace_seconds` of each table.
* Repair process does not affect query performance.
* In essence, the adaptive repair regulator slows down the repair velocity when it detects an increase in load and speeds up to catch up with the repair schedule when resources are more readily available.
* This mechanism does not require JMX access. The adaptive repair service running on AxonOps server orchestrates and issues commands to the agents over the existing connection.

!!! infomy 

    [![adaptive_repair](../../img/cass_repairs/adaptive_repair.png)](../../img/cass_repairs/adaptive_repair.png)

From a user’s point of view there is only a single switch to enable this service. Keep this enabled and AxonOps will take care of the repair of all tables for you.

You can, however, customize the following:

* Blacklist select tables.
* Specify the number of tables to repair in parallel.
* Specify the number of segments per VNode to repair.
* The GC grace threshold in seconds.
    * If a table has a gc grace lesser than the specified value, the table will be ignored by the adaptive repair service.

### Increasing Data Consistency

To keep tables as up-to-date as possible we recommend both:

* Increasing the `table parallelism` to be greater than the total number of tables in the cluster.
* Reducing the `segments per VNode` to generate fewer repair requests.

## Scheduled Repairs

You can initiate three types of scheduled repairs with AxonOps.

!!! infomy 

    [![scheduled_repair](../../img/cass_repairs/scheduled_repair4.png)](../../img/cass_repairs/scheduled_repair4.png)

The above screenshot showcases a running repair that has been initiated immediately and a scheduled repair that is scheduled for 12:00 AM UTC.

### Immediate Repairs

These will trigger immediately **once**.

!!! infomy 

    [![scheduled_repair](../../img/cass_repairs/scheduled_repair.png)](../../img/cass_repairs/scheduled_repair.png)


### Simple Scheduled Repairs

These will trigger based on the selected schedule **repeatedly**.

!!! infomy 

    [![scheduled_repair](../../img/cass_repairs/scheduled_repair2.png)](../../img/cass_repairs/scheduled_repair2.png)

### Cron Scheduled Repairs

Same as **Simple Scheduled Repairs** but the schedule will be based on a Cron expression.

!!! infomy 

    [![scheduled_repair](../../img/cass_repairs/scheduled_repair3.png)](../../img/cass_repairs/scheduled_repair3.png)
