# Configure SAML in AxonOps Cloud for JumpCloud

This guide covers the final step of configuring SAML authentication in AxonOps Cloud using the information from your JumpCloud setup.

## Prerequisites

Before proceeding, ensure you have:
1. Completed the JumpCloud application configuration
2. Downloaded the IdP certificate from JumpCloud
3. Noted the IdP URL and Entity ID from JumpCloud
4. Your SSL certificate and private key in PEM format
5. Created groups with custom attributes and assigned users

## Access SAML Configuration

1. Log in to [AxonOps Console](https://console.axonops.cloud) with an administrator account
2. Navigate to **Settings** → **SAML Authentication**
3. Click **Configure SAML** or **Edit SAML Configuration**

## Configure SAML Settings

### 1. Identity Provider Selection

Select **JumpCloud** from the Identity Provider dropdown.

### 2. Entry Point URL

Enter the **IdP URL** from your JumpCloud application. This is found in:
- JumpCloud Admin → SSO → Your App → SSO tab
- It typically looks like: `https://sso.jumpcloud.com/saml2/axonops-cloud/{unique-id}`

### 3. Identity Provider Entity ID

Enter the **IdP Entity ID** from JumpCloud. This is typically:
```
JumpCloud
```

Some JumpCloud configurations may use a URL format. Check your JumpCloud SSO settings for the exact value.

### 4. Identity Provider Certificate

1. Open the IdP certificate file you downloaded from JumpCloud
2. Copy the entire contents including:
   ```
   -----BEGIN CERTIFICATE-----
   [certificate content]
   -----END CERTIFICATE-----
   ```
3. Paste it into the **IdP Certificate** field

### 5. Service Provider Entity ID

This must match exactly what you configured in JumpCloud:
```
https://axonops.com/saml/metadata
```

### 6. Service Provider Certificate

Paste your SSL certificate (generated during prerequisites):
```
-----BEGIN CERTIFICATE-----
[your certificate content]
-----END CERTIFICATE-----
```

### 7. Service Provider Private Key

Paste your SSL private key (generated during prerequisites):
```
-----BEGIN PRIVATE KEY-----
[your private key content]
-----END PRIVATE KEY-----
```

**Important**: Keep your private key secure and never share it.

### 8. Attribute Mapping

JumpCloud should automatically send the correct attributes, but verify:
- **Email**: Should map automatically from JumpCloud user email
- **First Name**: Should map from JumpCloud user first name
- **Last Name**: Should map from JumpCloud user last name
- **Roles**: Will come from the `axonops-roles` custom attribute

### 9. Role Attribute Configuration

Ensure the role attribute name is set to: `axonops-roles`

This must match the custom attribute name configured in JumpCloud groups.

## Save and Test

1. Click **Save Configuration**
2. AxonOps will validate the configuration
3. If validation succeeds, you'll see a confirmation message

## Testing the Integration

### 1. Test Login

1. Open a new browser window (or incognito/private mode)
2. Navigate to `https://{orgname}.axonops.cloud`
3. You should be redirected to the JumpCloud login page
4. Sign in with a JumpCloud user account that:
   - Is assigned to the AxonOps SAML application
   - Is a member of at least one group with `axonops-roles` attribute
5. Upon successful authentication, you'll be redirected back to AxonOps

### 2. Verify User Access

1. Check that the user appears in AxonOps with the correct name and email
2. Verify that assigned roles are working correctly:
   - Users with `admin` role should have administrative access
   - Users with `readonly` role should have read-only access
3. Test access to different features based on the assigned role

### 3. Check Role Mapping

Review the user's profile in AxonOps to confirm:
- The roles from JumpCloud groups are properly applied
- Multiple roles (if assigned) are all present
- Cluster-specific roles are working as expected

## Troubleshooting

### Common Issues

**"Invalid SAML Response"**
- Verify the Entry Point URL matches your JumpCloud IdP URL
- Check that the IdP certificate is properly formatted
- Ensure the SP Entity ID is exactly `https://axonops.com/saml/metadata`
- Verify that "Sign Assertion" is enabled in JumpCloud

**"User not authorized"**
- Confirm the user is assigned to the application in JumpCloud
- Check that the user is in at least one group with `axonops-roles` attribute
- Verify the custom attribute name is exactly `axonops-roles`

**Roles not appearing**
- Check group membership in JumpCloud
- Verify the custom attribute is configured at the group level
- Ensure the attribute name is `axonops-roles` (case-sensitive)
- Confirm the group is assigned to the SAML application

**Certificate errors**
- Ensure you're using the correct IdP certificate from JumpCloud
- Verify your SP certificate and private key are valid and match
- Check certificate expiration dates
- Confirm the certificate format includes header and footer lines

### Debug Information

If issues persist:

1. **Check JumpCloud Insights**:
   - Go to JumpCloud Admin → Insights → Events
   - Filter for SAML authentication events
   - Look for error messages or failed attempts

2. **Verify SAML Assertion**:
   - Use browser developer tools to capture the SAML response
   - Check that the `axonops-roles` attribute is present
   - Verify the attribute values match your configuration

3. **Test with a Simple Configuration**:
   - Create a test user with only one group
   - Assign a single, simple role (e.g., `readonly`)
   - Test if basic authentication works before complex roles

## Maintenance

### Certificate Management

1. **JumpCloud Certificates**:
   - JumpCloud manages its own certificates
   - Monitor for notifications about certificate updates
   - Update the IdP certificate in AxonOps when JumpCloud rotates it

2. **Service Provider Certificates**:
   - Monitor your SP certificate expiration
   - Plan renewal at least 30 days before expiry
   - Generate new certificates using the same OpenSSL commands

### User Management

1. **Adding Users**:
   - Add users to appropriate JumpCloud groups
   - Changes take effect on next login
   - No need to create users in AxonOps (JIT provisioning)

2. **Removing Access**:
   - Remove users from JumpCloud groups
   - Or disable their JumpCloud account
   - Access is revoked immediately

3. **Changing Roles**:
   - Modify group membership in JumpCloud
   - Changes apply on next user login
   - Consider forcing re-authentication for immediate changes

### Monitoring

1. **Access Logs**:
   - Monitor AxonOps access logs for unusual patterns
   - Review JumpCloud Insights for authentication events
   - Set up alerts for failed login attempts

2. **Regular Audits**:
   - Review group memberships quarterly
   - Verify role assignments match job responsibilities
   - Remove unnecessary access promptly

## Advanced Features

### Session Management

- JumpCloud SSO sessions are separate from AxonOps sessions
- Configure session timeouts in both systems as needed
- Users must log out of both systems for complete sign-out

### Multi-Factor Authentication

- Enable MFA in JumpCloud for enhanced security
- MFA challenges occur at the JumpCloud login
- AxonOps inherits the security from JumpCloud authentication

## Support

If you encounter issues not covered in this guide:
1. Contact AxonOps support with your organization name
2. Provide any error messages you're seeing
3. Include sanitized SAML responses if available
4. Share relevant JumpCloud Insights event logs