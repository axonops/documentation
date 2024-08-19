

Increase the bulk queue size of Elasticsearch by running the following command:

``` bash 
sudo echo 'thread_pool.write.queue_size: 2000' >> /etc/elasticsearch/elasticsearch.yml
```

Increase the default heap size of elasticsearch by editing `/etc/elasticsearch/jvm.options`.

Set Xmx and Xms to no more than 50% of your physical RAM.

**Example:**

From:
``` bash
-Xms1g
-Xmx1g 
```
To: 
``` bash
-Xms6g
-Xmx6g 
```
This will set the minimum and maximum heap size to 8 GB.

 Elasticsearch requires memory for purposes other than the JVM heap and it is important to leave available memory(RAM) space for this.


Set the following index codec by running the following command:

``` bash 
sudo echo 'index.codec: best_compression' >> /etc/elasticsearch/elasticsearch.yml
```

Elasticsearch uses an mmapfs directory by default to store its indices. 

The default operating system limits on mmap counts is likely to be too low, which may result in out of memory exceptions.

You can increase the limits by running the following command:

``` bash 
sudo sysctl -w vm.max_map_count=262144
```

To make this change persist across reboots run this command:

``` bash
echo "vm.max_map_count = 262144" | sudo tee /etc/sysctl.d/10-elasticsearch.conf > /dev/null
```

Elasticsearch needs `max file descriptors` system settings at least to 65536.

``` bash 
echo 'elasticsearch  -  nofile  65536' | sudo tee --append /etc/security/limits.conf > /dev/null
```

#### Start Elasticsearch

``` bash
sudo systemctl start elasticsearch.service
```

After a short period of time, you can verify that your Elasticsearch node is running by sending an HTTP request to port 9200 on localhost:

``` bash
curl "localhost:9200"
```