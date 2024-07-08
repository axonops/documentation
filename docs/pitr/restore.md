#### Requirements

- Make sure Cassandra service is stopped on every node in the Cluster/Data Center(DC)
- Make sure $COMMITLOG_DIR is empty and writable
- Check target table directories are empty and writable

#### Steps:

In the AxonOps Dashboard on the left hand menu navigate to Operations --> Restore

<img src="/pitr/pitr_left_restore.png" width="200">

On the top tab select Point-In-Time Recovery

<img src="/pitr/pitr_top_recovery.png" width="700">

You will be presented with the Point-In-Time recovery screen. There are several steps that need to be done to complete a Point-in-time restore. 

<br/>

#### Step 1: Select Restore Point-in-time.

<img src="/pitr/pitr_full.png" width="700">

Select the Point-In-Time you want to restore your cluster too. 

Please complete the Date/Time selection and fields of the keyspace and table/s that you would like to restore.

- **```Wide Time Range```**
    
    The wide time range is always a calendar month from the 1st to the last day of the selected month.

    To select a different month please use the ![](../previous.png){ .skip-lightbox width="15" } and ![](../next.png){ .skip-lightbox width="15" } arrows on either side of the slider.

    At the beginning and end of the Wide Time Range slider there is a black bar that you can slide left and right to narrow the Date/Time of when you want to restore to.

- **``` Zoomed Section```**

    This is a narrower view of the wide selection in the above slider.
    
    By default if the Wide Time Range slider is 30 days the Zoomed Section will be 30 days. 
    
    The narrower the time range in the Wide Time Range slider the more precise the available date/time selection will be in the Zoomed section.

    Example of what the Zoomed section will look like when snapshots are available to select for PITR.

    ![](../zoomed_section.png)
    ```
    The Camera Icon represents a snapshot at a point-in-time where a commitlog is archived.
    ```

- **```Point in time```**

    A text based representation of the selection made in the Zoomed section slider. This is an altenative if you want to manually input a specific time. 

- **```Keyspace(optional)```**

    The Application or System Keyspaces that were included as part of the commitlog archive process. If you don't specify a Keyspace all Keyspaces will be included in the restore process.

- **```Tables(optional)```**

    The Application or System Tables that were included as part of the commitlog archive process. If you don't specify a Table all Tables will be included in the restore process.

#### Step 2: Overview of Point-in-time nodes,keyspaces and tables.

<img src="/pitr/step_2_full.png" width="700">

Confirm by clicking show details that all the tables and keyspaces you want to restore will be part of the restoration. You will be presented with the following screen. 

<img src="/pitr/step_2_full_details.png" width="700">

- **```Tables```**

    Tables to be restored will be highlighted in Green, those to be excluded will be Greyed out. 
    The search box will allow you to search for and confirm specific tables or keyspaces will be restored.

- **```Commit Logs ```**

    The last timestamp and file name of the commit log that will be used to recover to the specified point-in-time.

- **```Snapshots```**

    The Snapshot/s that will be used to recover to the specified point-in-time

#### Step 3: Confirmation of Point-in-time restoration to proceed.

Confirm you are ready to start the Point-in-time recovery.

<img src="/pitr/step_3_full.png" width="700">

- Stop Cassandra on the nodes that need to be restored. 
- Delete the SStable files in the target table directories
- Delete commitlog files in the commitlog directory

#### Step 4: Final checks and last steps before Point-in-time recovery starts.

The Axon-Agent service confirm the Cassandra nodes are stopped.
Checks to ensure the clstuer is ready for the Point-in-time recovery.

<img src="/pitr/step_4_full.png" width="700">

Once you have clicked Check PITR Readiness a warning will be displayed. 
Click on show details button to view the tables affected and any errors/warnings.

<img src="/pitr/step_4_full_details.png" width="700">


#### Step 5: Start the Point-in-time recovery.

Start the recovery process

<img src="/pitr/step_5_full.png" width="700">

#### Step 6: Wait for completion and start Cassandra nodes.

The Status page of the Point-in-time restore process. 
Once the restore has been completed the status will remain in a progressing state until the Cassandra nodes are restarted.

<img src="/pitr/step_6_full.png" width="700">


#### Step 7: Check data in Cassandra has been recovered to specified Point-in-time.

Successful Point-in-time restore. 
Please confirm the details and data in the tables that have been restored are present as expected.

<img src="/pitr/step_7_full.png" width="700">













<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>

bottom please remove