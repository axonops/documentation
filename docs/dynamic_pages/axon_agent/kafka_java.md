Change line EXTRA_ARGS to:

<div id="Kafka20Div" class="javakafka">
<div id="Broker" class="axon_kafka_dynamic_s3">

```
  EXTRA_ARGS=${EXTRA_ARGS-'-name kafkaServer -loggc -javaagent:/usr/share/axonops/axon-kafka2.0-agent.jar=/etc/axonops/axon-agent.yml'}
```
</div>
<div id="Zookeeper" class="axon_kafka_dynamic_s3" style="display:none">

```
  EXTRA_ARGS=${EXTRA_ARGS-'-name zookeeper -loggc -javaagent:/usr/share/axonops/axon-kafka2.0-agent.jar=/etc/axonops/axon-agent.yml'}
```
</div>
<div id="KRaftBroker" class="axon_kafka_dynamic_s3" style="display:none">

```
  EXTRA_ARGS=${EXTRA_ARGS-'-name kafkaServer -loggc -javaagent:/usr/share/axonops/axon-kafka2.0-agent.jar=/etc/axonops/axon-agent.yml'}
```
</div>
<div id="KRaftController" class="axon_kafka_dynamic_s3" style="display:none">

```
  EXTRA_ARGS=${EXTRA_ARGS-'-name kafkaServer -loggc -javaagent:/usr/share/axonops/axon-kafka2.0-agent.jar=/etc/axonops/axon-agent.yml'}
```
</div>
<div id="Connect" class="axon_kafka_dynamic_s3" style="display:none">

```
  EXTRA_ARGS=${EXTRA_ARGS-'-name connectDistributed -javaagent:/usr/share/axonops/axon-kafka2.0-agent.jar=/etc/axonops/axon-agent.yml'}
```
</div>
</div>
<div id="Kafka30Div" class="javakafka">
<div id="Broker" class="axon_kafka_dynamic_s4">

```shell
  EXTRA_ARGS=${EXTRA_ARGS-'-name kafkaServer -loggc -javaagent:/usr/share/axonops/axon-kafka3.0-agent.jar=/etc/axonops/axon-agent.yml'}
```
</div>
<div id="Zookeeper" class="axon_kafka_dynamic_s4" style="display:none">

```
  EXTRA_ARGS=${EXTRA_ARGS-'-name zookeeper -loggc -javaagent:/usr/share/axonops/axon-kafka3.0-agent.jar=/etc/axonops/axon-agent.yml'}
```
</div>
<div id="KRaftBroker" class="axon_kafka_dynamic_s4" style="display:none">

```
  EXTRA_ARGS=${EXTRA_ARGS-'-name kafkaServer -loggc -javaagent:/usr/share/axonops/axon-kafka3.0-agent.jar=/etc/axonops/axon-agent.yml'}
```
</div>
<div id="KRaftController" class="axon_kafka_dynamic_s4" style="display:none">

```
  EXTRA_ARGS=${EXTRA_ARGS-'-name kafkaServer -loggc -javaagent:/usr/share/axonops/axon-kafka3.0-agent.jar=/etc/axonops/axon-agent.yml'}
```
</div>
<div id="Connect" class="axon_kafka_dynamic_s4" style="display:none">

```
  EXTRA_ARGS=${EXTRA_ARGS-'-name connectDistributed -javaagent:/usr/share/axonops/axon-kafka3.0-agent.jar=/etc/axonops/axon-agent.yml'}
```
</div>

</div>