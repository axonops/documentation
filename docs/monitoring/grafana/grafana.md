---
title: "Accessing AxonOps Metrics with Grafana"
description: "View AxonOps metrics in Grafana. Export and visualize Cassandra and Kafka metrics."
meta:
  - name: keywords
    content: "Grafana integration, AxonOps Grafana, metrics visualization"
---

# Accessing AxonOps Metrics with Grafana

## Generate API Token

Generate an API token with *read-only* permission to the clusters you wish to access.

- Login to (https://console.axonops.com)[https://console.axonops.com]
- Navigate in the left menu to API Tokens.

    <img src="/monitoring/grafana/api_token_menu.png" class="skip-lightbox">

- Click on Create New API Token button and complete the details.
    <img src="/monitoring/grafana/generate_api_token.png" class="skip-lightbox">


## Configure Grafana

- Configure a new Prometheus data source in Grafana
- Set the URL to **https://dash.axonops.cloud/$ORGNAME** 
- Enable Basic auth. 
- Paste the API key in the User field 
- Click Save & Test

Now you should be able to browse and query the metrics from the Explore interface.

See the video below:
![type:video](./setup.mov)
