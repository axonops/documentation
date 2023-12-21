# axon-server installation (Debian / Ubuntu)

## Step 1 - Prerequisites

Elasticsearch stores the data collected by axon-server.
AxonOps is currently only compatible with Elasticsearch 7.x, we recommend installing the latest available 7.x release.

#### Installing Elasticsearch

``` bash
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.17.16-amd64.deb
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.17.16-amd64.deb.sha512
shasum -a 512 -c elasticsearch-7.17.16-amd64.deb.sha512
sudo dpkg -i elasticsearch-7.17.16-amd64.deb
```

The `shasum` command above verifies the downloaded package and should show this output:
```
elasticsearch-7.17.16-amd64.deb: OK
```

{!installation/axon-server/elastic.md!}

## Step 2 - axon-server
``` bash
apt-get install curl gnupg ca-certificates
curl https://packages.axonops.com/apt/repo-signing-key.gpg | sudo apt-key add -
echo "deb https://packages.axonops.com/apt axonops-apt main" | sudo tee /etc/apt/sources.list.d/axonops-apt.list
sudo apt-get update
sudo apt-get install axon-server
```

{!installation/axon-server/install.md!}







