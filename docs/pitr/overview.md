# Point in Time Recovery

The aim of the AxonOps Cassandra Commitlog Archiving(PITR) feature is to provide an easy to use graphical user interface instead of users having to configure it manually on every Cassandra node in a cluster. 

#### Features
- UI to configure Commitlog archiving per Data Center(DC) in your cluster.
- Local or Remote Storage locations to store your commitlog archives.
- Retention periods for storing and retrieving your commitlog archives.
- UI that uses backups and commitlogs to specify the Point-in-Time to restore your cluster state too. 
- UI for current commitlog archiving status / statistics


#### Assumptions

- Native Cassandra installation:
    Axon-agent has write access to Cassandra conf directory

- Docker Cassandra installation:
    Axon-agent has the ability to start/stop Cassandra containers


#### Commit logs are archived in three different ways: 

- At Cassandra node startup 
- When a commit log is written to disk 
- At a specified point-in-time or when a backup is taken. 


#### The Point-in-Time recovery (PITR) feature is implemented in Cassandra as “Commitlog Archiving”.

Depending on the installation method used for Cassandra, in either ```$CASSANDRA_HOME/conf/```(tarball) or ```/etc/cassandra/```(package) there is a file called ```commitlog-archiving.properties```. 

To enable Commitlog Archiving(PITR) in Cassandra, some properties need to be set in the configuration file for every Cassandra node.

- **archive_command**

    One command can be inserted with %path and %name arguments. %path is the fully qualified path of the commitlog segment to archive. %name is the filename of the commitlog. STDOUT, STDIN, or multiple commands cannot be executed. If multiple commands are required, add a pointer to a script in this option.

    ```Example: archive_command=/bin/ln %path /backup/%name```

    ```Default value: blank```

- **restore_command**
    
    One command can be inserted with %from and %to arguments. %from is the fully qualified path to an archived commitlog segment using the specified restore directories. %to defines the directory to the live commitlog location.

    ```Example: restore_command=/bin/cp -f %from %to```

    ```Default value: blank```

- **restore_directories**
    
    Defines the directory to scan the recovery files into.

    ```Example: restore_directories=/path/to/restore_dir_location```

    ```Default value: blank```

- **restore_point_in_time**
    
    Restore mutations created up to and including this timestamp in GMT in the format yyyy:MM:dd HH:mm:ss. Recovery will continue through the segment when the first client-supplied timestamp greater than this time is encountered, but only mutations less than or equal to this timestamp will be applied.

    ```Example: restore_point_in_time=2020:04:31 20:43:12```

    ```Default value: blank```

- **precision**

    Precision of the timestamp used in the inserts. Choice is generally MILLISECONDS or MICROSECONDS

    ```Example: precision=MICROSECONDS```

    ```Default value: MICROSECONDS```
