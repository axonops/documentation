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
- Resource (topic/group)
- Permission type (ALLOW or DENY)
- Host (the IP address or hostname)

### Best Practices

- Principals: Use a separate principal for each application or service. This limits the blast radius of a compromise and aids auditing.
- Least Privilege: Grant only the permissions required for each principal - no more.
- Host Restrictions: Use the host option to restrict access to trusted network locations or hosts.
- Wildcard ACLs: Use with caution, typically only for admin users