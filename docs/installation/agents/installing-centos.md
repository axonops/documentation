
# Installing on RPM-based Linux (CentOS, Fedora, OpenSuse, RedHat)


##  Java Agent Installation

<table style="white-space: nowrap;">
  <thead>
    <tr>
      <th colspan="3">Description</td>
      <th colspan="1">Download</td>
    </tr>
  </thead>
  <tbody>
   
    <tr>
      <td  colspan="3" align="left">Stable for CentOS / Fedora / OpenSuse / Redhat Linux</td>
      <td colspan="1" align="right">
        <a href="#">x86-64</a>
      </td>
    </tr>
    <tr>
      <td colspan="3" align="left">Stable for CentOS / Fedora / OpenSuse / Redhat Linux</td>
      <td colspan="1" align="right">
        <a href="#">ARM64</a>
      </td>
    </tr>
    <tr>
      <td colspan="3" align="left">Stable for CentOS / Fedora / OpenSuse / Redhat Linux</td>
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
 sudo yum install <rpm package url>

```

Example:

``` debcontrol
 sudo yum install https://dl.java-agent.com/oss/release/java-agent-5.4.2-1.x86_64.rpm

```
Or install manually using rpm. First execute
``` debcontrol
 wget <rpm package url>

```
Example:

``` debcontrol
wget https://dl.java-agent.com/oss/release/java-agent-5.4.2-1.x86_64.rpm

```

#### On CentOS / Fedora / Redhat:

``` debcontrol
 sudo yum install initscripts fontconfig
 sudo rpm -Uvh <local rpm package>

```

#### On OpenSuse:

``` debcontrol
sudo rpm -i --nodeps <local rpm package>

```
#### Install via YUM Repository

Add the following to a new file at ` /etc/yum.repos.d/axonops.repo `

``` debcontrol
[java-agent]
name=axonagent
baseurl=https://packages.javaagent.com/oss/rpm
repo_gpgcheck=1
enabled=1
gpgcheck=1
gpgkey=https://packages.javaagent.com/gpg.key
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt

```

There is a separate repository if you want beta releases.

``` debcontrol
[java-agent]
name=axonagent
baseurl=https://packages.javaagent.com/oss/rpm-beta
repo_gpgcheck=1
enabled=1
gpgcheck=1
gpgkey=https://packages.javaagent.com/gpg.key
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt

```
Then install Grafana via the yum command.

``` debcontrol
sudo yum install java-agent
```


### RPM GPG Key

The RPMs are signed, you can verify the signature with this [public GPG key][1].
[1]:https://#

Create a file `/etc/apt/sources.list.d/java_agent.list` and add the following to it.


### Cloning from GitHub

Java agent can also be used without a system-wide installation by cloning the repository into a subfolder of your project's root directory:

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
* Installs systemd service (if systemd is available) name ` java-agent.agent` 
* The default configuration sets the log file at ` /var/log/java_agent/java_agent.log` 


###  Using Docker

If you're familiar with Docker, the official [Docker image][2] for Material
comes with all dependencies pre-installed and ready-to-use with the latest
version published on PyPI, packaged in a very small image. Pull it with:

``` docker
docker pull squidfunk/mkdocs-material
```

The `axonops` executable is provided as an entrypoint, `serve` is the default
command. Start the development agent in your project root with:

``` docker
docker run --rm -it -p 8000:8000 -v ${PWD}:/docs squidfunk/mkdocs-material
```

If you're using Windows command prompt (`cmd.exe`), substitute `${PWD}` with
`"%cd%"`.

  [2]: https://hub.docker.com/r/squidfunk/mkdocs-material/

### Start the agent (init.d service)

 <small>Start Java Agent by running:</small>

``` extempore
 sudo service java-agent start
```
This will start the `java-agent` process as the java-agent user, which was created during the package installation. 

To configure the java agent to start at boot time:

``` extempore
sudo /sbin/chkconfig --add java-agent
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




##  Axon Agent Installation

<table style="white-space: nowrap;">
  <thead>
    <tr>
      <th colspan="3">Description</td>
      <th colspan="1">Download</td>
    </tr>
  </thead>
  <tbody>
   
    <tr>
      <td  colspan="3" align="left">Stable for CentOS / Fedora / OpenSuse / Redhat Linux</td>
      <td colspan="1" align="right">
        <a href="#">x86-64</a>
      </td>
    </tr>
    <tr>
      <td colspan="3" align="left">Stable for CentOS / Fedora / OpenSuse / Redhat Linux</td>
      <td colspan="1" align="right">
        <a href="#">ARM64</a>
      </td>
    </tr>
    <tr>
      <td colspan="3" align="left">Stable for CentOS / Fedora / OpenSuse / Redhat Linux</td>
      <td colspan="1" align="right">
        <a href="#">ARMv7</a>
      </td>
    </tr>
  </tbody>
