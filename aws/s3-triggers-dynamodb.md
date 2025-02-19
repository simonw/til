# Using S3 triggers to maintain a list of files in DynamoDB

This is a three-quarters-baked experiment that I ran this morning. I'm interested in efficiently tracking which new files have been added to an S3 bucket, where that bucket could potentially hold millions of items.

Frustratingly S3 doesn't offer an API for listing files that have been updated since a specific date - you have to do a full paginated listing of every file in the bucket every time.

Could this be solved using S3 triggers, where a lambda function runs for every change to the bucket and writes the results somewhere else?

I was curious to see if this could work, so I decided to build a protoype using Claude, ChatGPT and o3-mini-high.

I *hate* figuring out AWS things, but I've recently found that most of the modern LLMs have a deep knowledge of the key AWS APIs, thanks to their tendency to stay stable over a multi-year time period.

Which means I can learn AWS by getting LLMs to write custom one-off tools for me!

## v1 using Claude

I started by prompting my [Claude Python app Project](https://simonwillison.net/2024/Dec/19/one-shot-python-tools/) with the following:

> Python CLI app using boto3 with commands for creating a new S3 bucket which it also configures to have S3 lambada event triggers which moantian a dynamodb table containing metadata about all of the files in that bucket. Include these commands
>
> - create_bucket - create a bucket and sets up the associated triggers and dynamo tables
> - list_files - shows me a list of files based purely on querying dynamo

I've never used S3 lambda triggers _or_ DynamoDB, so this was a fun new experiment!

Claude [gave me a script that looked convincing](https://gist.github.com/simonw/8588decba2e539b1d392c60ce0755a8e#create-s3-manager-with-dynamodb-metadata) - it ran the following steps:

- Create a new S3 bucket with the specified name
- Create a DynamoDB table called `"{bucket_name}-metadata"` with a `bucket_key` string primary key ("KeySchema" in DynamoDB terminology)
- Create a Lambda role with (presumably) the correct policies attached
- Create a new Lambda function, implemented in Python, that updates DynamoDB
- Set that function to trigger on `["s3:ObjectCreated:*", "s3:ObjectRemoved:*"]` bucket notification events

On reading the script more closely though I spotted what looked like a bug: it was sending the raw Python code to Lamba as the `Code={'ZipFile': lambda_code}` parameter, and I was pretty sure that was meant to be a zip file.

## v2 using ChatGPT and o3-mini-high

Rather than continuing to wrestle with Claude (which probably would have worked) I decided to switch models and dump the whole thing into ChatGPT's o3-mini-high model and tell it to identify and fix any bugs:

> Identify, explain and then fix any bugs in this code:
>
> *code from Claude pasted here*

Here's [the transcript](https://chatgpt.com/c/67b635b9-170c-8006-b9c3-dea6d61b3f88). It "reasoned" for 1 minute and 9 seconds and then spat out the following (full code to follow at the end):

> Below is one acceptable answer. In our original code there were three main issues:
> 
> 1. **Lambda Code Not Packaged as a ZIP Archive**  
>    The AWS Lambda API (when using the `ZipFile` parameter) expects a ZIP archive containing your function code (with the file name matching your handler, e.g. “lambda_function.py”). In the original code the raw text was encoded with `.encode()`, which does not create a ZIP file.  
>    **Fix:** Use Python’s `zipfile` (with an in‑memory buffer via `io.BytesIO`) to package the code as a ZIP archive before uploading.
> 
> 2. **Missing Permission for S3 to Invoke the Lambda Function**  
>    S3 bucket notifications will not work unless the Lambda function’s resource policy allows S3 to invoke it. In the original code no permission was granted to S3.  
>    **Fix:** Call `lambda_client.add_permission` with the proper parameters (including a statement ID, the action `"lambda:InvokeFunction"`, principal `"s3.amazonaws.com"`, and the source ARN for your bucket).
> 
> 3. **Region Mismatch for AWS Clients**  
>    The command-line option “--region” is used when creating the S3 bucket but not for other resources (Lambda and DynamoDB are created using the default region). This can lead to resources being created in different regions.  
>    **Fix:** Instantiate all regional boto3 clients with the same region (by using the `region_name` parameter) and pass the region value (or create a context) so that all API calls are in the intended region.
> 
> The fixed code below incorporates these changes:
> 
> *code removed, full code to follow*
> 
> ### Explanation
> 
> - **ZIP Packaging:**  
>   In the function `create_lambda_function`, we now create a ZIP archive in memory:
>   ```python
>   zip_buffer = io.BytesIO()
>   with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
>       zip_file.writestr('lambda_function.py', lambda_code)
>   zip_buffer.seek(0)
>   zip_bytes = zip_buffer.read()
>   ```
>   This archive is then passed in `Code={'ZipFile': zip_bytes}` so that AWS Lambda receives a proper deployment package.
> 
> - **Lambda Permission:**  
>   In the `create_bucket` command we add:
>   ```python
>   lambda_client.add_permission(
>       FunctionName=function_name,
>       StatementId=f"{bucket_name}-s3invoke",
>       Action="lambda:InvokeFunction",
>       Principal="s3.amazonaws.com",
>       SourceArn=f"arn:aws:s3:::{bucket_name}"
>   )
>   ```
>   This allows S3 (identified by its ARN) to invoke the Lambda function.
> 
> - **Region Consistency:**  
>   The CLI now takes a global option “--region” (with default `'us-east-1'`). Every boto3 client that is regional (S3, Lambda, DynamoDB) is created with that region so that all resources are created in the same region.
> 
> This version fixes the bugs noted above and is one correct way to resolve the issues in the original code.

It spotted and fixed the ZipFile issue I identified, and it looks like it found a couple of other issues worth fixing too.

I ran the code that it gave me... and it *almost* worked! I got this error:

```
Created bucket: simon-magic-bucket-2
Created DynamoDB table: simon-magic-bucket-2-metadata
Created/using IAM role: simon-magic-bucket-2-lambda-role
Error: An error occurred (InvalidParameterValueException) when calling the CreateFunction operation: The role defined for the function cannot be assumed by Lambda.
Aborted!
```
I pasted that error message back into o3-mini-high, it "reasoned" for another 8 seconds and suggested that I add `time.sleep(10)` after creating the role to allow it time to propagate.

(I eventually added another `time.sleep(5)` elsewhere for a similar reason.)

## The finished script

All of that combined together gave me the following script - which works! I saved it as `magic_bucket.py`:

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click",
#     "boto3",
# ]
# ///

import json
import click
import boto3
import io
import zipfile
from typing import Optional
import time

# IAM is global since it is a global service
iam = boto3.client("iam")


def create_lambda_role(role_name: str) -> str:
    """Create IAM role for Lambda function with necessary permissions."""
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }

    try:
        response = iam.create_role(
            RoleName=role_name, AssumeRolePolicyDocument=json.dumps(trust_policy)
        )

        # Attach necessary policies
        policy_arns = [
            "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
            "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
            "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess",
        ]

        for policy_arn in policy_arns:
            iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)

        return response["Role"]["Arn"]
    except iam.exceptions.EntityAlreadyExistsException:
        return iam.get_role(RoleName=role_name)["Role"]["Arn"]


