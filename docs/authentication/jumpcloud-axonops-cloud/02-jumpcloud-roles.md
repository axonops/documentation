# Configuring AxonOps Roles in JumpCloud

The permissions granted to each user are controlled by a custom group attribute named `axonopsroles`.
The `axonopsroles` attribute can contain a single role or a comma-separated list of roles which will
be assigned to all members of the group.

Global roles that can be assigned to AxonOps users:
- `superAdmin`
- `dba`
- `readonly`

Finer-grained access can be controlled by cluster type or individual cluster, for example:
- `orgname/cassandra/dba` This would give DBA-level access to all Cassandra clusters
- `orgname/kafka/readonly` This would give read-only access to all Kafka clusters
- `orgname/cassandra/cluster1/readonly` This would allow read-only access to Cassandra cluster `cluster1` only.

> replace `orgname` in these examples with your AxonOps organisation.


### 1\. Click "User Groups"

Access the User Groups section.

![Click 'User Groups'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2F1AECrRf967vPL4phK53PdL%2FwL4Ny3Vu4uXCJfkcZ4sWy7_doc.png?alt=media&token=382cfd21-0690-47de-b31c-a7c950d06fae)

### 2\. Open a group
The group name could be anything, "AxonOps Admins" is only an example here

![Click 'AxonOps Admins'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2F1AECrRf967vPL4phK53PdL%2Fqv5d3ZuyYAq7nggLN5Uj2g_doc.png?alt=media&token=d88ce28b-1616-416e-8f66-1a1a0c42a9ee)

### 3\. Click "+ Add Custom Attribute"

Add a custom attribute.

![Click '+ Add Custom Attribute'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2F1AECrRf967vPL4phK53PdL%2F1FyTaTwELn7aDR9rTeuFes_doc.png?alt=media&token=e08dcc1e-b32b-48d0-b5ba-103962df0547)

### 4\. Select "String"

Select the data type.

![Click 'String'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2F1AECrRf967vPL4phK53PdL%2FrqEtZbXJrHvV2hqNGBBxbM_doc.png?alt=media&token=cc6eb766-3be6-47f5-8d2c-a4d2fbe3e856)

### 5\. Click "Attribute Name"

Enter the attribute name.

![Click 'Attribute Name'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2F1AECrRf967vPL4phK53PdL%2F31G4YYJSr33LMfw69qVMXt_doc.png?alt=media&token=ea124a60-5627-4dbf-b946-92385f6b9c48)

### 6\. Enter "axonopsroles"

![Fill 'axonopsroles'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2F1AECrRf967vPL4phK53PdL%2Fn8xvcxAqd81gs77ahxfbmf_doc.png?alt=media&token=652d9432-4038-4759-a911-65345793526f)

### 7\. Enter AxonOps roles for the group

Enter the AxonOps role(s) to assign to the members of this group. This could be a single
role or a comma-separated list. See above for allowed values.

![Fill 'superAdmin'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2F1AECrRf967vPL4phK53PdL%2FxA2oYyyn3HiReixPziQx5u_doc.png?alt=media&token=e39263e5-8f50-44b7-9b76-ee003c665716)

### 8\. Click "Save Group"

Save the group settings.

![Click 'Save Group'](https://static.guidde.com/v0/qg%2FDYav2XnW7MMsJ8b5Y7XiJvaQaH43%2F1AECrRf967vPL4phK53PdL%2F4m7VHtUmSc5tKcW64E7eWM_doc.png?alt=media&token=0db41aef-3d2c-4873-9958-10367a0ee395)

### 9\. Repeat the above steps to configure the roles for other groups

## Next Steps

[Configure SAML in AxonOps Cloud](../03-axonops-saml-jumpcloud)
