
# Installing on Debian / Ubuntu


##  Java Agent Installation

<table style="white-space: nowrap;">
  <thead>
    <tr>
      <th colspan="2">Description</td>
      <th colspan="2">Download</td>
    </tr>
  </thead>
  <tbody>
   
    <tr>
      <td  colspan="3" align="left">Stable for Debian-based Linux</td>
      <td colspan="1" align="right">
        <a href="#">x86-64</a>
      </td>
    </tr>
    <tr>
      <td colspan="3" align="left">Stable for Debian-based Linux</td>
      <td colspan="1" align="right">
        <a href="#">ARM64</a>
      </td>
    </tr>
    <tr>
      <td colspan="3" align="left">Stable for Debian-based Linux</td>
      <td colspan="1" align="right">
        <a href="#">ARMv7</a>
      </td>
    </tr>
  </tbody>
</table>


### Install Stable

Before installing [java agent][1], you need to make sure you have ... and ... – ... up and running. You can verify if you're already good to go with the following commands:

[1]: https://axonops.com

``` sh
.. --version
# ... 2.7.13
... --version
# ... 9.0.1
```

Installing and verifying java agent is as simple as:

``` debcontrol
wget <debian package url>
sudo apt-get install -y adduser libfontconfig
sudo dpkg -i java_agent<version>_amd64.deb
```

Example

``` debcontrol
wget https://url/dl.java_agent.4.2_amd64.deb
sudo apt-get install -y adduser libfontconfig
sudo dpkg -i java_agent_5.4.2_amd64.deb
```
  

### APT Repository


Create a file `/etc/apt/sources.list.d/java_agent.list` and add the following to it.

``` debcontrol
deb https://packages.axonops.java_agent.com/oss/deb stable main
```

There is a separate repository if you want beta releases.

``` debcontrol
deb https://packages.axonops.java_agent.com/oss/deb beta main
```

Use the above line even if you are on Ubuntu or another Debian version. Then add our gpg key. This allows you to install signed packages.

``` debcontrol 
curl https://packages.axonops.java_agent.com/gpg.key | sudo apt-key add -
```

Update your Apt repositories and install agent

``` debcontrol 
sudo apt-get update
sudo apt-get install axonops_java_agent
```

On some older versions of Ubuntu and Debian you may need to install the apt-transport-https package which is needed to fetch packages over HTTPS.

``` extempore 
sudo apt-get install -y apt-transport-https
```

### Cloning from GitHub

AxonOps Server can also be used without a system-wide installation by cloning the repository into a subfolder of your project's root directory:

``` extempore
git clone https://github.com/squidfunk/axonops.git
```

This is especially useful if you want to extend the app and
override some parts of the app. The app will reside in the folder
`path-to/folder`.


### Package details

* Installs binary to ` /usr/sbin/java-agent `
* Installs Init.d script to `/etc/init.d/java-agent `
* Creates default file (environment vars) to ` /etc/default/java-agent` 
* Installs configuration file to ` /etc/java_agent/java_agent.ini `
* Installs systemd service (if systemd is available) name ` java-server.agent` 
* The default configuration sets the log file at ` /var/log/java_agent/java_agent.log` 


###  Using Docker

If you're familiar with Docker, the official [Docker image][8] for Material
comes with all dependencies pre-installed and ready-to-use with the latest
version published on PyPI, packaged in a very small image. Pull it with:

``` docker
docker pull squidfunk/mkdocs-material
```

The `axonops` executable is provided as an entrypoint, `serve` is the default
command. Start the development server in your project root with:

``` docker
docker run --rm -it -p 8000:8000 -v ${PWD}:/docs squidfunk/mkdocs-material
```

If you're using Windows command prompt (`cmd.exe`), substitute `${PWD}` with
`"%cd%"`.

  [8]: https://hub.docker.com/r/squidfunk/mkdocs-material/

### Start the server (init.d service)

 <small>Start Java Agent by running:</small>

``` extempore
 sudo service java-server start
```
This will start the `java-server` process as the java-server user, which was created during the package installation. 

To configure the java server to start at boot time:

``` extempore
sudo update-rc.d java-agent defaults
```

### Start the Java Agent (init.d service)

To start the service using systemd:

``` debcontrol
systemctl daemon-reload
systemctl start java-agent
systemctl status java-agent
```

Enable the systemd service so that java agent starts at boot.

``` extempore
sudo systemctl enable java-agent.service
```

### Environment file
The systemd service file and init.d script both use the file located at ` /etc/default/java-agent ` for environment variables used when starting the agent. Here you can override log directory, data directory and other variables.

### Logging
By default Java Agent will log to /var/log/java_agent





