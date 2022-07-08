# axon-server installation (CentOS / RedHat)



## Step 1 - Prerequisites

Elasticsearch stores all of the collected data by axon-server. Let's install Java 8 and Elasticsearch first.


#### Installing JDK
Elasticsearch supports either OpenJDK or Oracle JDK. Since Oracle has changed the licensing model as of January 2019 we suggest using OpenJDK.

Run the following commands for OpenJDK:
``` bash
sudo yum install java-1.8.0-openjdk-devel
```

Run the following commands for Oracle JDK:
``` bash
wget -c --header "Cookie: oraclelicense=accept-securebackup-cookie" http://download.oracle.com/otn-pub/java/jdk/8u131-b11/d54c1d3a095b4ff2b6607d096fa80163/jdk-8u131-linux-x64.rpm
```

``` bash
sudo rpm -i jdk-8u131-linux-x64.rpm
```

{!installation/axon-server/elastic.md!}


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


{!installation/axon-server/install.md!}