</table>


### Install Stable

Before installing [axon agent][2], you need to make sure you have ... and ... – ... up and running. You can verify if you're already good to go with the following commands:

[2]: https://axonops.com

``` sh
.. --version
# ... 2.7.13
... --version
# ... 9.0.1
```

Installing and verifying axon agent is as simple as:

``` debcontrol
 sudo yum install <rpm package url>

```

Example:

``` debcontrol
 sudo yum install https://dl.axon-agent.com/oss/release/axon-agent-5.4.2-1.x86_64.rpm

```
Or install manually using rpm. First execute
``` debcontrol
 wget <rpm package url>

```
Example:

``` debcontrol
wget https://dl.axon-agent.com/oss/release/axon-agent-5.4.2-1.x86_64.rpm

```

#### On CentOS / Fedora / Redhat:

``` debcontrol
 sudo yum install initscripts fontconfig
 sudo rpm -Uvh <local rpm package>

```

#### On OpenSuse:

``` debcontrol
sudo rpm -i --nodeps <local rpm package>

```
#### Install via YUM Repository

Add the following to a new file at ` /etc/yum.repos.d/axonops.repo `

``` debcontrol
[axon-agent]
name=axonagent
baseurl=https://packages.axonagent.com/oss/rpm
repo_gpgcheck=1
enabled=1
gpgcheck=1
gpgkey=https://packages.axonagent.com/gpg.key
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt

```

There is a separate repository if you want beta releases.

``` debcontrol
[axon-agent]
name=axonagent
baseurl=https://packages.axonagent.com/oss/rpm-beta
repo_gpgcheck=1
enabled=1
gpgcheck=1
gpgkey=https://packages.axonagent.com/gpg.key
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt

```
Then install Grafana via the yum command.

``` debcontrol
sudo yum install axon-agent
```


### RPM GPG Key

The RPMs are signed, you can verify the signature with this [public GPG key][3].
[3]:https://#

Create a file `/etc/apt/sources.list.d/axon_agent.list` and add the following to it.


### Cloning from GitHub

Axon agent can also be used without a system-wide installation by cloning the repository into a subfolder of your project's root directory:

``` extempore
git clone https://github.com/squidfunk/axonops.git
```

This is especially useful if you want to extend the app and
override some parts of the app. The app will reside in the folder
`path-to/folder`.


### Package details

* Installs binary to ` /usr/sbin/axon-agent `
* Installs Init.d script to `/etc/init.d/axon-agent `
* Creates default file (environment vars) to ` /etc/default/axon-agent` 
* Installs configuration file to ` /etc/axon_agent/axon_agent.ini `
* Installs systemd service (if systemd is available) name ` axon-agent.agent` 
* The default configuration sets the log file at ` /var/log/axon_agent/axon_agent.log` 


###  Using Docker

If you're familiar with Docker, the official [Docker image][4] for Material
comes with all dependencies pre-installed and ready-to-use with the latest
version published on PyPI, packaged in a very small image. Pull it with:

``` docker
docker pull squidfunk/mkdocs-material
```

The `axonops` executable is provided as an entrypoint, `serve` is the default
command. Start the development agent in your project root with:

``` docker
docker run --rm -it -p 8000:8000 -v ${PWD}:/docs squidfunk/mkdocs-material
```

If you're using Windows command prompt (`cmd.exe`), substitute `${PWD}` with
`"%cd%"`.

  [4]: https://hub.docker.com/r/squidfunk/mkdocs-material/

### Start the agent (init.d service)

 <small>Start Axon Agent by running:</small>

``` extempore
 sudo service axon-agent start
```
This will start the `axon-agent` process as the axon-agent user, which was created during the package installation. 

To configure the axon agent to start at boot time:

``` extempore
sudo /sbin/chkconfig --add axon-agent
```

### Start the Axon Agent (init.d service)

To start the service using systemd:

``` debcontrol
systemctl daemon-reload
systemctl start axon-agent
systemctl status axon-agent
```

Enable the systemd service so that axon agent starts at boot.

``` extempore
sudo systemctl enable axon-agent.service
```

### Environment file
The systemd service file and init.d script both use the file located at ` /etc/default/axon-agent ` for environment variables used when starting the agent. Here you can override log directory, data directory and other variables.

### Logging
By default Axon Agent will log to /var/log/axon_agent









