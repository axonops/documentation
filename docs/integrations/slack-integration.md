# Setup Slack Integration

###  Create Slack Incoming Webhooks

Add the [Incoming WebHooks](https://axonopsworkspace.slack.com/marketplace/A0F7XDUAZ-incoming-webhooks){target="_blank"} app to Slack.

> Note: Ensure you're on the correct Slack Workspace by using the Workspace indicator on the top left.

In the `Post to Channel` Box, select an option from the `Choose a channel...` dropdown menu.

Click `Add Incoming WebHooks Integration`.

!!! infomy 

    [![ChannelBoxSLACK](imgs/slack-1.png)](imgs/slack-1.png)

Copy and make a note of the `WebHook URL` that appears in the `Setup Instructions`.

!!! infomy 

    [![SetupInstrucSLACK](imgs/slack-2.png)](imgs/slack-2.png)


### Creating the Slack integration on axon-server

On the Axonops application menu, select `Settings -> Integrations` .

Click on the `Slack` area.

!!! infomy 

    [![slack](imgs/integrations.png)](imgs/integrations.png)


[1]: #create-slack-incoming-webhooks

Add the `Webhook URL` from the previous step into the `url` field.

!!! infomy 

    [![slack](imgs/slack-2.jpg)](imgs/slack-2.jpg)


