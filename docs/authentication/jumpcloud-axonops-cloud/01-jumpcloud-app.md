# JumpCloud SAML Configuration

### 1\. Login to JumpCloud as an administrator
Login as an administrator then go to the **SSO Applications** page

### 2\. Click "Add New Application"

Add a new application.

![Click 'Add New Application'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2FunaHzJzAWySemmNrnohagr%2Fim1YLn94EgD1RFuNR4nqWz_doc.png?alt=media&token=a2fe939a-ba4e-410f-b9f4-233f9a45f3ad)

### 3\. Select Custom Application

![Click 'Select'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2FunaHzJzAWySemmNrnohagr%2Fp7mXqQv9Ct2CJVjkKrF3vT_doc.png?alt=media&token=2916234b-37ab-4f1f-a2cb-8e2e498c35b3)

### 4\. Click "Next"

Proceed to the next step.

![Click 'Next'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2FunaHzJzAWySemmNrnohagr%2FbCWPDTBVcEKmxaFeNexTA7_doc.png?alt=media&token=182d0df9-3fb6-4cd4-b616-3b5921c5b174)

### 5\. Click "Manage Single Sign-On (SSO)"

Access Single Sign-On settings.

![Click 'Manage Single Sign-On (SSO)'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2FunaHzJzAWySemmNrnohagr%2F6sqn2zr5f4yUese78xnCUh_doc.png?alt=media&token=1385320c-51ac-4e3c-8fd5-c6897b49e4dd)

### 6\. Click "Next"

Move on to the next section.

![Click 'Next'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2FunaHzJzAWySemmNrnohagr%2FrUtwziawr6vENfGp8PhPiB_doc.png?alt=media&token=f1a6be5a-2840-48ef-a919-5afc39afea46)

### 7\. Enter Application Name

Enter a friendly name for the application in the Display Label field

![Fill 'AxonOps Cloud Test'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2FunaHzJzAWySemmNrnohagr%2FwYxNFifxNxHz6F3gcVzc9C_doc.png?alt=media&token=fd8bd8f7-7df9-4038-be5c-b9064ca3bdab)

### 8\. Click "Save Application"

Save the application settings.

![Click 'Save Application'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2FunaHzJzAWySemmNrnohagr%2F5exXJWB37NJJRi4JraZm3G_doc.png?alt=media&token=e6b5c59b-5b0d-4e0b-95c0-18af32a589d7)

### 9\. Click "Configure Application"

Configure the application settings.

![Click 'Configure Application'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2FunaHzJzAWySemmNrnohagr%2FdPdAJsVYqcGg79AqpYxvx5_doc.png?alt=media&token=7f264e70-96dc-43f1-b18c-3104fbca4548)

### 12\. Click "IdP Entity ID"

Enter the IdP Entity ID.


### 10\. Enter the IdP Entity ID

This can be any string as long as the same is used in AxonOps. We recommend setting this to `jumpcloud-axonops`.

![Click 'IdP Entity ID'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2FunaHzJzAWySemmNrnohagr%2FoG7rpRCTBNR3iFSJomnFNA_doc.png?alt=media&token=10dc1ae3-65dd-4b8b-80b7-8bafdc99fe55)

### 11\. Enter the SP Entity ID

Enter `https://axonops.com/saml/metadata` in the **SP Entity ID** field

![Click 'SP Entity ID'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2FunaHzJzAWySemmNrnohagr%2Fm542nWzzQmmXeToM8jMg9L_doc.png?alt=media&token=bb6e97ee-1048-476b-afa3-74dffed08ae9)

### 12\. Set the ACS URL

Enter `https://orgname.axonops.cloud/login-idp/callback` in the **ACS URL** field (replace `orgname` with your AxonOps organisation name)

![Click 'https://YOUR_ACS_URL/'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2FunaHzJzAWySemmNrnohagr%2FoLazT1TTTY8792EB6o4UiA_doc.png?alt=media&token=286ce6ab-96b2-4f1a-b43c-d1f71a538e46)

### 13\. Click "Replace SP Certificate"

Upload the certificate you generated in the prerequisites

![Click 'Replace SP Certificate'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2FunaHzJzAWySemmNrnohagr%2FgtXhcK1QS6jmL9H7ZXGiLy_doc.png?alt=media&token=1fc94253-0ecc-4241-a6f1-0317770343ea)

### 14\. Configure Assertion signing

Under the **Sign** option, select `Assertion`

![Click 'Assertion'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2FunaHzJzAWySemmNrnohagr%2FwyyiA5VYJNGT2DWXH3u2j8_doc.png?alt=media&token=935ce3b5-af3d-44b2-bec4-35b45ba65a90)

### 15\. Configure user attributes

Under **User Attributes**, click "add attribute"

![Click 'add attribute'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2FunaHzJzAWySemmNrnohagr%2FryjouYgw5niBMdgNabVcFe_doc.png?alt=media&token=66094711-7068-44f0-b5b4-80fe205e3180)

### 16\. Configure attribute mapping

Enter `axonopsroles` in the "Service Provider Attribute" field

![Fill 'axonopsroles'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2FunaHzJzAWySemmNrnohagr%2FwvHtbtrVQHKijCiXbgjjbY_doc.png?alt=media&token=5c901782-51b3-4499-a983-66aafa2e20bb)

Now select `Custom User or Group Attribute` and enter a custom value of `axonopsroles`

![Go here](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2FunaHzJzAWySemmNrnohagr%2FbV7P4r3Ad3Xzf3bWtF1mEK_doc.png?alt=media&token=b026873a-1ecb-4e53-a50b-ecf36f5c470a)

### 17\. Allow groups access to AxonOps

Access the User Groups section.

![Click 'User Groups'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2FunaHzJzAWySemmNrnohagr%2FvfADxi6VMfkAXbXEdLcNZU_doc.png?alt=media&token=a02e0fd2-e3dc-4f0c-b5ed-9b322daaeac0)

### 18\. Select groups that can access AxonOps

Tick all groups that you wish to provide access to AxonOps

![Click '6848164eb4054000016074ef'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2FunaHzJzAWySemmNrnohagr%2F5jQgV2puygoe94LqBZSt6V_doc.png?alt=media&token=c1aea888-deb7-4cee-94e3-e08f75ddf91f)

### 19\. Return to the "SSO" tab

![Click 'SSO'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2FunaHzJzAWySemmNrnohagr%2Fc9FyP8r8hH55KYdYWAaQUe_doc.png?alt=media&token=64fff74c-7e72-41d4-9517-196f29a34354)

### 20\. Click "Export Metadata"

Export XML metadata from JumpCloud. You will need this to configure AxonOps.

![Click 'Export Metadata'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2FunaHzJzAWySemmNrnohagr%2FvDZxjsaSugVstfGkConnTZ_doc.png?alt=media&token=929f46d9-3498-49cd-9df8-698a39085219)

### 21\. Click "save"

Save the changes.

![Click 'save'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2FunaHzJzAWySemmNrnohagr%2F2NuipYyAXqxt6dE4DwQHzc_doc.png?alt=media&token=533fd173-3d07-47d2-aeea-83ac91bb6193)

## Next Steps

[Configure roles in JumpCloud](../02-jumpcloud-roles)

[Configure SAML in AxonOps Cloud](../03-axonops-saml-jumpcloud)