def create_lambda_function(
    function_name: str, role_arn: str, table_name: str, region: str
) -> str:
    """Create Lambda function to process S3 events and update DynamoDB."""
    # Note the use of double braces to escape inner curly braces so that the final code has proper f-string syntax.
    lambda_code = f"""
import json
import boto3
import urllib.parse
from datetime import datetime

dynamodb = boto3.client('dynamodb')
s3 = boto3.client('s3')

def lambda_handler(event, context):
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(record['s3']['object']['key'])
        size = record['s3']['object'].get('size', 0)
        event_time = record.get('eventTime', '')
        event_name = record.get('eventName', '')
        
        if event_name.startswith('ObjectCreated'):
            # Get additional metadata from S3
            response = s3.head_object(Bucket=bucket, Key=key)
            content_type = response.get('ContentType', 'unknown')
            
            # Store in DynamoDB
            dynamodb.put_item(
                TableName='{table_name}',
                Item={{
                    'bucket_key': {{'S': f'{{bucket}}/{{key}}'}},
                    'filename': {{'S': key}},
                    'bucket': {{'S': bucket}},
                    'size': {{'N': str(size)}},
                    'content_type': {{'S': content_type}},
                    'last_modified': {{'S': event_time}},
                    'timestamp': {{'S': datetime.utcnow().isoformat()}}
                }}
            )
        elif event_name.startswith('ObjectRemoved'):
            # Remove from DynamoDB
            dynamodb.delete_item(
                TableName='{table_name}',
                Key={{
                    'bucket_key': {{'S': f'{{bucket}}/{{key}}'}}
                }}
            )
    
    return {{
        'statusCode': 200,
        'body': json.dumps('Successfully processed S3 event')
    }}
"""
    # Package the lambda code as a ZIP archive in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr("lambda_function.py", lambda_code)
    zip_buffer.seek(0)
    zip_bytes = zip_buffer.read()

    lambda_client = boto3.client("lambda", region_name=region)

    try:
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime="python3.12",
            Role=role_arn,
            Handler="lambda_function.lambda_handler",
            Code={"ZipFile": zip_bytes},
            Timeout=30,
            MemorySize=128,
            Environment={"Variables": {"DYNAMODB_TABLE": table_name}},
        )
        return response["FunctionArn"]
    except lambda_client.exceptions.ResourceConflictException:
        return lambda_client.get_function(FunctionName=function_name)["Configuration"][
            "FunctionArn"
        ]


