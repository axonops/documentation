


###  Add Healthchek Services

On the Axonops application menu, click `Healthchecks` and select `Setup` tab.

!!! infomy 

    [![healthchekcssetup](/img/healthchekcssetup.png)](/img/healthchekcssetup.png)



####  Create Services

Below there few examples `copy` and `Paste` inside. and click `save` [![save](/img/disk.png)](/img/disk.png)


``` jsonld
{
    "shellchecks": [
     {
         "name" : "check_cassandra_statusbinary",
         "shell" :  "/bin/bash",
         "script":  "/var/lib/cassandra_checks/check_cassandra_statusbinary.sh",
         "interval": "5m" ,
         "timeout": "1m" 
     }
   ],
 
   "httpchecks": [
     {
         "name" : "cassandra",
         "http" :  "http://localhost:9042",
         "tls_skip_verify":  true,
         "method": "GET" ,
         "interval": "10s" ,
         "timeout": "1m" 
     },
     {
         "name" : "cassandra",
         "http" :  "http://localhost:9916",
         "tls_skip_verify":  true,
         "method": "GET" ,
         "interval": "10s" ,
         "timeout": "1m" 
     }
   ],
   "tcpchecks": [
     {
         "name" : "tcp_cassandra",
         "tcp" :  "http://localhost:9042",
         "interval": "30s" ,
         "timeout": "1m" 
     },
     {
         "name" : "tcp_cassandra",
         "tcp" :  "http://localhost:9200",
         "interval": "5m" ,
         "timeout": "1m" 
     }
   ]
 
  }
               
```

Example:

!!! infomy

    
    [![healthcheckseditor](/img/healthcheckseditor.png)](/img/healthcheckseditor.png)


####  Delete Services

To Delete a service `copy` and `Paste` inside. and `click` save  [![save](/img/disk.png)](/img/disk.png)

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

