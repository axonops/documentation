Change line EXTRA_ARGS to:
<!-- Kafka 2.0 Java 11 -->
<div id="Kafka20JavaDiv" class="javakafka">
<div id="Broker" class="axon_kafka_dynamic_s3">

```shell
  EXTRA_ARGS=${EXTRA_ARGS-'-name kafkaServer -loggc -javaagent:/usr/share/axonops/axon-kafka2.0-agent.jar=/etc/axonops/axon-agent.yml'}
```
</div>
<div id="Zookeeper" class="axon_kafka_dynamic_s3" style="display:none">

```shell
  EXTRA_ARGS=${EXTRA_ARGS-'-name zookeeper -loggc -javaagent:/usr/share/axonops/axon-kafka2.0-agent.jar=/etc/axonops/axon-agent.yml'}
```
</div>
<div id="KRaftBroker" class="axon_kafka_dynamic_s3" style="display:none">

```shell
  EXTRA_ARGS=${EXTRA_ARGS-'-name kafkaServer -loggc -javaagent:/usr/share/axonops/axon-kafka2.0-agent.jar=/etc/axonops/axon-agent.yml'}
```
</div>
<div id="KRaftController" class="axon_kafka_dynamic_s3" style="display:none">

```shell
  EXTRA_ARGS=${EXTRA_ARGS-'-name kafkaServer -loggc -javaagent:/usr/share/axonops/axon-kafka2.0-agent.jar=/etc/axonops/axon-agent.yml'}
```
</div>
<div id="Connect" class="axon_kafka_dynamic_s3" style="display:none">

```shell
  EXTRA_ARGS=${EXTRA_ARGS-'-name connectDistributed -javaagent:/usr/share/axonops/axon-kafka2.0-agent.jar=/etc/axonops/axon-agent.yml'}
```
</div>
</div>
<!-- END Kafka 2.0 Java 11 -->
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
<!-- Kafka 3.0 Java 11 -->
<div id="Kafka30JavaDiv" class="javakafka">
<div id="Broker" class="axon_kafka_dynamic_s6">

```shell
  EXTRA_ARGS=${EXTRA_ARGS-'-name kafkaServer -loggc -javaagent:/usr/share/axonops/axon-kafka3.0-agent.jar=/etc/axonops/axon-agent.yml'}
```
</div>
<div id="Zookeeper" class="axon_kafka_dynamic_s6" style="display:none">

```shell
  EXTRA_ARGS=${EXTRA_ARGS-'-name zookeeper -loggc -javaagent:/usr/share/axonops/axon-kafka3.0-agent.jar=/etc/axonops/axon-agent.yml'}
```
</div>
<div id="KRaftBroker" class="axon_kafka_dynamic_s6" style="display:none">

```shell
  EXTRA_ARGS=${EXTRA_ARGS-'-name kafkaServer -loggc -javaagent:/usr/share/axonops/axon-kafka3.0-agent.jar=/etc/axonops/axon-agent.yml'}
```
</div>
<div id="KRaftController" class="axon_kafka_dynamic_s6" style="display:none">

```shell
  EXTRA_ARGS=${EXTRA_ARGS-'-name kafkaServer -loggc -javaagent:/usr/share/axonops/axon-kafka3.0-agent.jar=/etc/axonops/axon-agent.yml'}
```
</div>
<div id="Connect" class="axon_kafka_dynamic_s6" style="display:none">

```shell
  EXTRA_ARGS=${EXTRA_ARGS-'-name connectDistributed -javaagent:/usr/share/axonops/axon-kafka3.0-agent.jar=/etc/axonops/axon-agent.yml'}
```
</div>
</div>
<!-- END Kafka 3.0 Java 11 -->
<!-- Kafka 3.0 Java 17 -->
<div id="Kafka30Java17Div" class="javakafka">
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