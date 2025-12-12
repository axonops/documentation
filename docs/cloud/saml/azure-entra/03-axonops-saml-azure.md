# Configure SAML in AxonOps Cloud for Azure Entra ID

This guide covers the final step of configuring SAML authentication in AxonOps Cloud using the information from your Azure Entra ID setup.

## Prerequisites

Before proceeding, ensure you have:
1. Completed the Azure Entra ID application configuration
2. Downloaded the SAML certificate from Azure
3. Noted the Login URL and Azure AD Identifier
4. Your SSL certificate and private key in PEM format

## Access SAML Configuration

1. Log in to [AxonOps Console](https://console.axonops.cloud) with an administrator account
2. Navigate to **Settings** → **SAML Authentication**
3. Click **Configure SAML** or **Edit SAML Configuration**

## Configure SAML Settings

### 1. Identity Provider Selection

Select **Azure AD / Microsoft Entra ID** from the Identity Provider dropdown.

### 2. Entry Point URL

Enter the **Login URL** from your Azure application. This is found in the Azure Portal under:
- Enterprise Applications → Your App → Single sign-on → Set up section
- It typically looks like: `https://login.microsoftonline.com/{tenant-id}/saml2`

### 3. Identity Provider Entity ID

Enter the **Azure AD Identifier** from your Azure application. This is typically:
```
https://sts.windows.net/{tenant-id}/
```

### 4. Identity Provider Certificate

1. Open the certificate file you downloaded from Azure (Certificate Base64)
2. Copy the entire contents including:
   ```
   -----BEGIN CERTIFICATE-----
   [certificate content]
   -----END CERTIFICATE-----
   ```
3. Paste it into the **IdP Certificate** field

### 5. Service Provider Entity ID

This field should contain a unique identifier for your AxonOps instance. Use the same value you configured as the **Identifier (Entity ID)** in Azure:
- For example: `axonops-production` or `axonops-yourcompany`

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

### 8. Attribute Mapping (if needed)

The default Azure Entra ID attributes usually map correctly, but verify:
- Email: `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress`
- First Name: `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname`
- Last Name: `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname`
- Roles: `axonops-roles` (if configured)

## Save and Test

1. Click **Save Configuration**
2. AxonOps will validate the configuration
3. If validation succeeds, you'll see a confirmation message

## Testing the Integration

### 1. Test Login

1. Open a new browser window (or incognito/private mode)
2. Navigate to `https://{orgname}.axonops.cloud`
3. You should be redirected to the Microsoft/Azure login page
4. Sign in with an Azure account that has been assigned to the application
5. Upon successful authentication, you'll be redirected back to AxonOps

### 2. Verify User Access

1. Check that the user appears in AxonOps with the correct name and email
2. Verify that assigned roles are working correctly
3. Test access to different features based on the assigned role

## Troubleshooting

### Common Issues

**"Invalid SAML Response"**
- Verify the Entry Point URL is correct
- Check that the IdP certificate is properly formatted
- Ensure the Entity IDs match between Azure and AxonOps

**"User not authorized"**
- Confirm the user is assigned to the application in Azure
- Check that roles are properly configured if using role-based access
- Verify the role claim name is `axonops-roles`

**Certificate errors**
- Ensure you're using the Base64 encoded certificate from Azure
- Verify your SP certificate and private key are valid and match
- Check certificate expiration dates

### Debug Mode

If issues persist:
1. Enable SAML debug mode in AxonOps (if available)
2. Check browser developer tools for error messages
3. Review Azure sign-in logs for authentication attempts

## Maintenance

### Certificate Renewal

1. Azure certificates typically expire after 3 years
2. Monitor expiration dates and renew before expiry
3. Update the IdP certificate in AxonOps when Azure renews it

### Adding/Removing Users

1. Manage user access through Azure Enterprise Application assignments
2. Role changes in Azure are reflected after the user's next login

## Support

If you encounter issues not covered in this guide:
1. Contact AxonOps support with your organization name
2. Provide any error messages you're seeing
3. Include relevant configuration details (excluding sensitive information like private keys)