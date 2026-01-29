<p>Insert the following code block into the above file, right before the final line which contains the <code>exec</code> statement:

```shell
# Please note the period(.) at the beginning of the config line.
. /usr/share/axonops/axonops-jvm.options
```

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