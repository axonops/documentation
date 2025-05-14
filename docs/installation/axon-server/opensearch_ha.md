---
hide:
  - toc
---

# Opensearch Cross Cluster Replication Setup

Cross cluster replication allows you to index data to a leader index and then replicate that to a follower index. 

For more [Read Here](https://docs.opensearch.org/docs/latest/tuning-your-cluster/replication-plugin/getting-started/)

## Prerequisites

!!! warning "Please take note"
    Cross Cluster Replication needs to be setup before installing and starting Axon-Server

Cross-cluster replication has the following prerequisites:

- Both the leader and follower cluster must have the replication plugin installed.

- If you’ve overridden node.roles in opensearch.yml on the follower cluster, make sure it also includes the remote_cluster_client role:

`node.roles: [<other_roles>, remote_cluster_client]`

## Permissions
On both the Leader and the Follower cluster

- Make sure the Opensearch Security plugin is either enabled or disabled. 

If you disabled the Security plugin, you can skip the following section.

Ensure that non-admin users are mapped to the appropriate permissions so they can perform replication actions.

For index and cluster-level permission requirements, see [Cross-cluster replication permissions](https://docs.opensearch.org/docs/latest/tuning-your-cluster/replication-plugin/permissions/).


## Step 1 - Create Replication Role (If Security Enabled)

Opensearch has built-in roles that can be applied on both the leader and follower user.

- Create a user on both the Leader and Follower cluster. 
- Assign the role to the user on the Leader and Follower cluster.
  - cross_cluster_replication_leader_full_access
  - cross_cluster_replication_follower_full_access 

<img src="/installation/axon-server/CCR_Roles.png" />

## Step 2 - Create the connection with the leader

On the Follower cluster:

Update all the values in the Angle Brackets(**&lt;BRACKET&gt;**)

```shell
curl -XPUT -k -H 'Content-Type: application/json' -u '<CCR_USER>:<CCR_USER_PASSWORD>' 'https://<FOLLOWER_IP_ADDRESS>:<9200>/_cluster/settings?pretty' -d '
{
  "persistent": {
    "cluster": {
      "remote": {
        "<GIVE MY CONNECTION A NAME>": {
          "seeds": ["<LEADER_IP_ADDRESS>:<9300>"]
        }
      }
    }
  }
}'
```
 
!!! info "Transport Port 9300"
    Please take note that the port number needs to be the Transport port number for connecting the Follower Cluster to the Leader Cluster. **Default is 9300**. 
    If you have changed this value please update in the **seeds** section.

## Step 3 - Setup Auto Follower Replication Rule

On the Follower Cluster:

Please take note that the auto-follow pattern is setup with using wildcard(*) matching. This will pick up all the indexes that Axon-Server creates.

Update all the values in the Angle Brackets(**&lt;BRACKET&gt;**)

```shell
curl -XPOST -k -H 'Content-Type: application/json' -u '<CCR_USER>:<CCR_USER_PASSWORD>' 'https://<FOLLOWER_IP_ADDRESS>:<9200>/_plugins/_replication/_autofollow?pretty' -d '
{
   "leader_alias" : "<CONNECTION NAME FROM STEP 2>",
   "name": "<MY REPLICATION RULE NAME>",
   "pattern": "*", 
   "use_roles":{
      "leader_cluster_role": "cross_cluster_replication_leader_full_access",
      "follower_cluster_role": "cross_cluster_replication_follower_full_access"
   }
}'
```

!!! note "Roles"
    If you have Security disabled you can exclude the **use_roles** section.

## Step 4  - Start Axon-Server

On the Primary DC start axon-server. Once started axon-server will create the initial indices needed and the follower node will start replicating all the indices based on the auto-follow pattern setup in Step 3.
