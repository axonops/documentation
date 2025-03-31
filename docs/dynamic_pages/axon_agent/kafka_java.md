Edit kafka-server-start.sh, usually located in your Kafka install path such as: 

<p><code>/&lt;Kafka_Home&gt;/bin/kafka-server-start.sh</code></p>

Change line EXTRA_ARGS to:

<div id="Kafka20Div" class="javakafka">
  ```
  EXTRA_ARGS=${EXTRA_ARGS-'-name kafkaServer -loggc -javaagent:/usr/share/axonops/axon-kafka2.0-agent.jar=/etc/axonops/axon-agent.yml'}
  ```
</div>
<div id="Kafka30Div" class="javakafka">
  ```
  EXTRA_ARGS=${EXTRA_ARGS-'-name kafkaServer -loggc -javaagent:/usr/share/axonops/axon-kafka3.0-agent.jar=/etc/axonops/axon-agent.yml'}
  ```
</div>