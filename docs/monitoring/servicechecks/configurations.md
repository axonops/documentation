


###  Adding Service Checks

On the Axonops application menu, click `Service Checks` and select `Setup` tab.

!!! infomy 

    [![servicecheckssetup](/img/servicecheckssetup.png)](/img/servicecheckssetup.png)



####  Creating Services

Below there few examples. Just `copy`/`paste` inside the editor, then click `save` [![save](/img/disk.png)](/img/disk.png)


``` jsonld
{
    "shellchecks": [
        {
            "name" : "check_cassandra_process",
            "shell" :  "/bin/bash",
            "script":  "
                if [ `ps -auxwww | grep -v grep | grep org.apache.cassandra.service.CassandraDaemon | wc -l` -lt 1 ]
                then
                    exit 2
                else
                    exit 0
                fi
            ",
            "interval": "5m",
            "timeout": "1m" 
        }
   ],
 
    "httpchecks": [
        {
            "name" : "check_http_endpoint",
            "http" :  "https://{{.listen_address}}:80",
            "tls_skip_verify": true,
            "method": "GET",
            "interval": "10s",
            "timeout": "1m" 
        },
        {
            "name" : "check_http_endpoint2",
            "http" :  "http://localhost:8080",
            "tls_skip_verify": true,
            "method": "GET" ,
            "interval": "10s",
            "timeout": "1m" 
        }
    ],
   "tcpchecks": [
        {
            "name": "cassandra_cql_port_check",
            "interval": "10s",
            "timeout": "1m",
            "tcp": "{{.listen_address}}:9042"
        },
        {
            "name" : "cassandra_storage_port_check",
            "timeout": "1m",
            "interval": "5m",
            "tcp" : "{{.listen_address}}:7000"
        }
   ]
}
               
```
> Note that for a Cassandra node, you can use the variable `{{.listen_address}}` which will correspond to Cassandra listening address.

Example:

!!! infomy

    
    [![servicecheckseditor](/img/servicecheckseditor.png)](/img/servicecheckseditor.png)


####  Delete Services

To Delete a service `copy`/`paste` into the editor and `click` save  [![save](/img/disk.png)](/img/disk.png)

``` jsonld
{
    "shellchecks": [],
    "httpchecks": [],
    "tcpchecks": []

}
               
```

Example:

!!! infomy

    
    [![deleteservices](/img/deleteservices.png)](/img/deleteservices.png)

