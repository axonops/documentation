# Configuring SAML Roles for Azure Entra ID

AxonOps supports role-based access control through SAML assertions. This guide explains how to configure Azure Entra ID to pass role information to AxonOps.

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

## Option 1: Using Azure App Roles (Recommended)

### 1. Create App Roles

1. In your Enterprise Application, go to **App registrations** in Azure Entra ID
2. Find and click on your application registration
3. In the left navigation, click **App roles**
4. Click **Create app role** for each role you want to create

For each role, configure:
- **Display name**: e.g., "AxonOps Super Admin"
- **Allowed member types**: Users/Groups (or both)
- **Value**: The role name that will be sent to AxonOps (e.g., `superAdmin`)
- **Description**: A description of what this role provides

Example app roles to create:

| Display Name | Value | Description |
|--------------|-------|-------------|
| AxonOps Super Admin | superAdmin | Full access to all AxonOps features |
| AxonOps Admin | admin | Administrative access to AxonOps |
| AxonOps DBA | dba | Database administrator access |
| AxonOps Read Only | readonly | Read-only access to monitoring |
| AxonOps Billing | billing | Access to billing information |

### 2. Configure Claims to Include Roles

1. Go back to your Enterprise Application
2. Navigate to **Single sign-on**
3. Click **Edit** in the User Attributes & Claims section
4. Add a new claim:
   - **Name**: `axonops-roles`
   - **Source**: Attribute
   - **Source attribute**: `user.assignedroles`

### 3. Assign Roles to Users

1. In the Enterprise Application, go to **Users and groups**
2. Select a user or group
3. Click **Edit assignment**
4. Select the appropriate role from the dropdown
5. Click **Assign**

## Option 2: Using Groups

If you prefer to use Azure AD groups for role management:

### 1. Create Groups

Create Azure AD groups that correspond to AxonOps roles:
- `axonops-superadmin`
- `axonops-admin`
- `axonops-dba`
- `axonops-readonly`
- `axonops-billing`

For cluster-specific access, create groups like:
- `axonops-prod-cassandra-admin`
- `axonops-staging-kafka-readonly`

### 2. Configure Group Claims

1. In Single sign-on settings, edit User Attributes & Claims
2. Add a new claim:
   - **Name**: `axonops-roles`
   - **Source**: Attribute
   - **Source attribute**: Select "Groups" and configure to return group names

### 3. Configure AxonOps Role Mapping

When using groups, you'll need to map the group names to AxonOps roles in the AxonOps SAML configuration.

## Multiple Roles

Users can have multiple roles in AxonOps. When using app roles, Azure will send all assigned roles. When using groups, all group memberships will be included.

## Testing Role Assignment

1. Assign a test user to your application with a specific role
2. Complete the SAML configuration in AxonOps
3. Have the test user log in via SAML
4. Verify they have the expected permissions in AxonOps

## Troubleshooting

### Roles Not Appearing
- Ensure the claim name is exactly `axonops-roles`
- Check that users are properly assigned to roles/groups
- Verify the SAML response includes the role information

### Invalid Role Format
- Global roles must match exactly: `superAdmin`, `admin`, `dba`, `readonly`, `billing`
- Cluster-specific roles must follow the format: `orgname/clustertype/clustername/role`

## Next Steps

After configuring roles, proceed to [Configure SAML in AxonOps Cloud](03-axonops-saml-azure.md) to complete the integration.