---
description: "Configure Google Cloud Storage backup for Cassandra with AxonOps."
meta:
  - name: keywords
    content: "GCS backup, Google Cloud Storage, Cassandra backup, AxonOps"
---

## What is Google Cloud Storage

Google Cloud Storage (GCS) is a RESTful online file storage web service for storing and accessing data on Google Cloud Platform infrastructure. It provides unified object storage for developers and enterprises, from live data serving to data analytics/ML to data archiving. Read more at [Google Cloud Storage documentation](https://cloud.google.com/storage/docs)

When selecting Google Cloud Storage as a remote option there are several fields that need to be configured.

![](./gcs.png)

#### Remote Backup Retention

The amount of days that backup files will be kept in the remote storage provider location. 
After this amount of days the files that are older will be removed.

#### Base Remote Path

This is the name of the GCS bucket, you can also add subfolders if using shared storage buckets or saving multiple clusters to the same bucket. By default AxonOps will save the backups to `/bucket/folder/org/clustertype/clustername/host-id/`

The org/clustertype/clustername/host-id/ will match the top breadcrumb navigation in your AxonOps Dashboard.

#### Project ID

Your Google Cloud Project ID. This is a unique identifier for your GCP project and can be found in the GCP Console. It typically looks like `my-project-123456`.

#### Authentication

AxonOps supports multiple authentication methods for Google Cloud Storage:

**VM Instance Service Account (Recommended)**

The recommended approach is to use the service account attached to your GCE instances. This method is more secure as it doesn't require storing credentials:

1. Create a service account with the necessary GCS permissions (see IAM section below)
2. Attach the service account to your GCE instances running Cassandra
3. Leave the Service Account Key field empty in AxonOps
4. AxonOps will automatically use the instance's service account credentials

This approach provides:
* No credential management or key rotation needed
* More secure - no long-lived keys to protect
* Automatic credential refresh
* Follows GCP security best practices
* Works with Workload Identity for GKE deployments

**Service Account Key (Alternative)**
* Uses a JSON key file for authentication
* Only use when instance service accounts are not available (e.g., on-premises)
* Requires secure key storage and rotation
* Allows fine-grained permissions through IAM

**OAuth2 Token**
* Uses OAuth2 access tokens
* Suitable for development or temporary access
* Requires token refresh management

#### Service Account Configuration

When using explicit service account keys (not recommended), provide the JSON key file contents. 

**Required Permissions**

Whether using instance service accounts or explicit keys, the service account needs these permissions:
* `storage.buckets.get`
* `storage.objects.create`
* `storage.objects.delete`
* `storage.objects.get`
* `storage.objects.list`

You can grant these permissions by:
1. Using the predefined role `roles/storage.objectAdmin` on the specific bucket
2. Creating a custom role with only these permissions
3. Using `roles/storage.legacyBucketWriter` and `roles/storage.objectViewer` combined

Example service account key structure:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "service-account@project.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

#### Location

The location where your bucket is stored. Google Cloud Storage offers several location types:
* **Regional**: Data stored in a specific region (e.g., `us-central1`, `europe-west1`)
* **Multi-regional**: Data replicated across regions (e.g., `us`, `eu`, `asia`)
* **Dual-regional**: Data replicated across two specific regions

Choose based on your latency, availability, and compliance requirements.

#### Storage Class

Google Cloud Storage offers different storage classes optimized for different use cases:

* **Standard**: Best for frequently accessed data ("hot" data)
* **Nearline**: For data accessed once per month
* **Coldline**: For data accessed once per quarter
* **Archive**: For data accessed less than once per year

For backups, consider:
* Use **Standard** for recent backups that might need quick access
* Use **Nearline** or **Coldline** for older backups
* Use **Archive** for long-term compliance storage

#### Encryption

GCS provides several encryption options:
* **Google-managed keys**: Default encryption (no configuration needed)
* **Customer-managed keys (CMEK)**: Use your own keys via Cloud KMS
* **Customer-supplied keys (CSEK)**: Provide your own encryption keys

#### Object Lifecycle Management

While not directly configured in AxonOps, you can set up lifecycle rules in GCS to:
* Automatically transition objects to cheaper storage classes
* Delete objects older than the retention period
* Manage versions of objects

#### Uniform Bucket-Level Access

Recommended security setting that disables object ACLs and uses only IAM for access control. Enable this in your GCS bucket settings for better security.

#### Versioning

Object versioning can be enabled on the bucket to:
* Protect against accidental deletion
* Maintain backup history
* Support point-in-time recovery

#### Disable Checksum

Normally AxonOps Backups will check that the checksums of transferred files match, and give an error "corrupted on transfer" if they don't. If you disable this then the checksum will be ignored if there are differences. This is not advised.

### IAM Best Practices

1. **Use Service Accounts**: Create a dedicated service account for AxonOps
2. **Principle of Least Privilege**: Grant only the minimum required permissions
3. **Bucket-Level Permissions**: Apply IAM policies at the bucket level when possible
4. **Audit Logging**: Enable Cloud Audit Logs for backup operations
5. **Key Rotation**: Regularly rotate service account keys

### Cost Optimization

1. **Choose Appropriate Storage Class**: Match storage class to access patterns
2. **Set Lifecycle Policies**: Automatically transition to cheaper storage
3. **Regional Selection**: Choose regions close to your Cassandra clusters
4. **Monitor Egress Costs**: Be aware of cross-region transfer costs
5. **Enable Bucket Lock**: For compliance requirements, preventing early deletion

### Troubleshooting

1. **Permission Denied**: Check IAM permissions and service account key
2. **Bucket Not Found**: Verify project ID and bucket name
3. **Invalid Key**: Ensure the JSON key is properly formatted
4. **Network Timeouts**: Check firewall rules and GCP connectivity
5. **Storage Class Errors**: Verify the storage class is available in your region