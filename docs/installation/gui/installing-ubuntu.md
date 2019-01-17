
# Installing on Debian / Ubuntu


##  Axon-Dash Installation

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

Before installing [axon-dash][1], you need to make sure you have ... and ... – ... up and running. You can verify if you're already good to go with the following commands:

[1]: https://axonops.com

``` sh
.. --version
# ... 2.7.13
... --version
# ... 9.0.1
```

Installing and verifying axon-dash is as simple as:

``` debcontrol
wget <debian package url>
sudo apt-get install -y adduser libfontconfig
sudo dpkg -i axon-dash<version>_amd64.deb
```

Example

``` debcontrol
wget https://url/dl.axon-dash.4.2_amd64.deb
sudo apt-get install -y adduser libfontconfig
sudo dpkg -i axon-dash_5.4.2_amd64.deb
```
  

### APT Repository


Create a file `/etc/apt/sources.list.d/axon-dash.list` and add the following to it.

``` debcontrol
deb https://packages.axonops.axon-dash.com/oss/deb stable main
```

There is a separate repository if you want beta releases.

``` debcontrol
deb https://packages.axonops.axon-dash.com/oss/deb beta main
```

Use the above line even if you are on Ubuntu or another Debian version. Then add our gpg key. This allows you to install signed packages.

``` debcontrol 
curl https://packages.axonops.axon-dash.com/gpg.key | sudo apt-key add -
```

Update your Apt repositories and install axon-dash

``` debcontrol 
sudo apt-get update
sudo apt-get install axon-dash
```

On some older versions of Ubuntu and Debian you may need to install the apt-transport-https package which is needed to fetch packages over HTTPS.

``` extempore 
sudo apt-get install -y apt-transport-https
```

### Cloning from GitHub

Axon-Dash can also be used without a system-wide installation by cloning the repository into a subfolder of your project's root directory:

``` extempore
git clone https://github.com/squidfunk/axon-dash.git
```

This is especially useful if you want to extend the app and
override some parts of the app. The app will reside in the folder
`path-to/folder`.


### Package details

* Installs binary to ` /usr/sbin/axon-dash `
* Installs Init.d script to `/etc/init.d/axon-dash `
* Creates default file (environment vars) to ` /etc/default/axon-dash` 
* Installs configuration file to ` /etc/axon-dash/axon-dash.ini `
* Installs systemd service (if systemd is available) name ` axon-dash.agent` 
* The default configuration sets the log file at ` /var/log/axon-dash/axon-dash.log` 


###  Using Docker

If you're familiar with Docker, the official [Docker image][8] for Material
comes with all dependencies pre-installed and ready-to-use with the latest
version published on PyPI, packaged in a very small image. Pull it with:

``` docker
docker pull squidfunk/axon-dash
```

The `axonops` executable is provided as an entrypoint, `serve` is the default
command. Start the development server in your project root with:

``` docker
docker run --rm -it -p 8000:8000 -v ${PWD}:/docs squidfunk/axon-dash
```

If you're using Windows command prompt (`cmd.exe`), substitute `${PWD}` with
`"%cd%"`.

  [8]: https://hub.docker.com/r/squidfunk/mkdocs-material/

### Start the axon-dash (init.d service)

 <small>Start Java Agent by running:</small>

``` extempore
 sudo service axon-dash start
```
This will start the `axon-dash` process as the axon-dash user, which was created during the package installation. 

To configure the axon-dash to start at boot time:

``` extempore
sudo update-rc.d axon-dash defaults
```

### Start the Java Agent (init.d service)

To start the service using systemd:

``` debcontrol
systemctl daemon-reload
systemctl start axon-dash
systemctl status axon-dash
```

Enable the systemd service so that axon-dash starts at boot.

``` extempore
sudo systemctl enable axon-dash.service
```

### Environment file
The systemd service file and init.d script both use the file located at ` /etc/default/axon-dash ` for environment variables used when starting the axon-dash. Here you can override log directory, data directory and other variables.

### Logging
By default Java Agent will log to /var/log/axon-dash

### Logging in for the first time

Start Axon-Dash by executing `./bin/axon-dash`. The axon-dash binary needs the working directory to be the root install directory (where the binary and the public folder is located).

To run Axon-Dash open your browser and go to  <your-ip>:3000. 3000 is the default http port that axon-dash listens to. To configure axon-dash followw the instructions [here][3].
[3]: /configuration/axondash/