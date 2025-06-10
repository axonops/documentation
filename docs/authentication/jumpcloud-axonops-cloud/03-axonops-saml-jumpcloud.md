# Configuring SAML authentication in AxonOps Cloud

### 1\. Go to "console.axonops.cloud"

Go to the AxonOps console and login as a user with superadmin rights.
Open the SAML page by clicking the SAML link in the sidebar.

![Click 'SAML'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2F1AECrRf967vPL4phK53PdL%2F3RHMFtsMMW22FqCg8sP1rU_doc.png?alt=media&token=e317d950-8196-4da4-a8fd-f940c267f039)

### 3\. Click "Upload IdP Metadata XML"

Upload the IdP Metadata XML file that you downloaded from JumpCloud

![Click 'Upload IdP Metadata XML'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2F1AECrRf967vPL4phK53PdL%2Fp7GJWA378YExv3wcp9PwEG_doc.png?alt=media&token=9563f6fc-c2d7-427f-92ce-ebac3003a760)

### 4\. Enter the IdP Entity ID

Fill in the text box with `jumpcloud-axonops`, this must match the IdP Entity ID entered in JumpCloud.

![Fill 'jumpcloud-axonops'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2F1AECrRf967vPL4phK53PdL%2FsMX2rMq5RGqYGFH7BNhrUy_doc.png?alt=media&token=59f4a079-cdda-4872-8068-b12ea7dd2fe5)

### 5\. Enter the SP Entity ID

Enter `https://axonops.com/saml/metadata` in the SP Entity ID field

![Fill 'https://axonops.com/saml/metadata'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2F1AECrRf967vPL4phK53PdL%2FhtAWynDmFHFBePKc4MtHxZ_doc.png?alt=media&token=c6249faf-7207-4c91-9e45-98a6bd733acd)

### 6\. Click "SP Certificate \*"

Access the SP Certificate section.

![Click 'SP Certificate *'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2F1AECrRf967vPL4phK53PdL%2F2eKwLGZREwuGye6zT6wrsS_doc.png?alt=media&token=0aa4155c-df00-4339-b6a0-4c1275d00268)

### 7\. Paste in your certificate

Paste the PEM-format certificate you generated in the prerequisites into the `SP Certificate` field

![Fill '-----BEGIN...'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2F1AECrRf967vPL4phK53PdL%2FuMb9xK4G4bqomxeL3tfPbd_doc.png?alt=media&token=71bde9b0-1082-4881-9588-81db155597cd)

### 8\. Click "SP Private Key \*"

Access the SP Private Key section.

![Click 'SP Private Key *'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2F1AECrRf967vPL4phK53PdL%2FnySr3yQoNw83xX1LqaLoqh_doc.png?alt=media&token=cce43433-072c-42c6-882b-e1c5a83fc60d)

### 9. Paste your private key

Paste the PEM-format private key you generated in the prerequisites into the `SP Private Key` field

![Fill '-----BEGIN PRIVATE...'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2F1AECrRf967vPL4phK53PdL%2FwZpvMowvLPpLSKr5WYUCuj_doc.png?alt=media&token=bbd952a6-d6d5-4cff-a3dd-17b1c8899669)

### 10\. Click "Save"

Save the settings.

![Click 'Save'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2F1AECrRf967vPL4phK53PdL%2F88beaEbCPABY2XjYnFprNR_doc.png?alt=media&token=d2288c1e-fec8-4d94-9e3e-6562c18d9e33)

