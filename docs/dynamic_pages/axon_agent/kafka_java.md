<p>Insert the following two code blocks into the above file, right before the final line which contains the <code>exec</code> statement:

```shell
# Please note the period(.) at the beginning of the config line.
. /usr/share/axonops/axonops-jvm.options
```

<!-- Kafka 2.0 Java 17 -->
<div id="Kafka20Java17Div" class="javakafka">
<div id="Broker" class="axon_kafka_dynamic_s4">

```shell
  EXTRA_ARGS=${EXTRA_ARGS-'-name kafkaServer -loggc -javaagent:/usr/share/axonops/axon-kafka2.0-agent.jar=/etc/axonops/axon-agent.yml --add-exports=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/sun.nio.ch=ALL-UNNAMED --add-exports=jdk.unsupported/sun.misc=ALL-UNNAMED --add-exports=jdk.compiler/com.sun.tools.javac.tree=ALL-UNNAMED  --add-exports=jdk.compiler/com.sun.tools.javac.code=ALL-UNNAMED  --add-exports=jdk.compiler/com.sun.tools.javac.util=ALL-UNNAMED --add-opens=java.management/com.sun.jmx.mbeanserver=ALL-UNNAMED --add-exports=java.management/com.sun.jmx.mbeanserver=ALL-UNNAMED --add-opens=java.management/com.sun.jmx.interceptor=ALL-UNNAMED --add-exports=java.management/com.sun.jmx.interceptor=ALL-UNNAMED'}
```
</div>
<div id="Zookeeper" class="axon_kafka_dynamic_s4" style="display:none">

```shell
  EXTRA_ARGS=${EXTRA_ARGS-'-name zookeeper -loggc -javaagent:/usr/share/axonops/axon-kafka2.0-agent.jar=/etc/axonops/axon-agent.yml --add-exports=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/sun.nio.ch=ALL-UNNAMED --add-exports=jdk.unsupported/sun.misc=ALL-UNNAMED --add-exports=jdk.compiler/com.sun.tools.javac.tree=ALL-UNNAMED  --add-exports=jdk.compiler/com.sun.tools.javac.code=ALL-UNNAMED  --add-exports=jdk.compiler/com.sun.tools.javac.util=ALL-UNNAMED --add-opens=java.management/com.sun.jmx.mbeanserver=ALL-UNNAMED --add-exports=java.management/com.sun.jmx.mbeanserver=ALL-UNNAMED --add-opens=java.management/com.sun.jmx.interceptor=ALL-UNNAMED --add-exports=java.management/com.sun.jmx.interceptor=ALL-UNNAMED'}
```
</div>
<div id="KRaftBroker" class="axon_kafka_dynamic_s4" style="display:none">

```shell
  EXTRA_ARGS=${EXTRA_ARGS-'-name kafkaServer -loggc -javaagent:/usr/share/axonops/axon-kafka2.0-agent.jar=/etc/axonops/axon-agent.yml --add-exports=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/sun.nio.ch=ALL-UNNAMED --add-exports=jdk.unsupported/sun.misc=ALL-UNNAMED --add-exports=jdk.compiler/com.sun.tools.javac.tree=ALL-UNNAMED  --add-exports=jdk.compiler/com.sun.tools.javac.code=ALL-UNNAMED  --add-exports=jdk.compiler/com.sun.tools.javac.util=ALL-UNNAMED --add-opens=java.management/com.sun.jmx.mbeanserver=ALL-UNNAMED --add-exports=java.management/com.sun.jmx.mbeanserver=ALL-UNNAMED --add-opens=java.management/com.sun.jmx.interceptor=ALL-UNNAMED --add-exports=java.management/com.sun.jmx.interceptor=ALL-UNNAMED'}
```
</div>
<div id="KRaftController" class="axon_kafka_dynamic_s4" style="display:none">

```shell
  EXTRA_ARGS=${EXTRA_ARGS-'-name kafkaServer -loggc -javaagent:/usr/share/axonops/axon-kafka2.0-agent.jar=/etc/axonops/axon-agent.yml --add-exports=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/sun.nio.ch=ALL-UNNAMED --add-exports=jdk.unsupported/sun.misc=ALL-UNNAMED --add-exports=jdk.compiler/com.sun.tools.javac.tree=ALL-UNNAMED  --add-exports=jdk.compiler/com.sun.tools.javac.code=ALL-UNNAMED  --add-exports=jdk.compiler/com.sun.tools.javac.util=ALL-UNNAMED --add-opens=java.management/com.sun.jmx.mbeanserver=ALL-UNNAMED --add-exports=java.management/com.sun.jmx.mbeanserver=ALL-UNNAMED --add-opens=java.management/com.sun.jmx.interceptor=ALL-UNNAMED --add-exports=java.management/com.sun.jmx.interceptor=ALL-UNNAMED'}
```
</div>
<div id="Connect" class="axon_kafka_dynamic_s4" style="display:none">

