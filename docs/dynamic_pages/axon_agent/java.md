Add the following line at the end of `/etc/cassandra/cassandra-env.sh`:

<div id="Cassandra30Div" class="javacas">
  ```
  JVM_OPTS="$JVM_OPTS -javaagent:/usr/share/axonops/axon-cassandra3.0-agent.jar=/etc/axonops/axon-agent.yml"
  ```
</div>
<div id="Cassandra311Div" class="javacas" style="display:none">
  ```
  JVM_OPTS="$JVM_OPTS -javaagent:/usr/share/axonops/axon-cassandra3.11-agent.jar=/etc/axonops/axon-agent.yml"
  ```
</div>
<div id="Cassandra40Div" class="javacas" style="display:none">
  ```
  JVM_OPTS="$JVM_OPTS -javaagent:/usr/share/axonops/axon-cassandra4.0-agent.jar=/etc/axonops/axon-agent.yml"
  ```
</div>
<div id="Cassandra41Div" class="javacas" style="display:none">
  ```
  JVM_OPTS="$JVM_OPTS -javaagent:/usr/share/axonops/axon-cassandra4.1-agent.jar=/etc/axonops/axon-agent.yml"
  ```
</div>
<div id="Cassandra50Div" class="javacas" style="display:none">
  ```
  . /usr/share/axonops/axonops-jvm.options
  ```
</div>

If Cassandra was installed using a tarball, the correct path for the `cassandra-env.sh`
will be `<Cassandra Installation Directory>/conf/cassandra-env.sh`.

> **NB.** Make sure this configuration is not overridden by automation tools.

### Configure Cassandra user group

Configure the Linux user groups by:

* Adding the `axonops` user to the `cassandra` user group.
* Adding the `cassandra` user to the `axonops` user group.

```bash
{!installation/axon-agent/scripts/setup-users.sh!}
```

If Cassandra was setup to use a non-default user or group,
`CASSANDRA_GROUP` and/or `CASSANDRA_USER`
will need be updated accordingly for the above commands to work properly.

### Uninstall `needrestart` Package

Due to recent change with `needrestart`, as seen in Ubuntu 24.04, uninstalling the
`needrestart` package is currently recommended.

Failure to uninstall the `needrestart` package may cause the Cassandra service to be
restarted when updating the `AxonOps agent` package.
