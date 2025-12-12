# Azure Entra ID SAML Application Configuration

## 1. Login to Azure Portal

Login to the [Azure Portal](https://portal.azure.com) with an account that has permissions to create Enterprise Applications.

## 2. Navigate to Enterprise Applications

1. In the Azure Portal, search for "Enterprise applications" in the top search bar
2. Click on **Enterprise applications** under Services

## 3. Create New Application

1. Click **+ New application** at the top of the Enterprise applications page
2. Click **+ Create your own application**
3. Enter a name for your application (e.g., "AxonOps Cloud")
4. Select **Integrate any other application you don't find in the gallery (Non-gallery)**
5. Click **Create**

## 4. Configure Single Sign-On

1. Once the application is created, you'll be taken to the application overview page
2. In the left navigation, click **Single sign-on**
3. Select **SAML** as the single sign-on method

## 5. Basic SAML Configuration

Click **Edit** in the Basic SAML Configuration section and configure the following:

### Identifier (Entity ID)
Enter a unique identifier for your application. This can be any string, for example:
- `axonops-production`
- `axonops-yourcompany`

### Reply URL (Assertion Consumer Service URL)
Enter the following URL, replacing `<orgname>` with your AxonOps organization name:
```
https://<orgname>.axonops.cloud/login-idp/callback
```

### Sign on URL (Optional)
You can leave this blank or set it to:
```
https://<orgname>.axonops.cloud
```

Click **Save** when done.

## 6. User Attributes & Claims

The default attributes are usually sufficient, but ensure the following claims are present:

1. Click **Edit** in the User Attributes & Claims section
2. Verify these claims exist:
   - `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress` → user.mail
   - `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname` → user.givenname
   - `http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname` → user.surname

## 7. SAML Signing Certificate

1. In the SAML Signing Certificate section, download the **Certificate (Base64)**
2. Also download the **Federation Metadata XML** - you'll need information from this file later

## 8. Set up AxonOps Cloud URLs

In the "Set up [Your App Name]" section, note down the following URLs:
- **Login URL** (also called Sign-On URL or SAML SSO URL)
- **Azure AD Identifier** (also called Entity ID or Issuer URL)

You'll need these when configuring AxonOps.

## 9. Assign Users and Groups

1. In the left navigation, click **Users and groups**
2. Click **+ Add user/group**
3. Select the users or groups who should have access to AxonOps
4. Click **Assign**

## Next Steps

Now that you've configured the Azure Entra ID application, proceed to [Configure Roles in Azure Entra ID](02-azure-roles.md) to set up role-based access control.