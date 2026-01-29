---
title: "Set up Microsoft Teams Integration"
description: "Configure Microsoft Teams notifications in AxonOps. Send alerts to Teams channels."
meta:
  - name: keywords
    content: "Microsoft Teams, Teams integration, AxonOps alerts, chat notifications"
---

# Set up Microsoft Teams Integration

## Create Microsoft Teams Webhook

On the Microsoft Teams interface, go to `Connectors`.

![teams-1](imgs/teams-1.png)

`Configure` the `Incoming Webhook` connector.

![teams-2](imgs/teams-2.png)

Provide a name and select `Create`.

![teams-3](imgs/teams-3.png)

Copy the URL provided to the clipboard.

![teams-4](imgs/teams-4.png)

## Create the Microsoft Teams Integration on axon-server

On the AxonOps application menu, select `Settings -> Integrations`.

Click on the `Microsoft Teams` area.

![integrations](imgs/integrations.png)

Enter a `name`, paste the URL in the `Webhook URL` field, and select `Create`.

![teams-6](imgs/teams-6.png)
