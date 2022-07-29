# axon-server installation (Debian / Ubuntu)

## Step 1 - Prerequisites

Elasticsearch stores all of the collected data by axon-server. Let's install Java 8 and Elasticsearch first.

#### Installing JDK
Elasticsearch supports either OpenJDK or Oracle JDK. Since Oracle has changed the licensing model as of January 2019 we suggest using OpenJDK.

Run the following commands for OpenJDK:
``` bash
sudo apt-get update
sudo apt-get install default-jdk
```

Run the following commands for Oracle JDK:
``` bash
sudo apt-get update
sudo apt-get install dirmngr
sudo cp /etc/apt/sources.list /etc/apt/sources.list_backup
echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu xenial main" | sudo tee /etc/apt/sources.list.d/webupd8team-java.list
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys EEA14886
sudo apt-get update
sudo apt-get install oracle-java8-installer
```

Once you've accepted the license agreement the JDK will install.


#### Installing Elasticsearch

``` bash
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.6.1.deb
sudo dpkg -i elasticsearch-6.6.1.deb
```

{!installation/axon-server/elastic.md!}

## Step 2 - axon-server
``` bash
apt-get install curl gnupg
curl https://packages.axonops.com/apt/repo-signing-key.gpg | sudo apt-key add -
echo "deb https://packages.axonops.com/apt axonops-apt main" | sudo tee /etc/apt/sources.list.d/axonops-apt.list
sudo apt-get update
sudo apt-get install axon-server
```

{!installation/axon-server/install.md!}







