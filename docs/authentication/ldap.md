# LDAP Authentication

To setup LDAP(Lightweight Directory Authentication Protocol) in AxonOps(On Premise Only) you will need to update the axon-server.yml configuration at the following location:

```/etc/axonops/axon-server.yml```


### LDAP Fields

!!! tip "All the configuration for the below fields should be provided by the LDAP Server administrator."

  - **host** : IP Address or Hostname of the LDAP server(A domain controller for Active Directory).
  - **port** : The configured LDAP port of the server.

          Standard Default ports are either 
          - 389(Unencrypted) 
          - 636(Encrypted LDAPS)
          The ports can be changed by LDAP adminstrators.

  - **useSSL** : true/false - Connects to LDAP using a secure port.
  - **startTLS** : true/false - Start SSL/TLS encryption before LDAP authentication takes place, set this to true if your LDAP server uses StartTLS.
  - **base**: A base DN is the point from which AxonOps wil search for users or groups. 
  - **bindDN** : The DN of the user who has access to bind to LDAP.
  - **bindPassword** : The bindDN user's password.
  - **userFilter** : This is the LDAP filter that AxonOps will use to locate users.
                 
          Some examples could be 
          - (uid=%s) : Search for users by using the LDAP "uid" field.
          - (cn=%s) : Search for users by using the "cn" (Common Name) field.

  - **rolesAttribute** : The LDAP attribute that contains the user's list of groups.
  - **rolesMapping** : Mapping of LDAP user/groups to AxonOps security groups.

### Role Mapping

The rolesMapping has multiple levels based on the configuration of your AxonOps setup : 

!!! Info "Please Note :"

    Values in UPPERCASE need to be updated with your configuration specific values.

  - **\_global\_** : Roles assigned to the _global_ scope apply to all clusters connected to AxonOps
  - **ORGANISATIONNAME/CLUSTER_TYPE**: Roles assigned to this scope apply to all clusters of the specified type, 
  - **ORGANISATIONNAME/CLUSTER_TYPE/CLUSTER_NAME** : Roles assigned to this scope apply to a single cluster.

**ORGANISATIONNAME** :  The name of your organisation as shown in the AxonOps frontend, should be equal to the org_name option in axon-server.yml

**CLUSTER_TYPE** : `cassandra` or `kafka`

**CLUSTER_NAME** : The name of the cluster as shown in the AxonOps frontend.

For the above levels there are 4 role mappings which are required fields :

  - **superUserRole** : The Super user which has permission to do everything on AxonOps setup.
  - **adminRole** : Similar to superUserRole but cannot configure AxonOps settings or log collectors.
  - **backupAdminRole** : The user that has adminstration priviledges to create and manage backups. Has read only access to the rest of the AxonOps server pages and components.
  - **readOnlyRole** : A basic read-only role that cannot modify any configuration in AxonOps.

Distinguished Names that are used in the role mappings can comprise of the following parts which define hierarchical structure in a LDAP directory.

  - **CN** = Common Name
  - **OU** = Organisational Unit
  - **O** = Organisation Name
  - **DC** = Domain Component


### Example LDAP Role Mappings

!!! warning "Take Note"

    The default built-in Active directory OU names are case-sensitive.


The following examples can be configured differently based on your LDAP setup.

  - **Active Directory Groups or Distribution Groups** :
    
    ```cn=cassandra_superusers,ou=Groups,dc=example,dc=com```

    - cn = cassandra_superusers or cassandra_<ENV>_superusers group
    - ou = Groups or Distribution Groups
    - dc = example.com

  - **Active Directory Users** : 
    
    ```cn=superuser,ou=Users,dc=example,dc=com```

    - cn = The name of the user e.g. superuser
    - ou = Users
    - dc = example.com


### axon-server.yml configuration example

``` yaml

auth:
  enabled: true
  type: "LDAP" # only LDAP is supported for now
  settings:
    host: "myldapserver.example.com"
    port: 636
    useSSL: true
    startTLS: true
    insecureSkipVerify: false
    
    base: "OU=Users,DC=example,DC=com"   
    bindDN: "CN=administrator,OU=Users,DC=example,DC=com"
    bindPassword: "##############"
    userFilter: "(cn=%s)"
    rolesAttribute: "memberOf"
    callAttempts: 3 # how many times to retry a connection to LDAP, in case of network issues.
    rolesMapping:
      _global_:
        superUserRole: "cn=superuser,ou=Groups,dc=example,dc=com"
        readOnlyRole: "cn=readonly,ou=Groups,dc=example,dc=com"
        adminRole: "cn=admin,ou=Groups,dc=example,dc=com"
        backupAdminRole: "cn=backupadmin,ou=Groups,dc=example,dc=com"
      organisationName/cassandra:
        superUserRole: "cn=cassandra_superusers,ou=Groups,dc=example,dc=com"
        readOnlyRole: "cn=cassandra_readonly,ou=Groups,dc=example,dc=com"
        adminRole: "cn=cassandra_admins,ou=Groups,dc=example,dc=com"
        backupAdminRole: "cn=cassandra_backupadmins,ou=Groups,dc=example,dc=com"
      organisationName/cassandra/prod:
        superUserRole: "cn=cassandra_prod_superusers,ou=Groups,dc=example,dc=com"
        readOnlyRole: "cn=cassandra_prod_readonly,ou=Groups,dc=example,dc=com"
        adminRole: "cn=cassandra_prod_admins,ou=Groups,dc=example,dc=com"
        backupAdminRole: "cn=cassandra_prod_backupadmins,ou=Groups,dc=example,dc=com"
```