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
  - **startTLS** : true/false - Only upgrades to an encrypted connection once the authentication is successful, only needs to be enabled if the server requires it.
  - **base**: A base DN is the point from where the users/groups will be searched. 
  - **bindDN** : the DN of the user who has access to read from and bind to LDAP.
  - **bindPassword** : The bindDN users password.
  - **userFilter** : Filters are a key element in defining the criteria used to identify entries in search requests.
                 
          Some examples could be 
          - (uid=%s) UID of a user.
          - (cn=%s) is the Common Name of a user/group.

  - **roleAttribute** : the LDAP attribute that contains the users groups or a groups members.
  - **rolesMapping** : Mapping of LDAP user/groups to AxonOps security groups.

### Role Mapping

The rolesMapping has multiple levels based on the configuration of you On-premise AxonOps Server setup : 

  - **\_global\_** : Overarching level that has full coverage of all the configurations per AxonOps Server installation or setup.
  - **organisationName/<CLUSTER TYPE>**: This can be either Cassandra or Kafka depending on what cluster types you are monitoring.
  - **organisationName/<Cluster TYPE>/<CLUSTER NAME>** : This level will give fine grained permission to specific clusters and cluster types being monitored.

For the above levels there are 4 role mappings which are required fields :

  - **superUserRole** : The Super user which has permission to do everything on AxonOps setup. For e.g. Deleting a cluster from AxonOps Server.
  - **adminRole** : The Admin role can do most adminstration tasks but cannot delete clusters from AxonOps.
  - **backupAdminRole** : The user that has adminstration priviledges to create and manage backups. Has read only access to the rest of the AxonOps server pages and components.
  - **readOnlyRole** : A basic read-only role that cannot modify any configuration in AxonOps Server.

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
    
    base: "DC=example,DC=com"   
    bindDN: "CN=administrator,OU=Users,DC=example,DC=com"
    bindPassword: "##############"
    userFilter: "(cn=%s)" # The filter will search all AD entities(Users, Groups, Ditributed Groups etc.)
    rolesAttribute: "memberOf" # Default attribute that will contains a user groups
    callAttempts: 3 # how much retries in case of network issues
    rolesMapping:
      _global_: # _global_ overrides all other roles (underscores to prevent confusion with an organisationName named 'global')
        superUserRole: "cn=superuser,ou=Users,dc=example,dc=com"
        readOnlyRole: "cn=readonly,ou=Users,dc=example,dc=com"
        adminRole: "cn=admin,ou=Users,dc=example,dc=com"
        backupAdminRole: "cn=backupadmin,ou=Users,dc=example,dc=com"
      organisationName/cassandra: # cluster type permissions
        superUserRole: "cn=cassandra_superusers,ou=Groups,dc=example,dc=com"
        readOnlyRole: "cn=cassandra_readonly,ou=Groups,dc=example,dc=com"
        adminRole: "cn=cassandra_admins,ou=Groups,dc=example,dc=com"
        backupAdminRole: "cn=cassandra_backupadmins,ou=Groups,dc=example,dc=com"
      organisationName/cassandra/prod:  # Example Production Cassandra cluster permissions
        superUserRole: "cn=cassandra_prod_superusers,ou=Groups,dc=example,dc=com"
        readOnlyRole: "cn=cassandra_prod_readonly,ou=Groups,dc=example,dc=com"
        adminRole: "cn=cassandra_prod_admins,ou=Groups,dc=example,dc=com"
        backupAdminRole: "cn=cassandra_prod_backupadmins,ou=Groups,dc=example,dc=com"
```