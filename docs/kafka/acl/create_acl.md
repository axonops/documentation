---
title: "Topic Access Control List (ACL)"
description: "Create Kafka ACLs with AxonOps. Set up access control for topics and groups."
meta:
  - name: keywords
    content: "create Kafka ACL, access control, permissions"
---

# Topic Access Control List (ACL)

## Create an Access Control List (ACL)

### Click ACLs in the left navigation

<img src="../acl_click.png" width="700" alt="ACLs navigation item">

### Click Create ACL Button

<img src="../acl_create_button.png" width="700" alt="Create ACL button">

### On the ACL Create screen complete the following fields

<img src="../acl_create.png" alt="Create ACL form">

### Select the ACL Resource Type

<img src="../acl_resource_type.png" alt="ACL resource type selector">

### Select the Topic to apply the ACL to

<img src="../acl_topic.png" alt="Topic selection for ACL">

### Edit the Host that will have access to the Topic

<img src="../acl_host.png" width="700" alt="Host configuration for ACL">

### Select Principal and Principal Value

The user or application (e.g., `User:alice`, `User:app1`).

<img src="../acl_principal.png" alt="Principal field">

<img src="../acl_principal_value.png" alt="Principal value field">

### Select the Operation of the ACL

If you toggle the Operation switch it will flip between Allow and Deny.

#### Allow

<img src="../acl_allow.png" width="700" alt="Allow ACL example">

#### Deny
<img src="../acl_deny.png" width="700" alt="Deny ACL example">
