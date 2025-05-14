---
hide:
  - toc
---

# Opensearch Cross Cluster Replication Failover

For Every Index on the Follower Cluster you will need to perform theses Steps 1 and 2.

## Step 1 - Stop Replication on the Follower Cluster.

Update all the values in the Angle Brackets(**&lt;BRACKET&gt;**)

```shell
curl -XPOST -k -H 'Content-Type: application/json' -u '<CCR_USER>:<CCR_USER_PASSWORD>' 'https://<FOLLOWER_IP_ADDRESS>:<9200>/_plugins/_replication/<follower-index>/_stop?pretty' -d '{}'
```

## Step 2 - Confirm Replication is stopped in the Follower Cluster

Update all the values in the Angle Brackets(**&lt;BRACKET&gt;**)

```shell
curl -XGET -k -u '<CCR_USER>:<CCR_USER_PASSWORD>' 'https://<FOLLOWER_IP_ADDRESS>:<9200>/_plugins/_replication/<follower-index>/_status?pretty'
```

## Step 3 - Delete Auto Follow Replication Rule

Once all the indices have stopped following, you can delete the auto follow rule and the follower cluster will become the leader cluster.

Update all the values in the Angle Brackets(**&lt;BRACKET&gt;**)

```shell
curl -XDELETE -k -H 'Content-Type: application/json' -u '<CCR_USER>:<CCR_USER_PASSWORD>' 'https://<FOLLOWER_IP_ADDRESS>:<9200>/_plugins/_replication/_autofollow?pretty' -d '
{
   "leader_alias" : "<CONNECTION NAME FROM SETUP STEP 2>",
   "name": "<REPLICATION RULE NAME FROM SETUP STEP 3>"
}'
```

## Step 4 - Switchover Axon-Server config to connect to Follower Cluster

## Step 5 - Setup previous Leader Cluster as Follower Cluster.

Once the above steps have been completed the indices on the Existing Follower cluster will change from read-only to read-write. 

The current Follower cluster will become the new Leader cluster.

Please follow the steps above and setup the Previous Leader cluster as a new Follower cluster.
