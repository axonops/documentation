
#### Installing Elasticsearch

``` bash
wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-6.5.4.tar.gz
```

``` bash
tar -xzf elasticsearch-6.5.4.tar.gz
```

Increase the bulk queue size of Elasticsearch by running the following command:

``` bash 
sudo echo 'thread_pool.bulk.queue_size: 2000' >> elasticsearch-6.5.4/config/elasticsearch.yml

```

Elasticsearch uses a mmapfs directory by default to store its indices. The default operating system limits on mmap counts is likely to be too low, which may result in out of memory exceptions.

You can increase the limits by running the following command:

``` bash 
sudo sysctl -w vm.max_map_count=262144
```



Also, Elasticsearch needs `max file descriptors` system settings at least to 65536.
``` bash 
echo 'elasticsearch  -  nofile  65536' | sudo tee --append /etc/security/limits.conf > /dev/null
```

Add an elasticsearch user
``` bash 
sudo adduser elasticsearch
```

Move elasticsearch to elasticsearch home directory
``` bash 

sudo mv elasticsearch-6.5.4 /home/elasticsearch/ 
sudo chown elasticsearch:elasticsearch /home/elasticsearch/ -R
```

Start Elasticsearch as a daemon from the elasticsearch user:

``` bash
sudo -u elasticsearch /home/elasticsearch/elasticsearch-6.5.4/bin/elasticsearch -d
```

After a short period of time, you can verify that your Elasticsearch node is running by sending an HTTP request to port 9200 on localhost:

``` bash
curl -X GET "localhost:9200/"
```
