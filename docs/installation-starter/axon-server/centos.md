# axon-server installation (CentOS / RedHat)



## Step 1 - Prerequisites

Elasticsearch stores the data collected by axon-server.
AxonOps is currently only compatible with Elasticsearch 7.x, we recommend installing the latest available 7.x release.

#### Installing Elasticsearch

``` bash
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.17.16-x86_64.rpm
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.17.16-x86_64.rpm.sha512
sha512sum -c elasticsearch-7.17.16-x86_64.rpm.sha512
sudo rpm -i elasticsearch-7.17.16-x86_64.rpm
```

The `sha512sum` command above verifies the downloaded package and should show this output:
```
elasticsearch-7.17.16-x86_64.rpm: OK
```

{!installation-starter/axon-server/elastic.md!}


## Step 2 - axon-server
``` bash
sudo tee /etc/yum.repos.d/axonops-yum.repo << EOL
[axonops-yum]
name=axonops-yum
baseurl=https://packages.axonops.com/yum/
enabled=1
repo_gpgcheck=0
gpgcheck=0
EOL

sudo yum install axon-server
```


{!installation-starter/axon-server/install.md!}
