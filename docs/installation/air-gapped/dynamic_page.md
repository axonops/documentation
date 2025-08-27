
Select the OS Family

<label>
  <input type="radio" id="Debian" name="osFamily" onChange="selectOS()" checked=true />
  <img src="/get_started/debian.png" class="skip-lightbox" width="180px">
</label>
<label>
  <input type="radio" id="RedHat" name="osFamily" onChange="selectOS()" />
  <img src="/get_started/red_hat.png" class="skip-lightbox" width="180px">
</label>


## Download Packages on Online Machine

### Setup Dependencies

Prior to downloading the AxonOps packages, we must first install any missing packages
on our online machine and setup the AxonOps package repository using the following steps:

<div id="DebianDiv" class="os" markdown="span">

```bash
{!installation/air-gapped/debian/online-dependencies.sh!}
```

</div>

<div id="RedHatDiv" class="os" style="display:none">

```bash
{!installation/air-gapped/redhat/online-dependencies.sh!}
```

</div>

### Download Packages

Follow the instructions below to download the necessary packages to the online machine's
`/tmp` directory. The bundled tarball(s) can then be easily transferred to the air-gapped
machine.

<div id="DebianDiv" class="os" markdown="span">

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

<div id="RedHatDiv" class="os" style="display:none">

```bash
{!installation/air-gapped/redhat/online-download.sh!}
```

</div>

## Install Packages on Air-Gapped Machine

<div id="DebianDiv" class="os" markdown="1">

On the air-gapped machine:

* transfer the intended tarballs produced in the previous step to a temporary directory,
* navigate into that directory,
* and run the following commands to:
    * define the helper function
    * and install the targetted software(s).


```bash
{!installation/air-gapped/debian/offline-install.sh!}
```

</div>

<div id="RedHatDiv" class="os" style="display:none" markdown="1">

On the air-gapped machine:

* transfer the tarball(s) produced in the previous step to a temporary directory,
* navigate into that directory,
* and run the following commands to:
    * setup the offline repo,
    * define the helper function,
    * and install the targetted software(s).

```bash
{!installation/air-gapped/redhat/offline-install.sh!}
```

</div>
