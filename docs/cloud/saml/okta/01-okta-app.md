# Okta SAML Application Configuration

## 1. Login to Okta Admin Console

Login to your Okta organization's Admin Console as an administrator.

## 2. Navigate to Applications

1. In the Okta Admin Console, navigate to **Applications** → **Applications**
2. Click **Create App Integration**

## 3. Create New SAML Application

1. Select **SAML 2.0** as the Sign-in method
2. Click **Next**

## 4. General Settings

On the General Settings page:

1. **App name**: Enter a descriptive name (e.g., "AxonOps Cloud")
2. **App logo**: (Optional) Upload an AxonOps logo
3. **App visibility**: Configure according to your preferences
4. Click **Next**

## 5. Configure SAML Settings

### General Section

Configure the following SAML settings:

**Single sign on URL**
```
https://<orgname>.axonops.cloud/login-idp/callback
```
Replace `<orgname>` with your AxonOps organization name.

- ✓ Check "Use this for Recipient URL and Destination URL"

**Audience URI (SP Entity ID)**

Enter your organization name or a unique identifier, for example:
- `axonops-production`
- `yourcompany-axonops`

**Default RelayState**

Leave blank

**Name ID format**

Select: **EmailAddress**

**Application username**

Select: **Email**

### Attribute Statements

Add the following attribute statements:

| Name | Name format | Value |
|------|-------------|-------|
| email | Basic | user.email |
| firstName | Basic | user.firstName |
| lastName | Basic | user.lastName |

### Group Attribute Statements

This is critical for role-based access control. Add a group attribute statement:

- **Name**: `axonopsroles`
- **Name format**: Basic
- **Filter**: Starts with → `axonops-`

This will send all groups that start with "axonops-" to AxonOps for role mapping.

Click **Next** when done.

## 6. Feedback

On the Feedback page:

1. Select "I'm an Okta customer adding an internal app"
2. Select appropriate options for your use case
3. Click **Finish**

## 7. Download SAML Metadata

After creating the application:

1. Navigate to the **Sign On** tab of your newly created application
2. Find the **SAML Signing Certificates** section
3. Click **Actions** → **Download certificate** for the active certificate
4. In the **Metadata URL** section, copy the URL or download the metadata XML

## 8. View Setup Instructions

1. Still in the **Sign On** tab
2. Click **View SAML setup instructions**
3. Note down the following values:
   - **Identity Provider Single Sign-On URL**
   - **Identity Provider Issuer**
   - **X.509 Certificate**

## 9. Assign Users and Groups

### Assign Individual Users

1. Navigate to the **Assignments** tab
2. Click **Assign** → **Assign to People**
3. Search for and select users
4. Click **Assign** for each user
5. Click **Done**

### Assign Groups

1. Click **Assign** → **Assign to Groups**
2. Select the appropriate groups (must start with "axonops-")
3. Click **Assign** for each group
4. Click **Done**

## 10. Configure Application Settings (Optional)

In the **General** tab, you can configure:

- **Login/logout URLs**
- **User provisioning** (if needed)
- **App visibility settings**

## Next Steps

Now that you've configured the Okta application, proceed to [Configure Roles in Okta](02-okta-roles.md) to set up role-based access control.