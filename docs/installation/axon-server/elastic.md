
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
