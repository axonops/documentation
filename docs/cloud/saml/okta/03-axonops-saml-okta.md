# Configure SAML in AxonOps Cloud for Okta

This guide covers the final step of configuring SAML authentication in AxonOps Cloud using the information from your Okta setup.

## Prerequisites

Before proceeding, ensure you have:

1. Completed the Okta application configuration
2. Downloaded the SAML certificate from Okta
3. Noted the Identity Provider Single Sign-On URL and Issuer
4. Your SSL certificate and private key in PEM format
5. Created and assigned users to appropriate Okta groups

## Access SAML Configuration

1. Log in to [AxonOps Console](https://console.axonops.cloud) with an administrator account
2. Navigate to **Settings** → **SAML Authentication**
3. Click **Configure SAML** or **Edit SAML Configuration**

## Configure SAML Settings

### 1. Identity Provider Selection

Select **Okta** from the Identity Provider dropdown.

### 2. Entry Point URL

Enter the **Identity Provider Single Sign-On URL** from your Okta application. This is found in:
- Okta Admin → Applications → Your App → Sign On → View SAML setup instructions
- It typically looks like: `https://{yourOktaDomain}.okta.com/app/{yourOktaDomain}_axonopscloud_1/exk.../sso/saml`

### 3. Identity Provider Entity ID

Enter the **Identity Provider Issuer** from Okta. This is typically:
```
http://www.okta.com/exk...
```

You can find this in the SAML setup instructions or metadata.

### 4. Identity Provider Certificate

1. Open the X.509 certificate from Okta (found in SAML setup instructions)
2. Copy the entire contents including:
   ```
   -----BEGIN CERTIFICATE-----
   [certificate content]
   -----END CERTIFICATE-----
   ```
3. Paste it into the **IdP Certificate** field

### 5. Service Provider Entity ID

This should match the **Audience URI (SP Entity ID)** you configured in Okta. For example:
- `axonops-production`
- `yourcompany-axonops`

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

### 8. Role Attribute Name

Set the role attribute name to: `axonopsroles`

This must match the group attribute statement name configured in Okta.

### 9. Role Mapping Configuration

Configure how Okta groups map to AxonOps roles:

**Role Prefix**: `axonops-`

This tells AxonOps to strip the "axonops-" prefix from group names when determining roles.

## Save and Test

1. Click **Save Configuration**
2. AxonOps will validate the configuration
3. If validation succeeds, you'll see a confirmation message

## Testing the Integration

### 1. Test Login

1. Open a new browser window (or incognito/private mode)
2. Navigate to `https://{orgname}.axonops.cloud`
3. You should be redirected to the Okta login page
4. Sign in with an Okta account that has been assigned to the application
5. Upon successful authentication, you'll be redirected back to AxonOps

### 2. Verify User Access

1. Check that the user appears in AxonOps with the correct name and email
2. Verify that assigned roles are working correctly:
   - Users in `axonops-admin` group should have admin access
   - Users in `axonops-readonly` group should have read-only access
3. Test access to different features based on the assigned role

### 3. Verify Group Mapping

In AxonOps, check the user's profile to see which roles were assigned based on their Okta group memberships.

## Troubleshooting

### Common Issues

**"Invalid SAML Response"**
- Verify the Entry Point URL is correct
- Check that the IdP certificate is properly formatted
- Ensure the Entity IDs match between Okta and AxonOps

**"User not authorized"**
- Confirm the user is assigned to the application in Okta
- Check that the user is in at least one "axonops-" prefixed group
- Verify the group attribute statement is named `axonopsroles`

**Groups/Roles not appearing**
- Ensure all groups start with "axonops-" prefix
- Verify the group filter in Okta is set to "Starts with" → "axonops-"
- Check that the role attribute name in AxonOps is set to `axonopsroles`

**Certificate errors**
- Ensure you're using the correct certificate from Okta
- Verify your SP certificate and private key are valid and match
- Check certificate expiration dates

### Debug Mode

If issues persist:
1. Enable SAML debug mode in AxonOps (if available)
2. Use Okta's System Log to trace authentication attempts
3. Check browser developer tools for error messages

### Testing with Okta Preview

Use Okta's preview feature to test the SAML response:
1. In Okta Admin → Applications → Your App
2. Click on a user assignment
3. Use the "Preview SAML" feature to see what will be sent

## Maintenance

### Certificate Renewal

1. Monitor certificate expiration dates in both Okta and AxonOps
2. Okta certificates typically auto-rotate; update in AxonOps when changed
3. Renew your SP certificate before expiry

### Managing Access

1. Add/remove users through Okta group membership
2. Changes take effect on the user's next login
3. Use Okta's group rules for automatic user assignment

### Monitoring

1. Regularly review Okta System Log for failed authentications
2. Monitor AxonOps access logs
3. Set up alerts for unusual access patterns

## Integration Features

### Just-In-Time Provisioning

AxonOps supports JIT provisioning, meaning:
- Users are automatically created on first SAML login
- User attributes are updated on each login
- No need to pre-create users in AxonOps

### Session Management

- SAML sessions are independent of Okta sessions
- Users must log out of both AxonOps and Okta for complete sign-out
- Configure session timeouts in both systems as needed

## Support

If you encounter issues not covered in this guide:
1. Contact AxonOps support with your organization name
2. Provide any error messages you're seeing
3. Include the SAML response from Okta preview (excluding sensitive data)
4. Share relevant Okta System Log entries