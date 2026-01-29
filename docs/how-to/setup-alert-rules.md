---
title: "Set up alert rules"
description: "Create alert rules in AxonOps. Configure thresholds and notifications for metrics."
meta:
  - name: keywords
    content: "alert rules, AxonOps alerts, threshold configuration, notifications"
---

# Set up alert rules



### Create an alert rule

On the AxonOps application menu, click **Dashboards** and select the required dashboard (e.g., **System**).

Hover over the desired chart and click <span class="buttons">[![testb](../img/testb.png)](../img/testb.png)</span>.



[![createrule](../img/createrule.gif)](../img/createrule.gif)

### Complete the form fields

* Below the chart, click the **Alert** tab.



[![alertform](../img/alertform.png)](../img/alertform.png)


* A form will appear.


[![alertformfields](../img/alertformfields.png)](../img/alertformfields.png)


* Complete the alert settings by setting **Comparator Warning value** and/or **Critical value**, and the **Duration** (how often to check).


[![allertfields](../img/allertfields.png)](../img/allertfields.png)


#### Annotations

In the **Summary** box, you can include free text and one or more of the following `$labels`:


```yaml
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

In the **Description** box, you can include free text along with one or more of the above `$labels`.

!!! info "Example"

    `CPU usage per DC Alerts usage on {{ $labels.hostname }} and cluster {{$labels.cluster}}`
    



[![annotations](../img/annotations.png)](../img/annotations.png)


#### Integrations


* Using the slider bar <span class="buttons">[![sliderbar](../img/sliderbar.png)](../img/sliderbar.png)</span> you can select any [Integrations][1].

    Then click the **Info**, **Warning**, and **Error** icons to select the group(s) of [Integrations][1] for the alert.

[1]: ../integrations/overview.md



[![alertintegrations](../img/alertintegrations.png)](../img/alertintegrations.png)
[![alertintegrationswith](../img/alertintegrationswith.png)](../img/alertintegrationswith.png)


!!! info "Not selecting integrations"

    If you do not select any specific [Integrations][1], the alert automatically follows **Global Dashboard Routing**. If this has not been set up, it uses [Default Routing][2].



[2]: default-routing.md


### Edit Alert Rule

On the AxonOps application menu, click **Alerts & Notifications**, select **Active**, then select the **Alert Rules** tab and click <span class="buttons">[![edit](../img/edit.png)](../img/edit.png)</span>.


[![editalertrule](../img/editalertrule.png)](../img/editalertrule.png)


### Delete Alert Rule(s)

To delete an alert, either:

* On the AxonOps application menu, click **Dashboards** and select the required dashboard (e.g., **System**). Hover over the desired chart and click <span class="buttons">[![edit](../img/edit.png)](../img/edit.png)</span>. Below the chart, click the **Alert** tab and click <span class="buttons">[![delbtn](../img/delbtn.png)](../img/delbtn.png)</span> on the alert rule you want to remove.

OR...

* On the AxonOps application menu, click **Alerts & Notifications**, select **Active**, then select the **Alert Rules** tab and click <span class="buttons">[![delbtn](../img/delbtn.png)](../img/delbtn.png)</span>.



  [![activealertrules](../img/activealertrules.png)](../img/activealertrules.png)
