
### Select the OS Family. 
<label>
  <input type="radio" id="Debian" name="osFamily" onChange="selectOS()" checked=true />
  <img src="/get_started/debian.png" class="skip-lightbox" width="180px">
</label>
<label>
  <input type="radio" id="RedHat" name="osFamily" onChange="selectOS()" />
  <img src="/get_started/red_hat.png" class="skip-lightbox" width="180px">
</label>

<div id="DebianDiv" class="os">
    ```bash
    wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.17.16-amd64.deb
    wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.17.16-amd64.deb.sha512
    shasum -a 512 -c elasticsearch-7.17.16-amd64.deb.sha512
    sudo dpkg -i elasticsearch-7.17.16-amd64.deb
    ```
    The shasum command above verifies the downloaded package and should show this output:
    ```
    elasticsearch-7.17.16-amd64.deb: OK
    ```
</div>

<div id="RedHatDiv" class="os" style="display:none">
    ```bash
    wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.17.16-x86_64.rpm
    wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.17.16-x86_64.rpm.sha512
    sha512sum -c elasticsearch-7.17.16-x86_64.rpm.sha512
    sudo rpm -i elasticsearch-7.17.16-x86_64.rpm
    ```
    The sha512sum command above verifies the downloaded package and should show this output:
    ```
    elasticsearch-7.17.16-x86_64.rpm: OK
    ```
</div>