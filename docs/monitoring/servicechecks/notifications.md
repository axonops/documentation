
Service checks will notify with one of the three statuses:

!!! info "Service Statuses."

    <span class="buttons"> [![info](/img/success_service.png)](/img/info.png)</span> Success

    <span class="buttons"> [![warning](/img/warning.png)](/img/warning.png)</span> Warning  

    <span class="buttons"> [![error](/img/error_service.png)](/img/error.png)</span> Error



Depending on the status of the service an appropriate alert will be sent.
The ```alert``` will be sent based on the ``` Default Routing ``` that has been [setup][1] via the integrations menu.

[1]: /how-to/default-routing/
   
> Noticed: If the ``` Default Routing ``` has not been set up ``` no alerts ``` will be sent.

Service Alerts will be sent using the following rules.

##Info

Default routing rules will be used to send <span class="myinfo"> success </span> alerts

## Warning

Default routing rules will be used to send  <span class="warning"> warning </span> alerts

##Error

Default routing rules will be used to send <span class="error"> error </span> alerts

