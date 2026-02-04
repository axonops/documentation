---
title: "SSL/TLS Connections"
description: "Configure SSL/TLS encrypted connections to Cassandra clusters in AxonOps Workbench. CA certificates, client certificates, and validation options."
meta:
  - name: keywords
    content: "SSL, TLS, encrypted connection, CA certificate, client certificate, Cassandra security, AxonOps Workbench"
---

# SSL/TLS Connections

Encrypting client-to-node communication with SSL/TLS protects data in transit between AxonOps Workbench and your Cassandra cluster. This is essential for production deployments, environments subject to compliance requirements such as PCI DSS or HIPAA, and any cluster accessible over an untrusted network.

When SSL/TLS is not enabled, AxonOps Workbench displays an open padlock icon next to the connection name in the work area and shows a warning in the interactive terminal:

> SSL is not enabled, the connection is not encrypted and is being transmitted in the clear.

Enabling SSL/TLS upgrades the icon to a closed padlock, confirming that traffic between the Workbench and the cluster is encrypted.

---

## SSL Tab Overview

The SSL tab in the connection dialog provides four fields for configuring encrypted connections:

<!-- Screenshot: SSL tab in the connection dialog showing the certificate fields, Enable SSL toggle, and Validate files toggle -->

| Field | cqlsh.rc Key | Description |
|-------|-------------|-------------|
| **CA Certificate File** | `certfile` | Path to the Certificate Authority (CA) certificate used to verify the server's identity |
| **Client Key File** | `userkey` | Path to the client's private key file, required for mutual TLS |
| **Client Certificate File** | `usercert` | Path to the client certificate file, required for mutual TLS |
| **Enable connection with SSL** | `ssl` | Toggle that enables or disables SSL/TLS for the connection |
| **Validate files** | `validate` | Toggle that enables or disables server certificate verification (enabled by default) |

Each certificate path field opens a native file picker when clicked, allowing you to browse to the file on your local filesystem.

!!! tip
    Use the **Test Connection** button after configuring SSL to verify that your certificates are correct and the cluster accepts the connection before saving.

---

## Certificate Formats

AxonOps Workbench expects certificates and keys in **PEM format**. PEM files are Base64-encoded and typically have the following extensions:

- `.pem` -- generic PEM-encoded file
- `.crt` or `.cert` -- certificate file
- `.key` -- private key file

A PEM certificate file begins and ends with markers like:

```
-----BEGIN CERTIFICATE-----
MIIDdzCCAl+gAwIBAgIEbL...
-----END CERTIFICATE-----
```

A PEM private key file begins and ends with:

```
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w...
-----END PRIVATE KEY-----
```