```shell
  EXTRA_ARGS=${EXTRA_ARGS-'-name connectDistributed -javaagent:/usr/share/axonops/axon-kafka2.0-agent.jar=/etc/axonops/axon-agent.yml --add-exports=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/sun.nio.ch=ALL-UNNAMED --add-exports=jdk.unsupported/sun.misc=ALL-UNNAMED --add-exports=jdk.compiler/com.sun.tools.javac.tree=ALL-UNNAMED  --add-exports=jdk.compiler/com.sun.tools.javac.code=ALL-UNNAMED  --add-exports=jdk.compiler/com.sun.tools.javac.util=ALL-UNNAMED --add-opens=java.management/com.sun.jmx.mbeanserver=ALL-UNNAMED --add-exports=java.management/com.sun.jmx.mbeanserver=ALL-UNNAMED --add-opens=java.management/com.sun.jmx.interceptor=ALL-UNNAMED --add-exports=java.management/com.sun.jmx.interceptor=ALL-UNNAMED'}
```
</div>
</div>
<!-- END Kafka 2.0 Java 17 -->
<!-- Kafka 3.0 Java 17 -->
<div id="Kafka30Java17Div" class="javakafka" style="display:none">
<div id="Broker" class="axon_kafka_dynamic_s7">

```shell
  EXTRA_ARGS=${EXTRA_ARGS-'-name kafkaServer -loggc -javaagent:/usr/share/axonops/axon-kafka3.0-agent.jar=/etc/axonops/axon-agent.yml --add-exports=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/sun.nio.ch=ALL-UNNAMED --add-exports=jdk.unsupported/sun.misc=ALL-UNNAMED --add-exports=jdk.compiler/com.sun.tools.javac.tree=ALL-UNNAMED  --add-exports=jdk.compiler/com.sun.tools.javac.code=ALL-UNNAMED  --add-exports=jdk.compiler/com.sun.tools.javac.util=ALL-UNNAMED --add-opens=java.management/com.sun.jmx.mbeanserver=ALL-UNNAMED --add-exports=java.management/com.sun.jmx.mbeanserver=ALL-UNNAMED --add-opens=java.management/com.sun.jmx.interceptor=ALL-UNNAMED --add-exports=java.management/com.sun.jmx.interceptor=ALL-UNNAMED'}
```
</div>
<div id="Zookeeper" class="axon_kafka_dynamic_s7" style="display:none">

```shell
  EXTRA_ARGS=${EXTRA_ARGS-'-name zookeeper -loggc -javaagent:/usr/share/axonops/axon-kafka3.0-agent.jar=/etc/axonops/axon-agent.yml --add-exports=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/sun.nio.ch=ALL-UNNAMED --add-exports=jdk.unsupported/sun.misc=ALL-UNNAMED --add-exports=jdk.compiler/com.sun.tools.javac.tree=ALL-UNNAMED  --add-exports=jdk.compiler/com.sun.tools.javac.code=ALL-UNNAMED  --add-exports=jdk.compiler/com.sun.tools.javac.util=ALL-UNNAMED --add-opens=java.management/com.sun.jmx.mbeanserver=ALL-UNNAMED --add-exports=java.management/com.sun.jmx.mbeanserver=ALL-UNNAMED --add-opens=java.management/com.sun.jmx.interceptor=ALL-UNNAMED --add-exports=java.management/com.sun.jmx.interceptor=ALL-UNNAMED'}
```
</div>
<div id="KRaftBroker" class="axon_kafka_dynamic_s7" style="display:none">

```shell
  EXTRA_ARGS=${EXTRA_ARGS-'-name kafkaServer -loggc -javaagent:/usr/share/axonops/axon-kafka3.0-agent.jar=/etc/axonops/axon-agent.yml --add-exports=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/sun.nio.ch=ALL-UNNAMED --add-exports=jdk.unsupported/sun.misc=ALL-UNNAMED --add-exports=jdk.compiler/com.sun.tools.javac.tree=ALL-UNNAMED  --add-exports=jdk.compiler/com.sun.tools.javac.code=ALL-UNNAMED  --add-exports=jdk.compiler/com.sun.tools.javac.util=ALL-UNNAMED --add-opens=java.management/com.sun.jmx.mbeanserver=ALL-UNNAMED --add-exports=java.management/com.sun.jmx.mbeanserver=ALL-UNNAMED --add-opens=java.management/com.sun.jmx.interceptor=ALL-UNNAMED --add-exports=java.management/com.sun.jmx.interceptor=ALL-UNNAMED'}
```
</div>
<div id="KRaftController" class="axon_kafka_dynamic_s7" style="display:none">

```shell
  EXTRA_ARGS=${EXTRA_ARGS-'-name kafkaServer -loggc -javaagent:/usr/share/axonops/axon-kafka3.0-agent.jar=/etc/axonops/axon-agent.yml --add-exports=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/sun.nio.ch=ALL-UNNAMED --add-exports=jdk.unsupported/sun.misc=ALL-UNNAMED --add-exports=jdk.compiler/com.sun.tools.javac.tree=ALL-UNNAMED  --add-exports=jdk.compiler/com.sun.tools.javac.code=ALL-UNNAMED  --add-exports=jdk.compiler/com.sun.tools.javac.util=ALL-UNNAMED --add-opens=java.management/com.sun.jmx.mbeanserver=ALL-UNNAMED --add-exports=java.management/com.sun.jmx.mbeanserver=ALL-UNNAMED --add-opens=java.management/com.sun.jmx.interceptor=ALL-UNNAMED --add-exports=java.management/com.sun.jmx.interceptor=ALL-UNNAMED'}
```
</div>
<div id="Connect" class="axon_kafka_dynamic_s7" style="display:none">

