# Setup alert rules



###  Insert Alert Rules Credentials

On the Axonops application menu, click `Dashboards` and `select` required Dashboard. eg. `System`

`Hover over` the desired Chart `click` on the <span class="buttons"> [![testb](/docs/img/testb.png)](/docs/img/testb.png) </span> button.


 

[![createrule](/docs/img/createrule.gif)](/docs/img/createrule.gif)

###  Complete The Fields In Form

* Below the chart `click` on the `alert` tab.


 

[![alertform](/docs/img/alertform.png)](/docs/img/alertform.png)


* A form will appear

 

[![alertformfields](/docs/img/alertformfields.png)](/docs/img/alertformfields.png)


* Complete Alert settings in `Comparator Warning value` or `Critical value` or Both and the `Duration` ==> (how often to check) In

 

[![allertfields](/docs/img/allertfields.png)](/docs/img/allertfields.png)


####  Annotations

In the `Summary` box you can include free text & type one `or` many of the following `$labels`


``` yaml

$labels:
   - cluster
   - dc
   - hostname
   - org
   - rack
   - type
   - keyspace
$value:

```

In the `Description` box you can include free along with one `or` many of the above  `$labels`

!!! info "Example"

    `CPU usage per DC Alerts usage on {{ $labels.hostname }} and cluster {{$labels.cluster}}`
    



    
[![annotations](/docs/img/annotations.png)](/docs/img/annotations.png)


####  Integrations


* Using the slider bar <span class="buttons"> [![sliderbar](/docs/img/sliderbar.png)](/docs/img/sliderbar.png) </span> you can select any [Integrations][1].

    Then `click` on the `Info`, `Warning`, `Error` icons, to select the group(s) of [Integrations][1] for the alert.

[1]: /docs/integrations/overview

[![alertintegrations](/docs/img/alertintegrations.png)](/docs/img/alertintegrations.png)
[![alertintegrationswith](/docs/img/alertintegrationswith.png)](/docs/img/alertintegrationswith.png)

    
!!! info "Not selecting integrations"

    If you do not select any specific [Integrations][1] the Alert will automatically follow the `Global Dashboard Routing` or if this has not been [setup][2] the [Default Routing][3] Integrations.



[2]: /docs/how-to/setup-dashboards-global-integrations
[3]: /docs/how-to/default-routing


### Edit Alert Rule

On the Axonops application menu, click `Alerts & Notifications` and `click` Active. `Select` the `Alert Rules` tab and click <span class="buttons"> [![edit](/docs/img/edit.png)](/docs/img/edit.png) </span>



[![editalertrule](/docs/img/editalertrule.png)](/docs/img/editalertrule.png)


### Delete Alert Rule(s)

To Delete An Alert Either...

* On the Axonops application menu, click `Dashboards` and `select` required Dashboard. `eg. System` `Hover over` the desired Chart click on the <span class="buttons"> [![edit](/docs/img/edit.png)](/docs/img/edit.png) </span> button. Below the chart `click` on the `alert` tab and `click` on the <span class="buttons"> [![delbtn](/docs/img/delbtn.png)](/docs/img/delbtn.png) </span> of the alert rule you want to remove.

OR...

* On the Axonops application menu, click `Alerts & Notifications` and `click` Active. `Select` the Alert Rules tab and click  <span class="buttons"> [![delbtn](/docs/img/delbtn.png)](/docs/img/delbtn.png) </span>




[![activealertrules](/docs/img/activealertrules.png)](/docs/img/activealertrules.png)
