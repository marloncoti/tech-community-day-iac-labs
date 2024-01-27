"""A Python Pulumi program"""

import pulumi
import pulumi_aws as aws

bucket = aws.s3.Bucket(
    "my-website-bucket-mcoti",
    website=aws.s3.BucketWebsiteArgs(
        index_document="index.html",
    ),
)

public_access_block = aws.s3.BucketPublicAccessBlock(
    "public-access-block",
    bucket=bucket.bucket,
    block_public_policy=False,
)

aws.s3.BucketPolicy(
    "bucket-policy",
    bucket=bucket.bucket,
    policy=pulumi.Output.json_dumps({
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": "*",
            "Action": ["s3:GetObject"],
            "Resource": [
                pulumi.Output.concat(bucket.arn, "/*"),
            ]
        }],
    }),
    opts=pulumi.ResourceOptions(
        depends_on=[public_access_block],
    ),
)

aws.s3.BucketObject(
    "index.html",
    bucket=bucket.bucket,
    source=pulumi.FileAsset("www/index.html"),
    content_type="text/html",
)

pulumi.export("url", pulumi.Output.concat("http://", bucket.website_endpoint))
