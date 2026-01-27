
Select the OS Family

<label>
  <input type="radio" id="Debian" name="osFamily" onChange="selectOS()" checked=true />
  <img src="/get_started/debian.png" class="skip-lightbox" width="180px" alt="debian">
</label>
<label>
  <input type="radio" id="RedHat" name="osFamily" onChange="selectOS()" />
  <img src="/get_started/red_hat.png" class="skip-lightbox" width="180px" alt="red_hat">
</label>


## Download Packages on Online Machine

### Set up Dependencies

Prior to downloading the AxonOps packages, we must first install any missing packages
on our online machine and setup the AxonOps package repository using the following steps:

<div id="DebianDiv-1" class="os os-debian" markdown="span" data-os="Debian">

```bash
{!installation/air-gapped/debian/online-dependencies.sh!}
```

</div>

<div id="RedHatDiv-1" class="os os-redhat" style="display:none" data-os="RedHat">

```bash
{!installation/air-gapped/redhat/online-dependencies.sh!}
```

</div>

### Download Packages

Follow the instructions below to download the necessary packages to the online machine's
`/tmp` directory. The bundled tarball(s) can then be easily transferred to the air-gapped
machine.

<div id="DebianDiv-2" class="os os-debian" markdown="span" data-os="Debian">

Since `axon-dash-pdf2` relies on virtual Debian packages, we must first download these
packages separately and by name: 

```bash
{!installation/air-gapped/debian/online-download-predependencies.sh!}
```

Download all additional AxonOps packages and dependencies:

```bash
{!installation/air-gapped/debian/online-download.sh!}
```

</div>

<div id="RedHatDiv-2" class="os os-redhat" style="display:none" data-os="RedHat">

```bash
{!installation/air-gapped/redhat/online-download.sh!}
```

</div>

## Install Packages on Air-Gapped Machine

<div id="DebianDiv-3" class="os os-debian" markdown="1" data-os="Debian">

On the air-gapped machine:

* transfer the intended tarballs produced in the previous step to a temporary directory,
* navigate into that directory,
* and run the following commands to:
    * define the helper function
    * and install the targeted software(s).
</div>
<div id="RedHatDiv-3" class="os os-redhat" style="display:none" markdown="1" data-os="RedHat">

On the air-gapped machine:

* transfer the tarball(s) produced in the previous step to a temporary directory,
* navigate into that directory,
* and run the following commands to:
    * setup the offline repo,
    * define the helper function,
    * and install the targeted software(s).

</div>

### Install the Server and Dashboard

Use the following script to install `axon-server` and `axon-dash` on the offline
machine. `axon-server` and `axon-dash` can be installed on the same machine or be
configured to communicate across two machines.

The `axon-dash-pdf2` package is optional and provides support for generating PDF reports.

<div id="DebianDiv-4" class="os os-debian" markdown="1" data-os="Debian">

```bash
{!installation/air-gapped/debian/offline-install.sh!}
```

</div>

<div id="RedHatDiv-4" class="os os-redhat" style="display:none" markdown="1" data-os="RedHat">

```bash
{!installation/air-gapped/redhat/offline-install.sh!}
```

</div>

### Install the Agent

Use the following script to install the `AxonOps agent` as well as a version of
`axon-cassandra*-agent` or `axon-kafka*-agent` that coincides with the version of
Cassandra/Kafka and the Java JDK that is being used.

<div id="DebianDiv-5" class="os os-debian" markdown="1" data-os="Debian">

```bash
{!installation/air-gapped/debian/offline-install-agent.sh!}
```

</div>
<div id="RedHatDiv-5" class="os os-redhat" style="display:none" markdown="1" data-os="RedHat">

```bash
{!installation/air-gapped/redhat/offline-install-agent.sh!}
```

</div>