##  Axonops Agent Installation


<table style="white-space: nowrap;">
  <thead>
    <tr>
      <th colspan="2">Description</td>
      <th colspan="2">Download</td>
    </tr>
  </thead>
  <tbody>
   
    <tr>
      <td  colspan="3" align="left">Stable for Debian-based Linux</td>
      <td colspan="1" align="right">
        <a href="#">x86-64</a>
      </td>
    </tr>
    <tr>
      <td colspan="3" align="left">Stable for Debian-based Linux</td>
      <td colspan="1" align="right">
        <a href="#">ARM64</a>
      </td>
    </tr>
    <tr>
      <td colspan="3" align="left">Stable for Debian-based Linux</td>
      <td colspan="1" align="right">
        <a href="#">ARMv7</a>
      </td>
    </tr>
  </tbody>
</table>


### Install Stable

Before installing [axon-agent][9], you need to make sure you have ... and ... – ... up and running. You can verify if you're already good to go with the following commands:

[9]: https://axonops.com

``` sh
.. --version
# ... 2.7.13
... --version
# ... 9.0.1
```

Installing and verifying axon-agent:

``` debcontrol
wget <debian package url>
sudo apt-get install -y adduser libfontconfig
sudo dpkg -i axon-agent<version>_amd64.deb
```

Example

``` debcontrol
wget https://url/dl.axon-agent.4.2_amd64.deb
sudo apt-get install -y adduser libfontconfig
sudo dpkg -i axon-agent.4.2_amd64.deb
```
  

### APT Repository


Create a file `/etc/apt/sources.list.d/axon-agent.list` and add the following to it.

``` debcontrol
deb https://packages.axonops.axon-agent.com/oss/deb stable main
```

There is a separate repository if you want beta releases.

``` debcontrol
deb https://packages.axonops.axon-agent.com/oss/deb beta main
```

Use the above line even if you are on Ubuntu or another Debian version. Then add our gpg key. This allows you to install signed packages.

``` debcontrol 
curl https://packages.axonops.axon-agent.com/gpg.key | sudo apt-key add -
```

Update your Apt repositories and install agent

``` debcontrol 
sudo apt-get update
sudo apt-get install axonops_axon-agent
```

On some older versions of Ubuntu and Debian you may need to install the apt-transport-https package which is needed to fetch packages over HTTPS.

``` extempore 
sudo apt-get install -y apt-transport-https
```

### Cloning from GitHub

Node Server can also be used without a system-wide installation by cloning the repository into a subfolder of your project's root directory:

``` extempore
git clone https://github.com/squidfunk/axon-agent.git
```

This is especially useful if you want to extend the app and
override some parts of the app. The app will reside in the folder
`path-to/folder`.


### Package details

* Installs binary to ` /usr/sbin/axon-agent `
* Installs Init.d script to `/etc/init.d/axon-agent `
* Creates default file (environment vars) to ` /etc/default/axon-agent` 
* Installs configuration file to ` /etc/java_agent/axon-agent.ini `
* Installs systemd service (if systemd is available) name ` node-server.agent` 
* The default configuration sets the log file at ` /var/log/axon-agent/axon-agent.log` 


###  Using Docker

If you're familiar with Docker, the official [Docker image][10] for Material
comes with all dependencies pre-installed and ready-to-use with the latest
version published on PyPI, packaged in a very small image. Pull it with:

  [10]: https://hub.docker.com/r/squidfunk/mkdocs-material/

``` docker
docker pull squidfunk/mkdocs-material
```

The `axonops` executable is provided as an entrypoint, `serve` is the default
command. Start the development server in your project root with:

``` docker
docker run --rm -it -p 8000:8000 -v ${PWD}:/docs squidfunk/mkdocs-material
```

If you're using Windows command prompt (`cmd.exe`), substitute `${PWD}` with
`"%cd%"`.



### Start the server (init.d service)

 <small>Start Node Agent by running:</small>

``` extempore
 sudo service node-server start
```
This will start the `node-server` process as the node-server user, which was created during the package installation. 

To configure the node server to start at boot time:

``` extempore
sudo update-rc.d axon-agent defaults
```

### Start the Node Agent (init.d service)

To start the service using systemd:

``` debcontrol
systemctl daemon-reload
systemctl start axon-agent
systemctl status axon-agent
```

Enable the systemd service so that axon-agent starts at boot.

``` extempore
sudo systemctl enable axon-agent.service
```

### Environment file
The systemd service file and init.d script both use the file located at ` /etc/default/axon-agent ` for environment variables used when starting the agent. Here you can override log directory, data directory and other variables.

### Logging
By default Java Agent will log to /var/log/axon-agent