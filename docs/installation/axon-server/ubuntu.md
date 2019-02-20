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

{!installation/axon-server/elastic.md!}

## Step 2 - axon-server installer
``` bash
sudo cp /etc/apt/sources.list /etc/apt/sources.list_backup
echo "deb https://repo.digitalis.io/repository/axonops-apt xenial main" | sudo tee /etc/apt/sources.list.d/axonops.list
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 727BDA4A
sudo apt-get update
sudo apt-get install axon-server
```

{!installation/axon-server/install.md!}







