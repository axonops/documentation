### Select the Cassandra Version

<label>
  <input type="radio" id="Cassandra30" name="casFamily" onChange="selectCas()" checked=true />
  <img src="/get_started/cas_3.png" class="skip-lightbox" width="180px" alt="cas_3">
</label>
<label>
  <input type="radio" id="Cassandra311" name="casFamily" onChange="selectCas()" />
  <img src="/get_started/cas_3_11.png" class="skip-lightbox" width="180px" alt="cas_3_11">
</label>
<label>
  <input type="radio" id="Cassandra40" name="casFamily" onChange="selectCas()" />
  <img src="/get_started/cas_4.png" class="skip-lightbox" width="180px" alt="cas_4">
</label>
<label>
  <input type="radio" id="Cassandra41" name="casFamily" onChange="selectCas()" />
  <img src="/get_started/cas_4_1.png" class="skip-lightbox" width="180px" alt="cas_4_1">
</label>
<label>
  <input type="radio" id="Cassandra50" name="casFamily" onChange="selectCas()" />
  <img src="/get_started/cas_5_0.png" class="skip-lightbox" width="180px" alt="cas_5_0">
</label>

### Select the Java Version

<label>
  <input type="radio" id="Java8" name="javaFamily" onChange="selectJava()" checked=true />
  <img id="Java8img" src="/get_started/Java_8.png" class="skip-lightbox" width="180px" alt="Java_8">
</label>
<label>
  <input type="radio" id="Java11" name="javaFamily" onChange="selectJava()" />
  <img id="Java11img" src="/get_started/Java_11.png" class="skip-lightbox" width="180px" style="display:none" alt="Java_11">
</label>
<label>
  <input type="radio" id="Java17" name="javaFamily" onChange="selectJava()" />
  <img id="Java17img" src="/get_started/Java_17.png" class="skip-lightbox" width="180px" style="display:none" alt="Java_17">
</label>

Install the AxonOps Cassandra Agent and its dependency `AxonOps agent`:

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
<div id="DebianCassandra50Java17Div" class="cas" style="display:none">
  ```
  sudo apt-get install axon-cassandra5.0-agent-jdk17
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
<div id="RedHatCassandra50Java17Div" class="cas" style="display:none">
  ```
  sudo yum install axon-cassandra5.0-agent-jdk17
  ```
</div>

### Configuration File Locations

#### AxonOps Cassandra Agent

The AxonOps Cassandra Agent is the jar that is directly loaded by Cassandra.
The AxonOps Cassandra Agent then reaches out directly to the AxonOps Agent binary
which contacts the AxonOps Server directly.

- Configuration File: `/etc/axonops/axon-agent.yml`
- Binary: `/usr/share/axonops/axon-cassandra{version}-agent.jar`
- Version number: `/usr/share/axonops/axon-cassandra{version}-agent.version`
- Copyright: `/usr/share/doc/axonops/axon-cassandra{version}-agent/copyright`
- Licenses: `/usr/share/axonops/licenses/axon-cassandra{version}-agent/`


#### AxonOps Agent

The AxonOps Agent is a dependency of the AxonOps Cassandra Agent. This binary
contacts the AxonOps Server directly while minimizing the memory footprint
and CPU utilization of the Cassandra process.

- Configuration File: `/etc/axonops/axon-agent.yml`
- Binary: `usr/share/axonops/AxonOps agent`
- Logs: `/var/log/axonops/AxonOps agent.log`
- Systemd service: `/usr/lib/systemd/system/AxonOps agent.service`