def create_dynamodb_table(table_name: str, region: str):
    """Create DynamoDB table for storing file metadata."""
    dynamodb = boto3.client("dynamodb", region_name=region)
    try:
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "bucket_key", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "bucket_key", "AttributeType": "S"}
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        waiter = dynamodb.get_waiter("table_exists")
        waiter.wait(TableName=table_name)
    except dynamodb.exceptions.ResourceInUseException:
        pass


@click.group()
@click.option("--region", default="us-east-1", help="AWS region for the resources")
@click.pass_context
def cli(ctx, region):
    """Manage S3 buckets with DynamoDB metadata tracking."""
    ctx.ensure_object(dict)
    ctx.obj["REGION"] = region


@cli.command()
@click.argument("bucket_name")
@click.pass_context
def create_bucket(ctx, bucket_name: str):
    """Create a new S3 bucket with Lambda triggers and DynamoDB table."""
    region = ctx.obj["REGION"]
    s3 = boto3.client("s3", region_name=region)
    lambda_client = boto3.client("lambda", region_name=region)

    try:
        # Create S3 bucket
        if region == "us-east-1":
            s3.create_bucket(Bucket=bucket_name)
        else:
            s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={"LocationConstraint": region},
            )
        click.echo(f"Created bucket: {bucket_name}")

        # Create DynamoDB table
        table_name = f"{bucket_name}-metadata"
        create_dynamodb_table(table_name, region)
        click.echo(f"Created DynamoDB table: {table_name}")

        # Create Lambda function
        role_name = f"{bucket_name}-lambda-role"
        role_arn = create_lambda_role(role_name)
        click.echo(f"Created/using IAM role: {role_name} - wait 10s for it to be ready")
        time.sleep(10)

        function_name = f"{bucket_name}-processor"
        lambda_arn = create_lambda_function(function_name, role_arn, table_name, region)
        click.echo(f"Created Lambda function: {function_name}")

        # Grant S3 permission to invoke the Lambda function
        try:
            lambda_client.add_permission(
                FunctionName=function_name,
                StatementId=f"{bucket_name}-s3invoke",
                Action="lambda:InvokeFunction",
                Principal="s3.amazonaws.com",
                SourceArn=f"arn:aws:s3:::{bucket_name}",
            )
        except lambda_client.exceptions.ResourceConflictException:
            # Permission already exists
            pass

        time.sleep(5)

        # Add bucket notification configuration
        s3.put_bucket_notification_configuration(
            Bucket=bucket_name,
            NotificationConfiguration={
                "LambdaFunctionConfigurations": [
                    {
                        "LambdaFunctionArn": lambda_arn,
                        "Events": ["s3:ObjectCreated:*", "s3:ObjectRemoved:*"],
                    }
                ]
            },
        )
        click.echo("Configured S3 event notifications")

        click.echo("\nSetup completed successfully!")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()


