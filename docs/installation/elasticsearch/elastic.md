
### Configure Elasticsearch

#### Increase Bulk Queue Size

Increase the bulk queue size of Elasticsearch by running the following command:

``` bash 
echo 'thread_pool.write.queue_size: 2000' \
    | sudo tee --append /etc/elasticsearch/elasticsearch.yml
```

#### Increase Heap Size

Increase the default heap size of elasticsearch by editing `/etc/elasticsearch/jvm.options`.

Set Xmx and Xms to no more than 50% of the machine's physical RAM.

Elasticsearch requires memory for purposes other than the JVM heap and it is important to leave available memory (RAM) space for this.

##### Example

If you have 16 GB of physical RAM, change the settings from:

``` bash
$ sudo grep '\-Xm' /etc/elasticsearch/jvm.options
# -Xms4g
# -Xmx4g
```

to:

``` bash
$ sudo grep '\-Xm' /etc/elasticsearch/jvm.options
-Xms8g
-Xmx8g 
```

In the above example, we set the minimum and maximum heap size to 8 GB.

#### Increase Log Compression

Set the following index codec by running the following command:

``` bash 
echo 'index.codec: best_compression' \
    | sudo tee --append /etc/elasticsearch/elasticsearch.yml
```

#### Increase Number of Available Memory Maps

Elasticsearch uses an mmapfs directory by default to store its indices. 

The default operating system limits on mmap counts is likely to be too low, which may result in out of memory exceptions.

To increase the limits, run the following command:

``` bash 
sudo sysctl -w vm.max_map_count=262144
```

To make this change persist across reboots run this command:

``` bash
echo "vm.max_map_count = 262144" \
    | sudo tee --append /etc/sysctl.d/10-elasticsearch.conf
```

Elasticsearch needs `max file descriptors` system settings to be at least `65536`,
which can be updated with this command:

``` bash 
echo 'elasticsearch  -  nofile  65536' \
    | sudo tee --append /etc/security/limits.conf
```

#### Create an AxonOps Service Account or User

To create service accounts or users, please refer to the Elasticsearch docs [here](https://www.elastic.co/guide/en/elasticsearch/reference/current/setting-up-authentication.html){target="_blank"}.

### Start Elasticsearch

``` bash
sudo systemctl start elasticsearch.service
```

After a short period of time, it is possible to verify that the Elasticsearch node is running by sending an HTTP request to port 9200 on localhost:

``` bash
curl "localhost:9200"
```

### Securing Elasticsearch

Once Elasticsearch is online, move onto the next section to
[secure the Elasticsearch instance](./securing_elastic.md).
