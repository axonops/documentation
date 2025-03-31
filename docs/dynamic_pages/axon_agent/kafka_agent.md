

<h3>Select the Kafka Version</h3>
<label>
  <input type="radio" id="Kafka20" name="kafkaFamily" onChange="updateKafka()" checked=true />
  <img src="/get_started/kafka20.png" class="skip-lightbox" width="180px">
</label>
<label>
  <input type="radio" id="Kafka30" name="kafkaFamily" onChange="updateKafka()" />
  <img src="/get_started/kafka30.png" class="skip-lightbox" width="180px">
</label>

<h3>Select the Java Version.</h3>
<label>
  <input type="radio" id="Java" name="kjavaFamily" onChange="updateKJava()" checked=true />
  <img id="Javaimg" src="/get_started/java.png" class="skip-lightbox" width="180px">
</label>

<!-- Debian -->
<div id="DebianKafka20JavaDiv" class="kafka">
  ```
  sudo apt-get install axon-kafka2.0-agent axon-agent
  ```
</div>
<div id="DebianKafka30JavaDiv" class="kafka">
  ```
  sudo apt-get install axon-kafka3.0-agent axon-agent
  ```
</div>
<!-- RedHat -->
<div id="RedHatKafka20JavaDiv" class="kafka" style="display:none">
  ```
  sudo yum install axon-kafka2.0-agent axon-agent
  ```
</div>
<div id="RedHatKafka30JavaDiv" class="kafka" style="display:none">
  ```
  sudo yum install axon-kafka3.0-agent axon-agent
  ```
</div>