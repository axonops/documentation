---
title: "Configuring SAML authentication in AxonOps Cloud"
description: "Complete AxonOps SAML configuration with JumpCloud. Finalize SSO integration settings."
meta:
  - name: keywords
    content: "AxonOps SAML, JumpCloud integration, SSO configuration, SAML settings"
---

# Configuring SAML authentication in AxonOps Cloud

### 1\. Go to "console.axonops.cloud"

Go to the AxonOps console and login as a user with superadmin rights.
Open the SAML page by clicking the SAML link in the sidebar.

![Click 'SAML'](img/03-axonops-saml-jumpcloud/image-0.png)

### 3\. Click "Upload IdP Metadata XML"

Upload the IdP Metadata XML file that you downloaded from JumpCloud

![Click 'Upload IdP Metadata XML'](img/03-axonops-saml-jumpcloud/image-1.png)

### 4\. Enter the IdP Entity ID

Fill in the text box with `jumpcloud-axonops`, this must match the IdP Entity ID entered in JumpCloud.

![Fill 'jumpcloud-axonops'](img/03-axonops-saml-jumpcloud/image-2.png)

### 5\. Enter the SP Entity ID

Enter `https://axonops.com/saml/metadata` in the SP Entity ID field

![Fill 'https://axonops.com/saml/metadata'](img/03-axonops-saml-jumpcloud/image-3.png)

### 6\. Click "SP Certificate"

Access the SP Certificate section.

![Click 'SP Certificate'](img/03-axonops-saml-jumpcloud/image-4.png)

### 7\. Paste in your certificate

Paste the PEM-format certificate you generated in the prerequisites into the `SP Certificate` field

![Fill '-----BEGIN...'](img/03-axonops-saml-jumpcloud/image-5.png)

### 8\. Click "SP Private Key"

Access the SP Private Key section.

![Click 'SP Private Key'](img/03-axonops-saml-jumpcloud/image-6.png)

### 9. Paste your private key

Paste the PEM-format private key you generated in the prerequisites into the `SP Private Key` field

![Fill '-----BEGIN PRIVATE...'](img/03-axonops-saml-jumpcloud/image-7.png)

### 10\. Click "Save"

Save the settings.

![Click 'Save'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2F1AECrRf967vPL4phK53PdL%2F88beaEbCPABY2XjYnFprNR_doc.png?alt=media&token=d2288c1e-fec8-4d94-9e3e-6562c18d9e33)

