# JumpCloud SAML Configuration

### 1\. Login to JumpCloud as an administrator
Login as an administrator then go to the **SSO Applications** page

### 2\. Click "Add New Application"

Add a new application.

![Click 'Add New Application'](img/01-jumpcloud-app/image-0.png)

### 3\. Select Custom Application

![Click 'Select'](img/01-jumpcloud-app/image-1.png)

### 4\. Click "Next"

Proceed to the next step.

![Click 'Next'](img/01-jumpcloud-app/image-2.png)

### 5\. Click "Manage Single Sign-On (SSO)"

Access Single Sign-On settings.

![Click 'Manage Single Sign-On (SSO)'](img/01-jumpcloud-app/image-3.png)

### 6\. Click "Next"

Move on to the next section.

![Click 'Next'](img/01-jumpcloud-app/image-4.png)

### 7\. Enter Application Name

Enter a friendly name for the application in the Display Label field

![Fill 'AxonOps Cloud Test'](img/01-jumpcloud-app/image-5.png)

### 8\. Click "Save Application"

Save the application settings.

![Click 'Save Application'](img/01-jumpcloud-app/image-6.png)

### 9\. Click "Configure Application"

Configure the application settings.

![Click 'Configure Application'](img/01-jumpcloud-app/image-7.png)

### 12\. Click "IdP Entity ID"

Enter the IdP Entity ID.


### 10\. Enter the IdP Entity ID

This can be any string as long as the same is used in AxonOps. We recommend setting this to `jumpcloud-axonops`.

![Click 'IdP Entity ID'](img/01-jumpcloud-app/image-8.png)

### 11\. Enter the SP Entity ID

Enter `https://axonops.com/saml/metadata` in the **SP Entity ID** field

![Click 'SP Entity ID'](img/01-jumpcloud-app/image-9.png)

### 12\. Set the ACS URL

Enter `https://orgname.axonops.cloud/login-idp/callback` in the **ACS URL** field (replace `orgname` with your AxonOps organisation name)

![Click 'https://YOUR_ACS_URL/'](img/01-jumpcloud-app/image-10.png)

### 13\. Click "Replace SP Certificate"

Upload the certificate you generated in the prerequisites

![Click 'Replace SP Certificate'](img/01-jumpcloud-app/image-11.png)

### 14\. Configure Assertion signing

Under the **Sign** option, select `Assertion`

![Click 'Assertion'](img/01-jumpcloud-app/image-12.png)

### 15\. Configure user attributes

Under **User Attributes**, click "add attribute"

![Click 'add attribute'](img/01-jumpcloud-app/image-13.png)

### 16\. Configure attribute mapping

Enter `axonopsroles` in the "Service Provider Attribute" field

![Fill 'axonopsroles'](img/01-jumpcloud-app/image-14.png)

Now select `Custom User or Group Attribute` and enter a custom value of `axonopsroles`

![Go here](img/01-jumpcloud-app/image-15.png)

### 17\. Allow groups access to AxonOps

Access the User Groups section.

![Click 'User Groups'](img/01-jumpcloud-app/image-16.png)

### 18\. Select groups that can access AxonOps

Tick all groups that you wish to provide access to AxonOps

![Click '6848164eb4054000016074ef'](img/01-jumpcloud-app/image-17.png)

### 19\. Return to the "SSO" tab

![Click 'SSO'](img/01-jumpcloud-app/image-18.png)

### 20\. Click "Export Metadata"

Export XML metadata from JumpCloud. You will need this to configure AxonOps.

![Click 'Export Metadata'](img/01-jumpcloud-app/image-19.png)

### 21\. Click "save"

Save the changes.

![Click 'save'](img/01-jumpcloud-app/image-20.png)

## Next Steps

[Configure roles in JumpCloud](02-jumpcloud-roles.md)

[Configure SAML in AxonOps Cloud](03-axonops-saml-jumpcloud.md)
