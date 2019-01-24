
### Prerequisites

Elasticsearch stores all of the collected data by axon-server. Let's install Java 8 and Elasticsearch first.

#### Installing the Oracle JDK on Debian/Ubuntu

``` - 
sudo add-apt-repository ppa:webupd8team/java
```

``` - 
sudo apt update
```

Once the package list updates, install Java 8:

``` - 
sudo apt install oracle-java8-installer
```

Once you've accepted the license agreement the JDK will install.



#### Installing the Oracle JDK x64 on Centos/Redhat


``` - 
wget -c --header "Cookie: oraclelicense=accept-securebackup-cookie" http://download.oracle.com/otn-pub/java/jdk/8u131-b11/d54c1d3a095b4ff2b6607d096fa80163/jdk-8u131-linux-x64.rpm
```

``` -
sudo yum localinstall jdk-8u131-linux-x64.rpm
```

#### Installing Elasticsearch

``` -
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.5.4.tar.gz
```

``` -
tar -xzf elasticsearch-6.5.4.tar.gz
```

``` -
cd elasticsearch-6.5.4
```

Elasticsearch uses a mmapfs directory by default to store its indices. The default operating system limits on mmap counts is likely to be too low, which may result in out of memory exceptions.

You can increase the limits by running the following command:

``` - 
sudo sysctl -w vm.max_map_count=262144
```

Also, Elasticsearch needs `max file descriptors` system settings at least to 65536.
You can follow [those instructions][2] to set it up.

  [2]: https://www.elastic.co/guide/en/elasticsearch/reference/current/setting-system-settings.html#ulimit

Elasticsearch can be started from the command line as follows:

``` -
./bin/elasticsearch
```

You can test that your Elasticsearch node is running by sending an HTTP request to port 9200 on localhost:

``` -
curl -X GET "localhost:9200/"
```

#### Installing axon-server on Debian/Ubuntu

``` -
sudo add-apt-repository <TODO>
```

``` -
sudo apt install axon-server
```

#### Install via YUM Repository

Add the following to a new file at ` /etc/yum.repos.d/axonops.repo `

``` -
[axon-server]
name=axonserver
baseurl=https://repo.digitalis.io/axonops-apt/
repo_gpgcheck=1
enabled=1
gpgcheck=1
gpgkey=https://repo.digitalis.io/axonops-apt/gpg.key
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt

```


### Package details

* Configuration: `/etc/axonops/axon-server.yaml`
* Logs: ` /var/log/axonops/axon-server.log` 
* Binary: `usr/share/axonops/axon-server`






