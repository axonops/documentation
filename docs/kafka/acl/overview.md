---
title: "Topic Access Control List (ACL)"
description: "Kafka ACL management in AxonOps. Overview of access control list features."
meta:
  - name: keywords
    content: "Kafka ACL overview, access control, AxonOps Kafka"
search:
  boost: 8
---

# Topic Access Control List (ACL)

## What is an Access Control List

Kafka Access Control Lists (ACLs) are a core part of Kafka’s security, defining which authenticated users or applications (principals) can perform specific operations on Kafka resources such as topics, consumer groups, or the cluster itself.

### How Kafka ACLs Work

#### Authorization Framework:

Kafka uses a pluggable authorization framework, enabled by setting the `authorizer.class.name` property in the broker configuration.

- AclAuthorizer is used for ZooKeeper-based clusters (stores ACLs in ZooKeeper).
- StandardAuthorizer is used for KRaft-based clusters (stores ACLs in Kafka metadata).

#### Authentication Prerequisite:

Before ACLs can be enforced, clients must be authenticated (commonly using SASL mechanisms). The authenticated identity is the principal referenced in ACLs

### ACL Structure and Components

- Principal (the user/application)
- Operation (e.g., READ, WRITE)
- Resource type (topic, group, cluster, delegation_token or transactional_id)
- Permission type (ALLOW or DENY)
- Host (the IP address or hostname)

#### Principal

The user or service account identity. 

Format examples:

`User:alice`

`User:admin`

`Group:devs`

#### Operations

Define which users or services (principals) can perform specific operations.

##### Common Kafka ACL Operation

| Operation |	Description |	Typical Resource(s) |
| -------- | -------------------------------- | -------- |
| READ |	Consume messages from a topic, or read from a consumer group |	Topic, Group |
| WRITE |	Produce (write) messages to a topic |	Topic |
| CREATE |	Create a new topic or consumer group |	Topic, Group, Cluster |
| DELETE |	Delete a topic or consumer group |	Topic, Group |
| ALTER |	Change configuration of a topic, group, or cluster | Topic, Group, Cluster |
| ALTER_CONFIGS |	Change resource configuration (more granular than ALTER) | Topic, Cluster |
| DESCRIBE | View metadata of a resource (e.g., see topic or group details) | Topic, Group, Cluster |
| DESCRIBE_CONFIGS |	View resource configuration |	Topic, Cluster |
| CLUSTER_ACTION | Perform internal cluster operations (e.g., leader election, replication) |	Cluster |
| ALL	All | possible operations (admin-level permission) | Any |
| IDEMPOTENT_WRITE |	Allow idempotent producer operations| Cluster |

##### Transactional and Delegation Token Operations

| Operation |	Description |	Typical Resource(s) |
| -------- | -------------------------------- | -------- |
| WRITE |	Initiate and commit/abort transactions |	TransactionalId |
| DESCRIBE |	View transactional state or delegation token details |	TransactionalId, DelegationToken |

#### Resource Types

The type of Kafka resource to which the ACL applies:

- Topic : 

    Represents a Kafka topic, which is where messages are published and consumed.

- Group : 

    Refers to a consumer group, which is used for coordinating message consumption among multiple consumers.

- Cluster : 

    The entire Kafka cluster as a resource. Used for operations that affect the whole cluster.

- Transactional ID : 
  
    Identifies a transactional producer instance, enabling exactly-once semantics (EOS).

- Delegation Token : 

    Represents a token used for authentication between brokers and clients, often as part of SASL authentication.


#### Permission Type

- ALLOW:

    Grants the specified operation(s) to the principal on the resource. If an ACL with ALLOW is present and matches the request, the operation is permitted.

- DENY:

    Explicitly forbids the specified operation(s) to the principal on the resource. If an ACL with DENY matches, the operation is blocked—even if another ALLOW rule would also match.

#### Host

- Host Limiting:

    By specifying a host in an ACL, you restrict the permission so it only applies when the user connects from that host.

    e.g. setting the host as `192.168.1.100`, will only allow or deny connections originating from that IP to perform the specific operation on the topic.

- Wildcard Host:

    Using `*` means the permission applies from any host (no restriction).

### Best Practices

- Principals: Use a separate principal for each application or service. This limits the blast radius of a compromise and aids auditing.
- Least Privilege: Grant only the permissions required for each principal - no more.
- Host Restrictions: Use the host option to restrict access to trusted network locations or hosts.
- Wildcard ACLs: Use with caution, typically only for admin users