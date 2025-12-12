# Configuring SAML Roles for Okta

AxonOps uses Okta groups to manage role-based access control. This guide explains how to create and configure groups in Okta for AxonOps roles.

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

## Important: Okta Group Naming Convention

**All groups used for AxonOps roles MUST start with the prefix `axonops-`**

This prefix is required for the group filter configured in the SAML application to work correctly.

## Creating Groups for Global Roles

### 1. Navigate to Groups

In the Okta Admin Console:
1. Go to **Directory** → **Groups**
2. Click **Add Group**

### 2. Create Groups for Each Role

Create the following groups:

| Group Name | Description | AxonOps Role |
|------------|-------------|--------------|
| axonops-superadmin | AxonOps Super Administrators | superAdmin |
| axonops-admin | AxonOps Administrators | admin |
| axonops-dba | AxonOps Database Administrators | dba |
| axonops-readonly | AxonOps Read-Only Users | readonly |
| axonops-billing | AxonOps Billing Access | billing |

For each group:
1. Enter the group name exactly as shown
2. Add a description
3. Click **Save**

### 3. Map Groups to AxonOps Roles

When these groups are sent via SAML, AxonOps will extract the role name after the "axonops-" prefix. For example:
- `axonops-superadmin` → `superAdmin` role in AxonOps
- `axonops-readonly` → `readonly` role in AxonOps

## Creating Groups for Cluster-Specific Roles

For granular access to specific clusters:

### 1. Determine the Cluster Path

The cluster path format is: `orgname/clustertype/clustername/role`

For example, if you have:
- Organization: `acme`
- Cluster type: `cassandra`
- Cluster name: `production`
- Role: `admin`

The full role would be: `acme/cassandra/production/admin`

### 2. Create the Group

The group name should be: `axonops-{cluster-path-with-dashes}`

Replace forward slashes with dashes. For the example above:
- Group name: `axonops-acme-cassandra-production-admin`

### 3. Examples of Cluster-Specific Groups

| Group Name | Mapped Role | Access |
|------------|-------------|---------|
| axonops-acme-cassandra-prod-admin | acme/cassandra/prod/admin | Admin access to prod Cassandra cluster |
| axonops-acme-kafka-staging-readonly | acme/kafka/staging/readonly | Read-only access to staging Kafka cluster |
| axonops-acme-cassandra-dev-dba | acme/cassandra/dev/dba | DBA access to dev Cassandra cluster |

## Assigning Users to Groups

### 1. Add Users to Groups

1. Navigate to **Directory** → **Groups**
2. Click on the group you want to manage
3. Click **Assign people**
4. Search for and select users
5. Click **Save**

### 2. Multiple Roles

Users can be members of multiple groups to have multiple roles in AxonOps. For example, a user could be in:
- `axonops-readonly` (global read-only access)
- `axonops-acme-cassandra-prod-admin` (admin access to production cluster)

## Testing Role Assignment

### 1. Verify Group Membership

1. Go to **Directory** → **People**
2. Click on a test user
3. Check the **Groups** tab to verify membership

### 2. Check SAML Assertion

After configuring SAML in AxonOps:
1. Have the test user log in
2. In AxonOps, verify they have the expected permissions
3. Check that the roles match the groups they're assigned to

## Best Practices

### Group Organization

1. Use clear, descriptive group names
2. Document the purpose of each group
3. Regularly audit group membership
4. Consider using group rules for automatic assignment

### Security Considerations

1. Follow the principle of least privilege
2. Regularly review and remove unnecessary access
3. Use cluster-specific roles instead of global roles where possible
4. Implement approval workflows for sensitive group additions

## Troubleshooting

### Groups Not Appearing in SAML

1. Ensure all groups start with `axonops-` prefix
2. Verify the group attribute statement in the SAML app is configured correctly
3. Check that users are assigned to both the application and the groups

### Role Mapping Issues

1. Verify the group name follows the correct format
2. For cluster-specific roles, ensure the path uses dashes instead of slashes
3. Check that the role names match AxonOps expectations exactly

## Next Steps

After configuring groups and assigning users, proceed to [Configure SAML in AxonOps Cloud](03-axonops-saml-okta.md) to complete the integration.