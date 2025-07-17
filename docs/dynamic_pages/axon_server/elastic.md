
### Select the OS Family

<label>
  <input type="radio" id="Debian" name="osFamily" onChange="selectOS()" checked=true />
  <img src="/get_started/debian.png" class="skip-lightbox" width="180px">
</label>
<label>
  <input type="radio" id="RedHat" name="osFamily" onChange="selectOS()" />
  <img src="/get_started/red_hat.png" class="skip-lightbox" width="180px">
</label>

## Download and Install Package

<div id="DebianDiv" class="os" markdown="span">


```bash
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.17.29-amd64.deb
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.17.29-amd64.deb.sha512
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.17.29-amd64.deb.asc
wget https://artifacts.elastic.co/GPG-KEY-elasticsearch

sha512sum -c elasticsearch-7.17.29-amd64.deb.sha512

gpg --import GPG-KEY-elasticsearch
gpg --lsign-key "rsa2048/D27D666CD88E42B4"
gpg --verify elasticsearch-7.17.29-amd64.deb

sudo dpkg -i elasticsearch-7.17.29-amd64.deb
```

The `sha512sum` command above verifies the integrity of the downloaded package and should show this output:

```
elasticsearch-7.17.29-amd64.deb: OK
```

The `gpg` command above also verifies the package has not been tampered with and should show a `Good signature` on the third line of the following output:

```
gpg: Signature made Thu 19 Jun 2025 02:31:53 AM UTC
gpg:                using RSA key 46095ACC8548582C1A2699A9D27D666CD88E42B4
gpg: Good signature from "Elasticsearch (Elasticsearch Signing Key) <dev_ops@elasticsearch.org>" [unknown]
gpg: WARNING: This key is not certified with a trusted signature!
gpg:          There is no indication that the signature belongs to the owner.
Primary key fingerprint: 4609 5ACC 8548 582C 1A26  99A9 D27D 666C D88E 42B4
```

`WARNING: This key is not certified with a trusted signature` should not be a concern.
However, to remove this warning, follow the man pages to increase Elasticsearch's
Signing Key's [trust level](https://www.gnupg.org/gph/en/manual/x334.html){target="_blank"}.

</div>

<div id="RedHatDiv" class="os" style="display:none">

```bash
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.17.29-x86_64.rpm
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.17.29-x86_64.rpm.sha512
sha512sum -c elasticsearch-7.17.29-x86_64.rpm.sha512
sudo rpm -i elasticsearch-7.17.29-x86_64.rpm
```

The sha512sum command above verifies the downloaded package and should show this output:

```
elasticsearch-7.17.29-x86_64.rpm: OK
```

</div>