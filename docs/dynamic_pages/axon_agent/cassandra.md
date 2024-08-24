### Select the Cassandra Version
<label>
  <input type="radio" id="Cassandra30" name="casFamily" onChange="updateCas()" checked=true />
  <img src="/get_started/cas_3.png" class="skip-lightbox" width="180px">
</label>
<label>
  <input type="radio" id="Cassandra311" name="casFamily" onChange="updateCas()" />
  <img src="/get_started/cas_3_11.png" class="skip-lightbox" width="180px">
</label>
<label>
  <input type="radio" id="Cassandra40" name="casFamily" onChange="updateCas()" />
  <img src="/get_started/cas_4.png" class="skip-lightbox" width="180px">
</label>
<label>
  <input type="radio" id="Cassandra41" name="casFamily" onChange="updateCas()" />
  <img src="/get_started/cas_4_1.png" class="skip-lightbox" width="180px">
</label>
<label>
  <input type="radio" id="Cassandra50" name="casFamily" onChange="updateCas()" />
  <img src="/get_started/cas_5_0.png" class="skip-lightbox" width="180px">
</label>

### Select the Java Version. 
<label>
  <input type="radio" id="Java8" name="javaFamily" onChange="updateJava()" checked=true />
  <img id="Java8img" src="/get_started/Java_8.png" class="skip-lightbox" width="180px">
</label>
<label>
  <input type="radio" id="Java11" name="javaFamily" onChange="updateJava()" />
  <img id="Java11img" src="/get_started/Java_11.png" class="skip-lightbox" width="180px" style="display:none">
</label>

<!-- Debian -->
<div id="DebianCassandra30Java8Div" class="cas">
  ```
  sudo apt-get install axon-cassandra3.0-agent
  ```
</div>
<div id="DebianCassandra311Java8Div" class="cas" style="display:none">
  ```
  sudo apt-get install axon-cassandra3.11-agent
  ```
</div>
<div id="DebianCassandra40Java8Div" class="cas" style="display:none">
  ```
  sudo apt-get install axon-cassandra4.0-agent-jdk8
  ```
</div>
<div id="DebianCassandra40Java11Div" class="cas" style="display:none">
  ```
  sudo apt-get install axon-cassandra4.0-agent
  ```
</div>
<div id="DebianCassandra41Java8Div" class="cas" style="display:none">
  ```
  sudo apt-get install axon-cassandra4.1-agent-jdk8
  ```
</div>
<div id="DebianCassandra41Java11Div" class="cas" style="display:none">
  ```
  sudo apt-get install axon-cassandra4.1-agent
  ```
</div>
<div id="DebianCassandra50Java11Div" class="cas" style="display:none">
  ```
  sudo apt-get install axon-cassandra5.0-agent-jdk11
  ```
</div>
<!-- RedHat -->
<div id="RedHatCassandra30Java8Div" class="cas" style="display:none">
  ```
  sudo yum install axon-cassandra3.0-agent
  ```
</div>
<div id="RedHatCassandra311Java8Div" class="cas" style="display:none">
  ```
  sudo yum install axon-cassandra3.11-agent
  ```
</div>
<div id="RedHatCassandra40Java8Div" class="cas" style="display:none">
  ```
  sudo yum install axon-cassandra4.0-agent-jdk8
  ```
</div>
<div id="RedHatCassandra40Java11Div" class="cas" style="display:none">
  ```
  sudo yum install axon-cassandra4.0-agent
  ```
</div>
<div id="RedHatCassandra41Java8Div" class="cas" style="display:none">
  ```
  sudo yum install axon-cassandra4.1-agent-jdk8
  ```
</div>
<div id="RedHatCassandra41Java11Div" class="cas" style="display:none">
  ```
  sudo yum install axon-cassandra4.1-agent
  ```
</div>
<div id="RedHatCassandra50Java11Div" class="cas" style="display:none">
  ```
  sudo yum install axon-cassandra5.0-agent-jdk11
  ```
</div>