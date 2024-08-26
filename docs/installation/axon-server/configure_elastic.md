# Configure Elasticsearch

## Configuration file location

Most installations of Elasticsearch have the default config location at `/etc/elasticsearch/`

The default location depends on whether or not the installation is from an archive distribution (tar.gz or zip) or a package distribution (Debian or RPM packages).

For more info on Elasticsearch configuration please read [Configuring Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/settings.html){target="_blank"}

## Other default locations

Depending on the installation method the default location for Elasticsearch configuration and binary files can change. 

- Tarball Installation

    [Default Layout](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/targz.html#targz-layout){target="_blank"}
    
- Debian Package
      
    [Default Layout](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/deb.html#deb-layout){target="_blank"} 

- RPM Package

    [Default Layout](https://www.elastic.co/guide/en/elasticsearch/reference/7.17/rpm.html#rpm-layout){target="_blank"}

## Enable security features

Enabling the Elasticsearch security features enables basic authentication so that you can run a local cluster with username and password authentication.

This is part of the basic Elasticsearch licence, security is disabled by default on all Elasticsearch installs.

Edit `/etc/elasticsearch/elasticsearch.yml` and add/update the following line


```yaml
xpack.security.enabled: true
```

## Set passwords for default elastic built-in user

In the Elasticsearch `home` folder run the following commands to setup the default passwords.

**Please only run one of the commands.**

The below example will create a random secure password for the elastic user.

```
<DEFAULT LOCATION>/bin/elasticsearch-reset-password -u elastic
```

If you want to set the password using your own password, run the command with the interactive (-i) parameter. 
The example will set a self-assigned password for the elastic built-in user.

```
<DEFAULT LOCATION>/bin/elasticsearch-reset-password -i -u elastic
```






