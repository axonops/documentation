Select the OS Family

<label>
  <input type="radio" id="Debian" name="osFamily" onChange="selectOS()" checked=true />
  <img src="/get_started/debian.png" class="skip-lightbox" width="180px">
</label>
<label>
  <input type="radio" id="RedHat" name="osFamily" onChange="selectOS()" />
  <img src="/get_started/red_hat.png" class="skip-lightbox" width="180px">
</label>

Execute the following commands to setup the AxonOps repository:

<div id="DebianDiv" class="os">

```bash
{!installation/axon-agent/scripts/install-debian.sh!}
```

</div>

<div id="RedHatDiv" class="os" style="display:none">

```bash
{!installation/axon-agent/scripts/install-redhat.sh!}
```

</div>
