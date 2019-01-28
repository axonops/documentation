# Setup Healthcheks



###  Add Healthchek Services

On the Axonops application menu, click `Healthchecks` and select `Setup` tab.

!!! infomy 

    [![healthchekcssetup](/img/healthchekcssetup.png)](/img/healthchekcssetup.png)



####  Create Services

Below there few examples `copy` and `Paste` inside. and click `save` <span class="buttons"> [![save](/img/disk.png)](/img/disk.png) </span>


``` jsonld
{
    "shellchecks": [
     {
        "name" : "check_elastic",
        "shell" :  "/bin/bash",
        "script":  "if [ 'ps auxwww | grep elastic | wc -l' -lt 1 ] then exit 2 else exit 0  fi",
        "interval": "5m" ,
        "timeout": "1m" 
     }
   ],
 
   "httpchecks": [],
   "tcpchecks": [
    {
        "name": "elastic_tcp_endpoint_check",
        "interval": "5s",
        "timeout": "1m",
        "tcp": "localhost:9200"
    }
   ]
 
}
               
```

Example:

!!! infomy

    
    [![healthcheckseditor](/img/healthcheckseditor.png)](/img/healthcheckseditor.png)


####  Delete Services

To Delete a service `copy` and `Paste` inside. and `click` save <span class="buttons"> [![save](/img/disk.png)](/img/disk.png) </span>

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

