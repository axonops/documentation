
## What is S3

Amazon Simple Storage Service (Amazon S3) is an object storage service that offers industry-leading scalability, data availability, security, and performance. Read more at [Amazon S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html)

When selecting AWS S3 as a remote option there are a few fields that are mandatory the rest are optional.

S3 allows any valid UTF-8 string as a key.

![](./s3.png)

#### Remote Backup Retention

The amount of days that backup files will be kept in the remote storage provider location. 
After this amount of days the file that are older will be removed.

#### Base Remote Path

This is the name of the storage buckets, you can also add subfolders if using shared storage buckets or saving multiple clusters to the same bucket. by default AxonOps will save the backups to /bucket/folder/org/clustertype/clustername/host-id/

The org/clustertype/clustername/host-id/ will match the top breadcrump navigation in your AxonOps Dashboard.

#### Region

This is a drop down selection of all the AWS regions that are available for your AWS account.

#### Access Key ID and Secret Access Key

This is the standard AWS Access and Secret key that are associated with a IAM user. 
This AxonOps IAM user that has the key assigned ideally would have the following permissions for accessing the S3 buckets.

Please change the following 3 values

* BUCKETNAME : for some bucket naming rules please have a look [here](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html)
* ACCOUNT_ID : for info on the AWS Account ID please have a look [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/console_account-alias.html)
* AxonOpsS3User : the placeholder is an example name , it can be changed to any value for the the IAM User Name field

``` 
{
  "Id": "AxonOpsBackupBucketPolicy",
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "BackupsSID",
      "Action": [
        "s3:CreateAccessGrant"
      ],
      "Effect": "Allow",
      "Resource": "arn:aws:s3:::<BUCKETNAME>",
      "Principal": {
        "AWS": "arn:aws:iam::<ACCOUNT_ID>:<AxonOpsS3User>"
      }
    }
  ]
}
```

#### Storage Class

Amazon S3 offers a range of storage classes that you can choose from based on the performance, data access, resiliency, and cost requirements of your workloads. S3 storage classes are purpose-built to provide the lowest cost storage for different access patterns.

Please pick from the available AWS Storage classes:

* Glacier
* Glacier Deep Archive
* Intelligent-Tiering
* One Zone Infrequent Access
* Reduced Redundancy
* Standard
* Stadard Infrequent Access

For more inforamtion on S3 Storage classes please go [here](https://aws.amazon.com/s3/storage-classes/)

#### ACL

Amazon S3 access control lists (ACLs) enable you to manage access to buckets and objects. Each bucket and object has an ACL attached to it as a subresource. It defines which AWS accounts or groups are granted access and the type of access. When a request is received against a resource, Amazon S3 checks the corresponding ACL to verify that the requester has the necessary access permissions.

Please pick from the available AWS ACL's:

* Private
* Public Read
* Public Read-Write
* Authenticated Read
* Bucket Owner Read
* Bucket Owner Full Control

For more inforamtion on S3 ACL's please go [here](https://docs.aws.amazon.com/AmazonS3/latest/userguide/acl-overview.html#canned-acl)

#### Server Side Encryption

The server-side encryption algorithm used when storing this object in S3.

#### Disable Checksum

Normally AxonOps Backups will check that the checksums of transferred files match, and give an error "corrupted on transfer" if they don't. If you disable this then the checksum will be ignored if there are differences. This is not advised. 


