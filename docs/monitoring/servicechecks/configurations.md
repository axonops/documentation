


###  Adding Service Checks

On the Axonops application menu, click `Service Checks` and select `Setup` tab.

![](./0.JPG)



####  Creating Services

               
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

