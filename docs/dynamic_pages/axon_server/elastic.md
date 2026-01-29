## Installation

Select the OS Family

<label>
  <input type="radio" id="Debian" name="osFamily" onChange="selectOS()" checked=true />
  <img src="/get_started/debian.png" class="skip-lightbox" width="180px" alt="debian">
</label>
<label>
  <input type="radio" id="RedHat" name="osFamily" onChange="selectOS()" />
  <img src="/get_started/red_hat.png" class="skip-lightbox" width="180px" alt="red_hat">
</label>

Execute the following commands to setup Elasticsearch for your OS:

<div id="DebianDiv" class="os" markdown="span">

```bash
{!installation/elasticsearch/scripts/install-debian.sh!}
```

</div>

<div id="RedHatDiv" class="os" style="display:none">

```bash
{!installation/elasticsearch/scripts/install-redhat.sh!}
```

</div>