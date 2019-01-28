# axon-server installation (Debian / Ubuntu)

## Prerequisites

Elasticsearch stores all of the collected data by axon-server. Let's install Java 8 and Elasticsearch first.

#### Installing the Oracle JDK

Run the following commands:
``` - 
su -
apt-get install dirmngr
echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu xenial main" | tee /etc/apt/sources.list.d/webupd8team-java.list
echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu xenial main" | tee -a /etc/apt/sources.list.d/webupd8team-java.list
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys EEA14886
apt-get update
apt-get install oracle-java8-installer
exit
```

Once you've accepted the license agreement the JDK will install.



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

## axon-server installer
``` -
sudo apt-get install <TODO>

```

{!installation/axon-server/install.md!}



