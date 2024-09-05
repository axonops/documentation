


###  Adding Service Checks

On the Axonops application menu, click `Service Checks` and select `Setup` tab.

![](./0.JPG)



####  Creating Services

               
```
> Note that for a Cassandra node, you can use the variable `{{.listen_address}}` which will correspond to Cassandra listening address.

Example:



    
    [![servicecheckseditor](/docs/img/servicecheckseditor.png)](/docs/img/servicecheckseditor.png)


####  Delete Services

To Delete a service `copy`/`paste` into the editor and `click` save  [![save](/docs/img/disk.png)](/docs/img/disk.png)

``` jsonld
{
    "shellchecks": [],
    "httpchecks": [],
    "tcpchecks": []

}
               
```

Example:



    
    [![deleteservices](/docs/img/deleteservices.png)](/docs/img/deleteservices.png)

