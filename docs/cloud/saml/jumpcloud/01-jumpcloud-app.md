# JumpCloud SAML Application Configuration

## 1. Login to JumpCloud Admin Console

Login to the [JumpCloud Admin Console](https://console.jumpcloud.com) with an administrator account.

## 2. Navigate to SSO Applications

In the JumpCloud Admin Console, navigate to **SSO** in the left sidebar.

## 3. Add New Application

1. Click the **+** (plus) button to add a new application
2. Search for "SAML" or select **Custom SAML App**
3. Click **configure**

## 4. General Info

Configure the basic application information:

1. **Display Label**: Enter a name for your application (e.g., "AxonOps Cloud")
2. **Description**: (Optional) Add a description
3. **Logo**: (Optional) Upload an AxonOps logo for the application tile
4. Click **Save** to create the application

## 5. SSO Configuration

After saving, click on your newly created application to configure SSO settings.

### Configure SAML Settings

In the **SSO** tab, configure the following settings:

**SP Entity ID**
```
https://axonops.com/saml/metadata
```

**ACS URL**
```
https://<orgname>.axonops.cloud/login-idp/callback
```
Replace `<orgname>` with your AxonOps organization name.

### SAML Attributes

**Sign Assertion**: ✓ Enable (this must be checked)

**Signature Algorithm**: RSA-SHA256 (default)

**Login URL**: Leave as default or customize if needed

## 6. IdP Certificate

1. In the SSO configuration page, locate the **IDP Certificate**
2. Click **Download certificate** to save the certificate
3. You'll need this certificate when configuring AxonOps

## 7. IdP Information

Note down the following information from the SSO configuration:

- **IdP URL**: The single sign-on URL (looks like `https://sso.jumpcloud.com/saml2/...`)
- **IdP Entity ID**: JumpCloud's entity identifier

## 8. User Attributes

In the **User Attributes** section, you'll configure custom attributes for role mapping:

1. Click **add attribute**
2. Configure as follows:
   - **Service Provider Attribute Name**: `axonops-roles`
   - **JumpCloud Attribute Name**: Select "Add custom user attribute"
   - **Value**: `axonops-roles`

This attribute will be used to pass role information from JumpCloud to AxonOps.

## 9. Group Configuration

Enable group management for easier role assignment:

1. In the application settings, go to the **User Groups** tab
2. Enable **Enable management of user groups that can access this application**
3. You'll assign specific groups in the next section

## 10. Activation

1. Ensure the application status is set to **Active**
2. Save all configuration changes

## Important Notes

### Certificate Requirements
- JumpCloud provides its own signing certificate
- You'll still need to generate your own certificate/key pair for the Service Provider configuration

### URL Format
- Ensure your organization's custom domain is properly configured with AxonOps
- The ACS URL must exactly match the format: `https://<orgname>.axonops.cloud/login-idp/callback`

### Testing
- Before proceeding, verify that the application appears in the JumpCloud user portal
- The actual SSO flow will be tested after completing all configuration steps

## Next Steps

Now that you've configured the JumpCloud application, proceed to [Configure Roles in JumpCloud](02-jumpcloud-roles.md) to set up role-based access control.