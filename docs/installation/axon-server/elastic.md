
Increase the bulk queue size of Elasticsearch and it's index codec by running the following command:

``` bash 
sudo echo 'thread_pool.bulk.queue_size: 2000' >> /etc/elasticsearch/elasticsearch.yml
sudo echo 'index.codec: best_compression' >> /etc/elasticsearch/elasticsearch.yml
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
And set `LimitNOFILE=65536` in `/etc/systemd/system/elasticsearch.services` 

#### Start Elasticsearch

``` bash
sudo systemctl start elasticsearch.service
```

After a short period of time, you can verify that your Elasticsearch node is running by sending an HTTP request to port 9200 on localhost:

``` bash
curl -X GET "localhost:9200/"
```
