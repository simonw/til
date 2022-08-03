# Using boto3 from the command line

I found a useful pattern today for automating more complex AWS processes as pastable command line snippets, using [Boto3](https://aws.amazon.com/sdk-for-python/).

The trick is to take advantage of the fact that `python3 -c '...'` lets you pass in a multi-line Python string which will be executed directly.

I used that to create a new IAM role by running the following:
```bash
python3 -c '
import boto3, json

iam = boto3.client("iam")
create_role_response = iam.create_role(
    Description=("Description of my role"),
    RoleName="my-new-role",
    AssumeRolePolicyDocument=json.dumps(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": "arn:aws:iam::462092780466:user/s3.read-write.my-previously-created-user"
                    },
                    "Action": "sts:AssumeRole",
                }
            ],
        }
    ),
    MaxSessionDuration=12 * 60 * 60,
)
# Attach AmazonS3FullAccess to it - note that even though we use full access
# on the role itself any time we call sts.assume_role() we attach an additional
# policy to ensure reduced access for the temporary credentials
iam.attach_role_policy(
    RoleName="my-new-role",
    PolicyArn="arn:aws:iam::aws:policy/AmazonS3FullAccess",
)
print(create_role_response["Role"]["Arn"])
'
```
