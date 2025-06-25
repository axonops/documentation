# Configuring SAML Roles for JumpCloud

AxonOps uses JumpCloud custom attributes to manage role-based access control. This guide explains how to create groups and configure custom attributes for AxonOps roles.

## Understanding AxonOps Roles

### Global Roles
AxonOps supports the following global roles:
- `superAdmin` - Full access to all features and clusters
- `admin` - Administrative access
- `dba` - Database administrator access
- `readonly` - Read-only access to monitoring and metrics
- `billing` - Access to billing and cost information

### Cluster-Specific Roles
For granular access control, you can assign roles to specific clusters using the format:
```
orgname/clustertype/clustername/role
```

For example:
- `myorg/cassandra/production/admin`
- `myorg/kafka/staging/readonly`

## JumpCloud Role Management Strategy

JumpCloud uses custom attributes at the group level to manage roles. Users inherit these attributes when they're members of groups.

## Creating Groups for Role Management

### 1. Navigate to User Groups

In the JumpCloud Admin Console:
1. Go to **User Management** → **User Groups**
2. Click **+** to create a new group

### 2. Create Groups for Each Role

Create groups that represent different access levels:

| Group Name | Description | Purpose |
|------------|-------------|---------|
| AxonOps-SuperAdmins | AxonOps Super Administrators | Full system access |
| AxonOps-Admins | AxonOps Administrators | Administrative access |
| AxonOps-DBAs | AxonOps Database Administrators | DBA access |
| AxonOps-ReadOnly | AxonOps Read-Only Users | Monitoring access |
| AxonOps-Billing | AxonOps Billing Users | Billing access |

For each group:
1. Enter the group name
2. Add a description
3. Click **save**

### 3. Add Custom Attributes to Groups

For each group created above:

1. Click on the group to open its details
2. Navigate to the **Details** tab
3. Scroll to **Custom Attributes**
4. Click **add attribute**
5. Configure:
   - **Attribute Name**: `axonops-roles`
   - **Attribute Value**: The corresponding role value

| Group | Attribute Value |
|-------|----------------|
| AxonOps-SuperAdmins | `superAdmin` |
| AxonOps-Admins | `admin` |
| AxonOps-DBAs | `dba` |
| AxonOps-ReadOnly | `readonly` |
| AxonOps-Billing | `billing` |

### 4. Assign Application to Groups

For each group:
1. Navigate to the **Applications** tab
2. Click **+** to add an application
3. Search for and select your AxonOps SAML application
4. Click **save**

## Creating Groups for Cluster-Specific Access

### 1. Determine Cluster-Specific Roles

For granular access to specific clusters, create groups with cluster-specific role values.

Example groups:
| Group Name | Custom Attribute Value | Access Level |
|------------|----------------------|--------------|
| AxonOps-Prod-Cassandra-Admins | `acme/cassandra/production/admin` | Admin access to production Cassandra |
| AxonOps-Staging-Kafka-ReadOnly | `acme/kafka/staging/readonly` | Read-only access to staging Kafka |
| AxonOps-Dev-Cassandra-DBAs | `acme/cassandra/development/dba` | DBA access to development Cassandra |

### 2. Configure Cluster-Specific Groups

1. Create the group with a descriptive name
2. Add the custom attribute:
   - **Attribute Name**: `axonops-roles`
   - **Attribute Value**: The full cluster path (e.g., `acme/cassandra/production/admin`)
3. Assign the AxonOps SAML application to the group

## Assigning Users to Groups

### 1. Add Users to Groups

1. Navigate to **User Management** → **Users**
2. Click on a user to open their profile
3. Go to the **User Groups** tab
4. Click **+** to add groups
5. Select the appropriate AxonOps groups
6. Click **save**

### 2. Multiple Roles

Users can be members of multiple groups to have multiple roles in AxonOps:
- A user in both `AxonOps-ReadOnly` and `AxonOps-Prod-Cassandra-Admins` would have:
  - Global read-only access
  - Admin access to the production Cassandra cluster

### 3. Role Precedence

When users have multiple roles:
- More specific roles (cluster-specific) take precedence over global roles for those clusters
- Global roles apply to all resources not covered by specific roles

## Advanced Configuration

### Using Multiple Attribute Values

JumpCloud allows comma-separated values in custom attributes. You can assign multiple roles in a single group:

1. Create a group (e.g., "AxonOps-MultiRole")
2. Set the custom attribute:
   - **Attribute Name**: `axonops-roles`
   - **Attribute Value**: `readonly,acme/cassandra/production/admin,acme/kafka/staging/dba`

### Dynamic Group Assignment

Use JumpCloud's automated group membership rules to dynamically assign users based on:
- Department
- Location
- Manager
- Other user attributes

## Best Practices

### Group Naming Conventions

1. Use clear, consistent prefixes (e.g., "AxonOps-")
2. Include the access level in the name
3. For cluster-specific groups, include the cluster identifier

### Documentation

1. Document each group's purpose in the description
2. Maintain a mapping of groups to AxonOps access levels
3. Regular audit of group memberships

### Security

1. Follow the principle of least privilege
2. Regularly review group memberships
3. Remove users from groups when access is no longer needed
4. Use cluster-specific roles instead of global roles where possible

## Testing Role Assignment

### 1. Verify Attribute Configuration

1. In JumpCloud, navigate to a test user's profile
2. Check the **Details** tab
3. Verify that `axonops-roles` appears with the expected value(s)

### 2. Test SAML Assertion

1. Use JumpCloud's SAML assertion preview (if available)
2. Verify the `axonops-roles` attribute is included
3. Check that the values match your configuration

## Troubleshooting

### Attributes Not Appearing

1. Ensure the custom attribute is named exactly `axonops-roles`
2. Verify the user is in a group with the attribute configured
3. Check that the group is assigned to the AxonOps application

### Role Not Working in AxonOps

1. Verify the role value matches AxonOps expectations exactly
2. For cluster-specific roles, ensure the format is correct: `org/type/cluster/role`
3. Check for typos in role names (they are case-sensitive)

## Next Steps

After configuring groups and assigning users, proceed to [Configure SAML in AxonOps Cloud](03-axonops-saml-jumpcloud.md) to complete the integration.