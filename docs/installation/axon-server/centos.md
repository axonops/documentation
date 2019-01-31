# axon-server installation (CentOS / RedHat)



## Prerequisites

Elasticsearch stores all of the collected data by axon-server. Let's install Java 8 and Elasticsearch first.


#### Installing the OpenJDK
``` - 
sudo yum install java-1.8.0-openjdk-devel
```

#### Installing the Oracle JDK x64
``` - 
wget -c --header "Cookie: oraclelicense=accept-securebackup-cookie" http://download.oracle.com/otn-pub/java/jdk/8u131-b11/d54c1d3a095b4ff2b6607d096fa80163/jdk-8u131-linux-x64.rpm
```

``` -
sudo yum jdk-8u131-linux-x64.rpm
```

{!installation/axon-server/elastic.md!}


## axon-server installer
``` -
sudo yum install <TODO>
```


{!installation/axon-server/install.md!}