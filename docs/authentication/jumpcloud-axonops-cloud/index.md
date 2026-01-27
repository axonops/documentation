---
title: "Prerequisites and notes"
description: "Configure JumpCloud SAML authentication for AxonOps Cloud. Step-by-step SSO integration guide."
meta:
  - name: keywords
    content: "JumpCloud, SAML, SSO, AxonOps authentication, single sign-on"
---

# Prerequisites and notes
Configuring SAML authentication with JumpCloud for AxonOps Cloud
================================================================

This guide will walk you through configuring JumpCloud for AxonOps, focusing on setting up Single Sign-On (SSO) and customizing user attributes

## Prerequisites and notes

### Prerequisites

1. SAML support must be enabled for your account by AxonOps
2. You will need an RSA certificate and key in PEM format. You can generate a self-signed certificate and key with this command:
```bash
openssl req -new -newkey rsa:2048 -sha256 -days 3650 -nodes -x509 -keyout saml.key -out saml.crt
```

### Notes

After SAML support is enabled on your AxonOps account the URLs used to access the dashboard will change
from `dash.axonops.cloud` to `orgname.axonops.cloud` (where `orgname` is your AxonOps organisation).
This does not affect normal operation but any bookmarks you have to dashboard pages will no longer work.

**Logging in after enabling SAML**

After SAML has been configured you will have 2 ways to login to the AxonOps console:

1. https://console.axonops.cloud - Login with username+password or Google login
2. https://orgname.axonops.cloud - Login with SAML via JumpCloud

## Next Steps

[Configure JumpCloud](01-jumpcloud-app.md)

[Configure roles in JumpCloud](02-jumpcloud-roles.md)

[Configure SAML in AxonOps Cloud](03-axonops-saml-jumpcloud.md)