!!! info "Converting from other formats"
    If your certificates are in a different format (such as PKCS#12 or DER), convert them to PEM using OpenSSL:

    ```bash
    # Convert DER to PEM
    openssl x509 -inform DER -in certificate.der -out certificate.pem

    # Extract certificate and key from PKCS#12 (.p12 / .pfx)
    openssl pkcs12 -in keystore.p12 -out ca-cert.pem -cacerts -nokeys
    openssl pkcs12 -in keystore.p12 -out client-cert.pem -clcerts -nokeys
    openssl pkcs12 -in keystore.p12 -out client-key.pem -nocerts -nodes
    ```

---

## Common Configurations

### Server-Side SSL Only

This is the simplest SSL configuration. The client verifies the server's identity using the CA certificate, but the server does not require a client certificate. Use this when your cluster has `client_encryption_options.require_client_auth` set to `false` in `cassandra.yaml`.

**Required fields:**

- **CA Certificate File** -- path to the CA certificate that signed the server's certificate
- **Enable connection with SSL** -- toggled on
- **Validate files** -- toggled on

**Leave blank:**

- Client Key File
- Client Certificate File

<!-- Screenshot: SSL tab configured for server-side SSL only, with CA certificate set and Enable SSL toggled on -->

This corresponds to the following entries in the underlying `cqlsh.rc` configuration:

```ini
[connection]
ssl = true

[ssl]
certfile = /path/to/ca-certificate.pem
validate = true
```

### Mutual TLS (mTLS)

Mutual TLS provides two-way authentication: the client verifies the server, and the server verifies the client. Use this when your cluster has `client_encryption_options.require_client_auth` set to `true` in `cassandra.yaml`.

**Required fields:**

- **CA Certificate File** -- path to the CA certificate that signed the server's certificate
- **Client Key File** -- path to your client private key
- **Client Certificate File** -- path to your client certificate (signed by a CA trusted by the server)
- **Enable connection with SSL** -- toggled on
- **Validate files** -- toggled on

<!-- Screenshot: SSL tab configured for mutual TLS with all three certificate fields populated -->

This corresponds to the following entries in the underlying `cqlsh.rc` configuration:

```ini
[connection]
ssl = true

[ssl]
certfile = /path/to/ca-certificate.pem
userkey = /path/to/client-key.pem
usercert = /path/to/client-certificate.pem
validate = true
```

### Self-Signed Certificates

When connecting to a development or test cluster that uses self-signed certificates, the default certificate validation will fail because the certificate is not signed by a recognized CA. You can disable validation by toggling **Validate files** off.

!!! warning "Security implications"
    Disabling certificate validation means the Workbench will not verify the server's identity. This makes the connection vulnerable to man-in-the-middle attacks. Only disable validation in trusted development or test environments -- never in production.

**Required fields:**

- **Enable connection with SSL** -- toggled on
- **Validate files** -- toggled off

You may optionally still provide a CA certificate file. Even with validation disabled, the SSL/TLS encryption itself remains active -- traffic is still encrypted, but the server's identity is not verified.

This corresponds to the following entries in the underlying `cqlsh.rc` configuration:

```ini
[connection]
ssl = true

[ssl]
validate = false
```

---

## Per-Host CA Certificates

If your cluster nodes use different CA certificates (for example, during a certificate rotation), you can configure per-host CA certificates in the `cqlsh.rc` file directly using the `[certfiles]` section:

```ini
[certfiles]
192.168.1.3 = /path/to/keys/node1-ca.pem
192.168.1.4 = /path/to/keys/node2-ca.pem
```

When a per-host certificate is defined, it overrides the default `certfile` in the `[ssl]` section for that specific node.

!!! note
    Per-host CA certificates must be configured by editing the `cqlsh.rc` file in the Workbench editor. This option is not available through the SSL tab in the connection dialog.

---

## Troubleshooting

### Certificate File Not Found

**Symptom:** Connection fails with a file-not-found error after saving or testing.

**Possible causes and solutions:**

- Verify the file path is correct and the file exists at the specified location.
- Ensure the file is readable by your user account.
- If you moved or renamed the certificate files after configuring the connection, update the paths in the SSL tab.

### Certificate Format Errors

**Symptom:** Connection fails with an error indicating the certificate cannot be parsed or is in an unsupported format.

**Possible causes and solutions:**

- Confirm the file is in PEM format (not DER, PKCS#12, or JKS).
- Open the file in a text editor and verify it begins with `-----BEGIN CERTIFICATE-----` or `-----BEGIN PRIVATE KEY-----`.
- If the file is in another format, convert it to PEM using the OpenSSL commands listed in the [Certificate Formats](#certificate-formats) section above.

### Hostname Verification Failures

**Symptom:** Connection fails with a hostname mismatch or certificate verification error even though the CA certificate is correct.

**Possible causes and solutions:**

- The Common Name (CN) or Subject Alternative Name (SAN) in the server certificate must match the hostname or IP address you are connecting to.
- If you are connecting through an SSH tunnel to `127.0.0.1`, the server certificate likely does not list `127.0.0.1` as a valid name. In this case, you may need to disable validation for the tunneled connection.
- Ask your cluster administrator to reissue the server certificate with the correct hostname or IP in the SAN field.

### Expired Certificates

**Symptom:** Connection fails with a certificate expiration error.

**Possible causes and solutions:**

- Check the certificate expiration date using OpenSSL:

    ```bash
    openssl x509 -in /path/to/certificate.pem -noout -dates
    ```

- If the certificate has expired, obtain a renewed certificate from your CA or cluster administrator and update the path in the SSL tab.
- As a temporary workaround in non-production environments, you can disable validation by toggling **Validate files** off.

### SSL Handshake Failures

**Symptom:** Connection fails during the SSL handshake with a protocol or cipher error.

**Possible causes and solutions:**

- Ensure the Cassandra cluster has `client_encryption_options.enabled` set to `true` in `cassandra.yaml`.
- Verify that the TLS protocol version supported by the cluster is compatible. Cassandra 4.1 and later auto-negotiate the TLS protocol version.
- If the cluster requires client authentication (`require_client_auth: true`), make sure you have provided both the Client Key File and Client Certificate File.

### Connection Works Without SSL but Fails With SSL

**Symptom:** You can connect with the **Enable connection with SSL** toggle off but the connection fails when you turn it on.

**Possible causes and solutions:**

- Confirm that `client_encryption_options.enabled` is set to `true` on the Cassandra cluster. If the server does not have SSL enabled, the SSL handshake will fail.
- Double-check that the CA certificate you provided matches the one used to sign the server certificate.
- Try disabling **Validate files** temporarily to isolate whether the issue is with certificate validation or with the SSL setup itself.