@cli.command()
@click.argument("bucket_name")
@click.option("--prefix", help="Filter files by prefix")
@click.option("--region", default="us-east-1", help="AWS region for the resources")
def list_files(bucket_name: str, prefix: Optional[str], region: str):
    """List files in the bucket using DynamoDB metadata."""
    dynamodb = boto3.client("dynamodb", region_name=region)
    table_name = f"{bucket_name}-metadata"

    try:
        # Scan DynamoDB table
        scan_kwargs = {
            "TableName": table_name,
        }

        if prefix:
            scan_kwargs["FilterExpression"] = "begins_with(filename, :prefix)"
            scan_kwargs["ExpressionAttributeValues"] = {":prefix": {"S": prefix}}

        response = dynamodb.scan(**scan_kwargs)

        if not response.get("Items"):
            click.echo("No files found.")
            return

        # Print file information
        click.echo("\nFiles in bucket:")
        click.echo("-" * 80)
        format_str = "{:<40} {:>10} {:<20} {:<20}"
        click.echo(
            format_str.format("Filename", "Size (B)", "Content Type", "Last Modified")
        )
        click.echo("-" * 80)

        for item in response["Items"]:
            click.echo(
                format_str.format(
                    item["filename"]["S"],
                    item["size"]["N"],
                    item["content_type"]["S"],
                    item["last_modified"]["S"],
                )
            )

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    cli()
```
## Trying it out

I ran it with `uv` like this - the `/// script` block ensured that `uv` ran it with the `click` and `boto3` dependencies it needed:

```bash
uv run magic_bucket.py create-bucket simon-magic-bucket-6
```
```
Created bucket: simon-magic-bucket-6
Created bucket: simon-magic-bucket-6
Created DynamoDB table: simon-magic-bucket-6-metadata
Created/using IAM role: simon-magic-bucket-6-lambda-role - wait 10s for it to be ready
Created Lambda function: simon-magic-bucket-6-processor
Configured S3 event notifications

Setup completed successfully!
```
Now I can list the files in the bucket according to the DynamoDB table:
```bash
uv run magic_bucket.py list-files simon-magic-bucket-6
```
```
No files found.
```
Then upload some files using my existing [s3-credentials put-objects](https://s3-credentials.readthedocs.io/en/latest/other-commands.html#put-objects) tool:
```bash
uvx s3-credentials put-objects simon-magic-bucket-6 /tmp/*.gif
```
Wait a few seconds for the triggers to fire and:
```bash
uv run magic_bucket.py list-files simon-magic-bucket-6
```
```
Files in bucket:
--------------------------------------------------------------------------------
Filename                                   Size (B) Content Type         Last Modified       
--------------------------------------------------------------------------------
tab.gif                                      107141 binary/octet-stream  2025-02-19T21:30:03.860Z
tweak.gif                                    268411 binary/octet-stream  2025-02-19T21:30:04.649Z
my-image.gif                                 714735 binary/octet-stream  2025-02-19T21:30:03.423Z
```
I've since [saved the file on GitHub](https://github.com/simonw/tools/blob/main/python/magic_bucket.py), which means anyone with `uv` installed (and their AWS credentials configured on their machine) can run it like this:
```bash
uv run https://raw.githubusercontent.com/simonw/tools/refs/heads/main/python/magic_bucket.py \
  create-bucket name-your-magic-bucket-here
```
## Potential next steps

This is a very solid proof of concept: I've conclusively proven to myself that this approach can work and is feasible using the tools I have at hand.

There's actually not much left before I would consider putting it in production. Off the top of my head:

- The trigger right now only tracks `"s3:ObjectCreated:*"` and `"s3:ObjectRemoved:*"` - is there an equivalent for if an object is updated? Claude says that an update is treated as an `ObjectCreated` event as well so probably not but there might be other events I want to track.
- I'd really like to get some automated testing in place for something like this. A CI job that creates a new bucket, adds some files, waits a bit, checks that the DynamoDB table was populated and then cleans up at the end would give me more confidence in the system going forward.
- If I ever use this properly I'll turn it into a Python package with a GitHub repo, issues, a changelog etc.
- Is DynamoDB the best choice for this? I'd like to spend a little more time thinking through the project rather than assuming that my first guesses were the most appropriate architecture here.

Honestly though I feel like this prototype got me 90% of the way there already.

## Bonus TIL: deleting an S3 bucket with uvx

I wanted to clean up after myself, so I figured out how to run the `aws` CLI command via `uvx` like this:

```bash
uvx --with awscli aws s3 rb s3://simon-magic-bucket-6 --force
```
The `--force` option allows this to work even with buckets that aren't empty - it deletes each key first before deleting the bucket.
