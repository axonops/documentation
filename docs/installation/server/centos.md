
# axon-server installation (CentOS / RedHat)

## Prerequisites

Elasticsearch stores all of the collected data by axon-server. Let's install Java 8 and Elasticsearch first.

#### Installing the Oracle JDK x64


``` - 
wget -c --header "Cookie: oraclelicense=accept-securebackup-cookie" http://download.oracle.com/otn-pub/java/jdk/8u131-b11/d54c1d3a095b4ff2b6607d096fa80163/jdk-8u131-linux-x64.rpm
```

``` -
sudo yum jdk-8u131-linux-x64.rpm
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

## Installing axon-server 

``` -
sudo yum install <TODO>
```


#### Package details

* Configuration: `/etc/axonops/axon-server.yml`
* Logs: `/var/log/axonops/axon-server.log` 
* Binary: `usr/share/axonops/axon-server`
* Systemd service: `usr/lib/systemd/system/axon-server.service`

#### Start the server

``` -
systemctl daemon-reload
systemctl start axon-server
systemctl status axon-server
```

This will start the `axon-server` process as the `axonops` user, which was created during the package installation.  The default listening address is `0.0.0.0:8080`.

#### Configuration defaults

``` yaml

host: 0.0.0.0  # axon-server listening address 
port: 8080 # axon-server listening port 
elastic_host: localhost # Elasticsearch endpoint
elastic_port: 9200 # Elasticsearch port

axon-dash: # This must point to axon-dash address
  host: 127.0.0.1
  port: 3000
  https: false

alerting:
# How long to wait before sending a notification again if it has already
# been sent successfully for an alert. (Usually ~3h or more).
  notification_interval: 3h

retention:
  events: 24w # logs and events retention. Must be expressed in weeks (w)
  metrics:
      high_resolution: 30d # High frequency metrics. Must be expressed in days (d)
      med_resolution: 24w # Must be expressed in weeks (w)
      low_resolution: 24M # Must be expressed in months (M)
      super_low_resolution: 3y # Must be expressed in years (y)
  backups: # Those are use as defaults but can be overridden from the UI
    local: 10d
    remote: 30d 
```

## Installing axon-dash

Now axon-server is installed, you can start installing [axon-dash](../gui/centos.md)





