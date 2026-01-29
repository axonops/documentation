---
title: "What is SSH/SFTP"
description: "SSH/SFTP backup configuration for Cassandra. Secure remote backup setup."
meta:
  - name: keywords
    content: "SSH backup, SFTP, secure backup, Cassandra"
---

# What is SSH/SFTP

SSH File Transfer Protocol (SFTP) is a network protocol that provides file access, file transfer, and file management over any reliable data stream. It is typically used with SSH protocol to provide secure file transfer capabilities. Read more at [SSH.com SFTP](https://www.ssh.com/academy/ssh/sftp)

When selecting SSH/SFTP as a remote option there are several fields that need to be configured.

![sftp](./sftp.png)

#### Remote Backup Retention

The number of days that backup files will be kept in the remote storage provider location.
After this number of days, older files are removed.

#### Base Remote Path

This is the path on the remote SSH/SFTP server where backups will be stored. You can specify an absolute path like `/backups/cassandra` or a relative path from the user's home directory. By default AxonOps saves backups to `/path/org/clustertype/clustername/host-id/`.

The `org/clustertype/clustername/host-id/` path matches the top breadcrumb navigation in the AxonOps Dashboard.

#### Host

The hostname or IP address of the SSH/SFTP server. This can be:
* A fully qualified domain name (e.g., `backup.example.com`)
* An IP address (e.g., `192.168.1.100`)
* A hostname resolvable via DNS

#### Port

The port number for the SSH/SFTP connection. The default SSH port is 22, but your server may be configured to use a different port for security reasons.

#### Username

The username for authenticating to the SSH/SFTP server. This user must have:
* SSH access to the server
* Write permissions to the base remote path
* Sufficient disk quota for storing backups

#### Authentication Method

AxonOps supports two authentication methods for SSH/SFTP:

**Password Authentication**
* Enter the password for the specified username
* Less secure but simpler to configure
* May be disabled on some SSH servers for security reasons

**Key-Based Authentication**
* Uses SSH private key for authentication
* More secure than password authentication
* Requires the private key to be in PEM format

#### Private Key (for Key-Based Authentication)

When using key-based authentication, provide the SSH private key in PEM format. The key should:
* Be in standard PEM format (begins with `-----BEGIN RSA PRIVATE KEY-----` or similar)
* Have appropriate permissions (readable only by the AxonOps user)
* Correspond to a public key that has been added to the `~/.ssh/authorized_keys` file on the remote server

Example key format:
```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
...
-----END RSA PRIVATE KEY-----
```

#### Key Passphrase

If your private key is encrypted with a passphrase, enter it here. Leave blank if the key is not encrypted.

#### Host Key Verification

For security, AxonOps can verify the SSH server's host key to prevent man-in-the-middle attacks. Options include:
* **Strict**: Always verify the host key against known hosts
* **Accept New**: Accept new host keys but verify known ones
* **No Verification**: Skip host key verification (not recommended for production)

#### Compression

Enable compression for the SSH connection to reduce bandwidth usage. This is especially useful for:
* Slow network connections
* Large backup files
* Metered or limited bandwidth connections

#### Connection Timeout

The maximum time (in seconds) to wait for the SSH connection to be established. Increase this value if connecting to servers over slow or unreliable networks.

#### Disable Checksum

Normally AxonOps Backups will check that the checksums of transferred files match, and give an error "corrupted on transfer" if they don't. If you disable this then the checksum will be ignored if there are differences. This is not advised.

### Security Best Practices

1. **Use Key-Based Authentication**: Always prefer SSH keys over passwords for better security
2. **Restrict User Permissions**: Create a dedicated user for AxonOps with minimal required permissions
3. **Use Non-Standard Ports**: Consider using a non-standard SSH port to reduce automated attacks
4. **Enable Host Key Verification**: Always verify host keys in production environments
5. **Secure Key Storage**: Ensure private keys are stored securely with appropriate file permissions
6. **Regular Key Rotation**: Implement a key rotation policy for enhanced security
