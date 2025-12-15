---
title: "-Xms4g"
description: "Configure Elasticsearch for AxonOps. Search backend setup and optimization."
meta:
  - name: keywords
    content: "Elasticsearch setup, AxonOps Elasticsearch, search backend"
---


### Configuration File Locations

Most installations of Elasticsearch have the default configuration location at `/etc/elasticsearch/`.

The default location depends on whether the installation is from an archive distribution (.tar.gz or .zip file) or a package distribution (Debian or RPM packages). For more info on Elasticsearch configuration, please read [Configuring Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/settings.html){target="_blank"}.

All commands on this page assume Elasticsearch was installed via a Debian or RPM package.

#### Other Default Locations

Depending on the installation method the default location for Elasticsearch configuration and binary files can change. Use these Elasticsearch docs for more information:

- [Tarball Installation](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/targz.html#targz-layout){target="_blank"}
- [Debian Package](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/deb.html#deb-layout){target="_blank"}
- [RPM Package](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/rpm.html#rpm-layout){target="_blank"}

## Configure Elasticsearch

### Increase Bulk Queue Size

Increase the bulk queue size of Elasticsearch by running the following command:

``` bash
{!installation/elasticsearch/scripts/increase-bulk-queue-size.sh!}
```

### Increase Heap Size

Increase the default heap size of elasticsearch by editing `/etc/elasticsearch/jvm.options`.

Set Xmx and Xms to no more than 50% of the machine's physical RAM.

Elasticsearch requires memory for purposes other than the JVM heap and it is important to leave available memory (RAM) space for this.

#### Example

If you have 16 GB of physical RAM, change the settings from:

``` bash
$ sudo grep 'Xm' /etc/elasticsearch/jvm.options
# -Xms4g
# -Xmx4g
```

to:

``` bash
$ sudo grep 'Xm' /etc/elasticsearch/jvm.options
-Xms8g
-Xmx8g 
```

In the above example, we set the minimum and maximum heap size to 8 GB.

### Increase Log Compression

Set the following index codec by running the following command:

``` bash
{!installation/elasticsearch/scripts/set-compression.sh!}
```

### Increase Number of Available Memory Maps

Elasticsearch uses an mmapfs directory by default to store its indices. 

The default operating system limits on mmap counts is likely to be too low, which may result in out of memory exceptions.

To increase the limits, run the following command:

``` bash
{!installation/elasticsearch/scripts/max-map-count.sh!}
```

To make this change persist across reboots run this command:

``` bash
{!installation/elasticsearch/scripts/max-map-count-persisted.sh!}
```

### Increase Number of File Descriptors

> Note: This section is only required for non-package installations. Debian and RPM
packages already use the intended value.

Elasticsearch needs `max file descriptors` system settings to be at least `65536`,
which can be updated with this command:

``` bash
{!installation/elasticsearch/scripts/increase-file-descriptors.sh!}
```

### Enable Security Features

Enable the Elasticsearch security features to enable basic authentication. Basic authentication is available as part of the basic Elasticsearch license, but disabled by default.

Run the following command to allow access to the cluster using username and password authentication:

``` bash
{!installation/elasticsearch/scripts/install-security-features.sh!}
```

## Start Elasticsearch

``` bash
{!installation/elasticsearch/scripts/start-elasticsearch.sh!}
```

After a short period of time, it is possible to verify that the Elasticsearch node is running by sending an HTTP request to port 9200 on localhost:

``` bash
curl "localhost:9200"
```

## Securing Elasticsearch

### Set Passwords for Default User

In the Elasticsearch `home` folder run **one** of the following commands to setup the default passwords for the built-in `elastic` user.

This commands creates a random secure password:

```bash
{!installation/elasticsearch/scripts/create-password-random.sh!}
```

This commands sets a self-assigned password:

```bash
{!installation/elasticsearch/scripts/create-password.sh!}
```

### Create a Dedicated Role

When creating a dedicated AxonOps role in Elasticsearch, the following privileges are required:

* Cluster privileges:
    * `monitor`
    * `manage_index_templates`
* Index privileges:
    * `auto_configure`
    * `manage`
    * `read`
    * `view_index_metadata`
    * `write`

The index privileges should be applied to the the following indices:

* `orgs`
* `orgname_*`
    * Where the `orgname` prefix should match the `org_name` value in the AxonOps server and agent config files.

<img src="/installation/elasticsearch/elastic_role.png">

### Advanced User Setups

You can learn more about other User Authentication options using the
[Elastic's official documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/setting-up-authentication.html){target="_blank"}.