```shell
  EXTRA_ARGS=${EXTRA_ARGS-'-name connectDistributed -javaagent:/usr/share/axonops/axon-kafka3.0-agent.jar=/etc/axonops/axon-agent.yml --add-exports=java.base/sun.nio.ch=ALL-UNNAMED --add-opens=java.base/sun.nio.ch=ALL-UNNAMED --add-exports=jdk.unsupported/sun.misc=ALL-UNNAMED --add-exports=jdk.compiler/com.sun.tools.javac.tree=ALL-UNNAMED  --add-exports=jdk.compiler/com.sun.tools.javac.code=ALL-UNNAMED  --add-exports=jdk.compiler/com.sun.tools.javac.util=ALL-UNNAMED --add-opens=java.management/com.sun.jmx.mbeanserver=ALL-UNNAMED --add-exports=java.management/com.sun.jmx.mbeanserver=ALL-UNNAMED --add-opens=java.management/com.sun.jmx.interceptor=ALL-UNNAMED --add-exports=java.management/com.sun.jmx.interceptor=ALL-UNNAMED'}
```
</div>
</div>
<!-- END Kafka 3.0 Java 17 -->

The final state of the last lines of the file should look like this:

<!-- Kafka 2.0 Java 11 -->
<div id="Kafka20JavaDiv" class="javakafka">
<div id="Broker" class="axon_kafka_dynamic_s3">

```shell hl_lines="1"
. /usr/share/axonops/axonops-jvm.options

exec $base_dir/kafka-run-class.sh $EXTRA_ARGS kafka.Kafka "$@"
```
</div>
<div id="Zookeeper" class="axon_kafka_dynamic_s3" style="display:none">

```shell hl_lines="1"
. /usr/share/axonops/axonops-jvm.options

exec $base_dir/kafka-run-class.sh $EXTRA_ARGS org.apache.zookeeper.server.quorum.QuorumPeerMain "$@"
```
</div>
<div id="KRaftBroker" class="axon_kafka_dynamic_s3" style="display:none">

```shell hl_lines="1"
. /usr/share/axonops/axonops-jvm.options

exec $base_dir/kafka-run-class.sh $EXTRA_ARGS kafka.Kafka "$@"
```
</div>
<div id="KRaftController" class="axon_kafka_dynamic_s3" style="display:none">

```shell hl_lines="1"
. /usr/share/axonops/axonops-jvm.options

exec $base_dir/kafka-run-class.sh $EXTRA_ARGS kafka.Kafka "$@"
```
</div>
<div id="Connect" class="axon_kafka_dynamic_s3" style="display:none">

```shell hl_lines="1"
. /usr/share/axonops/axonops-jvm.options

exec $(dirname $0)/kafka-run-class.sh $EXTRA_ARGS org.apache.kafka.connect.cli.ConnectDistributed "$@"
```
</div>
</div>
<!-- END Kafka 2.0 Java 11 -->


<!-- Kafka 3.0 Java 11 -->
<div id="Kafka30JavaDiv" class="javakafka">
<div id="Broker" class="axon_kafka_dynamic_s6">

```shell hl_lines="1"
. /usr/share/axonops/axonops-jvm.options

exec $base_dir/kafka-run-class.sh $EXTRA_ARGS kafka.Kafka "$@"
```
</div>
<div id="Zookeeper" class="axon_kafka_dynamic_s6" style="display:none">

```shell hl_lines="1"
. /usr/share/axonops/axonops-jvm.options

exec $base_dir/kafka-run-class.sh $EXTRA_ARGS org.apache.zookeeper.server.quorum.QuorumPeerMain "$@"
```
</div>
<div id="KRaftBroker" class="axon_kafka_dynamic_s6" style="display:none">

```shell hl_lines="1"
. /usr/share/axonops/axonops-jvm.options

exec $base_dir/kafka-run-class.sh $EXTRA_ARGS kafka.Kafka "$@"
```
</div>
<div id="KRaftController" class="axon_kafka_dynamic_s6" style="display:none">

```shell hl_lines="1"
. /usr/share/axonops/axonops-jvm.options

exec $base_dir/kafka-run-class.sh $EXTRA_ARGS kafka.Kafka "$@"
```
</div>
<div id="Connect" class="axon_kafka_dynamic_s6" style="display:none">

```shell hl_lines="1"
. /usr/share/axonops/axonops-jvm.options

exec $(dirname $0)/kafka-run-class.sh $EXTRA_ARGS org.apache.kafka.connect.cli.ConnectDistributed "$@"
```
</div>
</div>
<!-- END Kafka 3.0 Java 11 -->
