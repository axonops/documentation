# Setup Service Checks



###  Add Service Checks

On the Axonops application menu, click `Service Checks` and select `Setup` tab.

 

    [![servicecheckssetup](/docs/img/servicecheckssetup.png)](/docs/img/servicecheckssetup.png)



####  Create Services

Below there few examples `copy` and `Paste` inside. and click `save` <span class="buttons"> [![save](/docs/img/disk.png)](/docs/img/disk.png) </span>


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



    
    [![servicecheckseditor](/docs/img/servicecheckseditor.png)](/docs/img/servicecheckseditor.png)


####  Delete Services

To Delete a service `copy` and `Paste` inside. and `click` save <span class="buttons"> [![save](/docs/img/disk.png)](/docs/img/disk.png) </span>

``` jsonld
{
    "shellchecks": [],
    "httpchecks": [],
    "tcpchecks": []

}
               
```

Example:



    
    [![deleteservices](/docs/img/deleteservices.png)](/docs/img/deleteservices.png)

