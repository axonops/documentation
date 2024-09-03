Edit cassandra-env.sh, usually located in your Cassandra install path such as: 

`/<Cassandra Installation Directory>/conf/cassandra-env.sh`

Add the following line at the end of the file:

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
  JVM_OPTS="$JVM_OPTS -javaagent:/usr/share/axonops/axon-cassandra5.0-agent.jar=/etc/axonops/axon-agent.yml"
  ```
</div> 