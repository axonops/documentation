# Topic Access Control List (ACL).

## Create an Access Control List (ACL).

### Click ACLs in the Left Navigation.

<img src="/kafka/acl/acl_click.png" width="700">

### Click Create ACL Button.

<img src="/kafka/acl/acl_create_button.png" width="700">

## On the ACL Create screen complete the following fields:

<img src="/kafka/acl/acl_create.png">

### Select the ACL Resource Type.

The Kafka resource (e.g., topic, group, cluster)

<img src="/kafka/acl/acl_resource_type.png">

### Select the Topic to apply the ACL too.

<img src="/kafka/acl/acl_topic.png">

### Edit the Host that will have access to the Topic.

Host Limiting:

By specifying a host in an ACL, you restrict the permission so it only applies when the user connects from that host.

e.g. setting the host as `192.168.1.100`, will only allow or deny connections originating from that IP to perform the specific operation on the topic.

Wildcard Host:

Using `*` means the permission applies from any host (no restriction).

<img src="/kafka/acl/acl_host.png" width="700">

### Select Principal User or Group and Principal Value

The user or application (e.g., User:alice, User:app1, Group:developers)

<img src="/kafka/acl/acl_principal.png">

<img src="/kafka/acl/acl_principal_value.png">

### Select the Operation of the ACL.

The action (READ, WRITE, CREATE, DELETE, DESCRIBE etc.)

If you toggle the Operation switch it will choose between 

#### Allow 

<img src="/kafka/acl/acl_allow.png" width="700">

#### Deny
<img src="/kafka/acl/acl_deny.png" width="700">