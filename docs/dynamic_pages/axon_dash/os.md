Select the OS Family

<label>
  <input type="radio" id="Debian" name="osFamily" onChange="selectOS()" checked=true />
  <img src="/get_started/debian.png" class="skip-lightbox" width="180px">
</label>
<label>
  <input type="radio" id="RedHat" name="osFamily" onChange="selectOS()" />
  <img src="/get_started/red_hat.png" class="skip-lightbox" width="180px">
</label>

Execute the following commands to setup the AxonOps GUI for your OS:

<div id="DebianDiv" class="os">

    ```bash
    sudo apt-get update
    sudo apt-get install -y curl gnupg ca-certificates

    curl -L https://packages.axonops.com/apt/repo-signing-key.gpg \
      | sudo gpg --dearmor -o /usr/share/keyrings/axonops.gpg

    echo "deb [arch=arm64,amd64 signed-by=/usr/share/keyrings/axonops.gpg]\
     https://packages.axonops.com/apt axonops-apt main" \
      | sudo tee /etc/apt/sources.list.d/axonops-apt.list
    sudo apt-get update

    sudo apt-get install axon-dash
    ```

</div>

<div id="RedHatDiv" class="os" style="display:none">

    ```bash
    sudo tee /etc/yum.repos.d/axonops-yum.repo << EOL
    [axonops-yum]
    name=axonops-yum
    baseurl=https://packages.axonops.com/yum/
    enabled=1
    repo_gpgcheck=0
    gpgcheck=0
    EOL

    sudo yum install axon-dash
    ```

</div>