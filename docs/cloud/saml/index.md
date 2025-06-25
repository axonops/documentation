# SAML Authentication for AxonOps Cloud

AxonOps Cloud supports SAML 2.0 authentication, allowing you to use your organization's identity provider for single sign-on (SSO). This provides centralized user management, enhanced security, and seamless access control.

## Supported Identity Providers

We provide detailed configuration guides for the following identity providers:

- [Azure Entra ID (Azure Active Directory)](azure-entra/index.md)
- [Okta](okta/index.md)
- [JumpCloud](../../authentication/jumpcloud-axonops-cloud/index.md)

Other SAML 2.0 compliant identity providers may also work with AxonOps Cloud. Contact support for assistance with additional providers.

## Benefits of SAML Authentication

### Enhanced Security
- No password management in AxonOps
- Leverage your organization's authentication policies
- Support for multi-factor authentication through your IdP
- Centralized access control

### Simplified User Management
- Automatic user provisioning (JIT provisioning)
- Role-based access control through IdP groups
- Immediate access revocation when users leave

### Compliance
- Meet regulatory requirements for access control
- Audit trail through your identity provider
- Consistent authentication across all your tools

## How It Works

1. **User Access**: User navigates to `https://{orgname}.axonops.cloud`
2. **Redirect**: AxonOps redirects to your identity provider
3. **Authentication**: User logs in with corporate credentials
4. **SAML Assertion**: IdP sends authenticated user info back to AxonOps
5. **Access Granted**: User is logged into AxonOps with appropriate roles

## Prerequisites

Before configuring SAML:

1. **AxonOps Requirements**
   - SAML must be enabled for your organization by AxonOps support
   - You need administrator access to AxonOps Cloud

2. **Identity Provider Requirements**
   - Administrative access to your identity provider
   - Ability to create applications/integrations
   - Understanding of your organization's group/role structure

3. **Technical Requirements**
   - SSL certificate and private key (can be self-signed)
   - Understanding of SAML concepts

## Role-Based Access Control

AxonOps supports fine-grained access control through SAML attributes:

### Global Roles
- `superAdmin` - Full system access
- `admin` - Administrative access
- `dba` - Database administrator access
- `readonly` - Read-only monitoring access
- `billing` - Billing and cost information access

### Cluster-Specific Roles
Format: `orgname/clustertype/clustername/role`

Examples:
- `acme/cassandra/production/admin`
- `acme/kafka/staging/readonly`

## Getting Started

1. **Contact AxonOps Support** to enable SAML for your organization
2. **Choose Your Identity Provider** from our supported list
3. **Follow the Configuration Guide** for your chosen provider
4. **Test the Integration** with a pilot group
5. **Roll Out** to your organization

## Important Considerations

### URL Changes
After enabling SAML, your AxonOps URL changes from:
- `https://dash.axonops.cloud` 
to:
- `https://{orgname}.axonops.cloud`

Update any bookmarks or documentation accordingly.

### Dual Authentication
After SAML is configured, you have two login options:
1. **Standard Login**: `https://console.axonops.cloud` (username/password)
2. **SAML Login**: `https://{orgname}.axonops.cloud` (SSO)

### Certificate Management
- Generate certificates with sufficient validity period (3-10 years recommended)
- Plan for certificate renewal before expiry
- Keep private keys secure

## Troubleshooting

Common issues and solutions:

### Login Loops
- Verify callback URL is correctly configured
- Check certificate validity
- Ensure clock synchronization between systems

### Missing Roles
- Verify group/role attribute mapping
- Check user group membership in IdP
- Confirm attribute names match configuration

### Access Denied
- Ensure user is assigned to the application in IdP
- Verify at least one valid role is assigned
- Check SAML response includes required attributes

## Support

For assistance with SAML configuration:
1. Review the specific guide for your identity provider
2. Contact AxonOps support with:
   - Your organization name
   - Identity provider being used
   - Any error messages
   - SAML response (sanitized of sensitive data)