# Deploying Python web apps as AWS Lambda functions

I've been wanting to figure out how to do this for years. Today I finally put all of the pieces together for it.

[AWS Lambda](https://aws.amazon.com/lambda/) can host functions written in Python. These are "scale to zero" - my favourite definition of serverless! - which means you only pay for the traffic that they serve. A project with no traffic costs nothing to run.

You used to have to jump through a whole bunch of extra hoops to get a working URL that triggered those functions, but in April 2022 they [released Lambda Function URLs](https://aws.amazon.com/blogs/aws/announcing-aws-lambda-function-urls-built-in-https-endpoints-for-single-function-microservices/) and dramatically simplified that process.

There are still a lot of steps involved though. Here's how to deploy a Python web application as a Lambda function.

## Set up the AWS CLI tool

I did this so long ago I can't remember how. You need an AWS account and you need to have the [AWS CLI tool](https://aws.amazon.com/cli/) installed and configured.

The `aws --version` should return a version number of `1.22.90` or higher, as [that's when they added function URL support](https://github.com/simonw/help-scraper/commit/d217b9d7f44a1200d0582d02aeccf27e006b8b78).

I found I had too old a version of the tool. I ended up figuring out this as the way to upgrade it:

```bash
head -n 1 $(which aws)
```
Output:
```
#!/usr/local/opt/python@3.9/bin/python3.9
```
This showed me the location of the Python environment that contained the tool. I could then edit that path to upgrade it like so:
```bash
/usr/local/opt/python@3.9/bin/pip3 install -U awscli
```
## Create a Python handler function

This is "hello world" as a Python handler function. Put it in `lambda_function.py`:

```python
def lambda_handler(event, context): 
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/html"
        },
        "body": "<h1>Hello World from Python</h1>"
    }
```

## Add that to a zip file

This is the part of the process that I found most unintuitive. Lambda functions are deployed as zip files. The zip file needs to contain both the Python code AND all of its dependencies - more on that to come.

Our first function doesn't have any dependencies, which makes things a lot easier. Here's how to turn it into a zip file ready to be deployed:
```bash
zip function.zip lambda_function.py
```
## Create a role with a policy

You only have to do this the first time you deploy a Lambda function. You need an IAM role that you can use for the other steps.

This command creates a role called `lambda-ex`:
```
aws iam create-role \
  --role-name lambda-ex \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"}
    ]}'
```
Then you have to run this. I don't know why this can't be handled as part of the `create-role` command, but it's necessary:
```
aws iam attach-role-policy \
  --role-name lambda-ex \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

## Find your AWS account ID

You need to know your AWS account ID for the next step.

You can find it by running this command:
```bash
aws sts get-caller-identity \
  --query "Account" --output text
```
I assigned it to an environment variable so I could use it later like this:
```bash
export AWS_ACCOUNT_ID=$(
  aws sts get-caller-identity \
  --query "Account" --output text
)
```
Run this to confirm that worked:
```bash
echo $AWS_ACCOUNT_ID
```

## Deploy that function

Now we can deploy the zip file as a new Lambda function!

Pick a unique function name - I picked `lambda-python-hello-world`.

Then run the following:
```bash
aws lambda create-function \
  --function-name lambda-python-hello-world \
  --zip-file fileb://function.zip \
  --runtime python3.9 \
  --handler "lambda_function.lambda_handler" \
  --role "arn:aws:iam::${AWS_ACCOUNT_ID}:role/lambda-ex"
```
We're telling it to deploy our `function.zip` file using the `python3.9` runtime.

We list `lambda_function.lambda_handler` as the handler because our Python file was called `lambda_function.py` and the function was called `lambda_handler`.

If all goes well you should get back a response from that command that looks something like this:

```json
{
    "FunctionName": "lambda-python-hello-world",
    "FunctionArn": "arn:aws:lambda:us-east-1:462092780466:function:lambda-python-hello-world",
    "Runtime": "python3.9",
    "Role": "arn:aws:iam::462092780466:role/lambda-ex",
    "Handler": "lambda_function.lambda_handler",
    "CodeSize": 332,
    "Description": "",
    "Timeout": 3,
    "MemorySize": 128,
    "LastModified": "2022-09-19T02:27:18.213+0000",
    "CodeSha256": "Y1nCZLN6KvU9vUmhHAgcAkYfvgu6uBhmdGVprq8c97Y=",
    "Version": "$LATEST",
    "TracingConfig": {
        "Mode": "PassThrough"
    },
    "RevisionId": "316481f5-7934-4e54-914f-6b075bb7d9dd",
    "State": "Pending",
    "StateReason": "The function is being created.",
    "StateReasonCode": "Creating",
    "PackageType": "Zip",
    "Architectures": [
        "x86_64"
    ],
    "EphemeralStorage": {
        "Size": 512
    }
}
```

## Grant permission for it to be executed

This magic command is also necessary for everything to work:

```bash
aws lambda add-permission \
  --function-name lambda-python-hello-world \
  --action lambda:InvokeFunctionUrl \
  --principal "*" \
  --function-url-auth-type "NONE" \
  --statement-id url
```

## Give it a Function URL

We need a URL that we can access in a browser to trigger our function.

Here's how to add a new Function URL to our deployed function:

```
aws lambda create-function-url-config \
  --function-name lambda-python-hello-world \
  --auth-type NONE
```

That `--auth-type NONE` means anyone on the internet will be able to trigger the function by visiting the URL.

This should return something like the following:

```json
{
    "FunctionUrl": "https://m2jatdfy4bulhvsfcrfc6sfw2i0bjfpx.lambda-url.us-east-1.on.aws/",
    "FunctionArn": "arn:aws:lambda:us-east-1:462092780466:function:lambda-python-hello-world",
    "AuthType": "NONE",
    "CreationTime": "2022-09-19T02:27:48.356967Z"
}
```
And sure enough, https://m2jatdfy4bulhvsfcrfc6sfw2i0bjfpx.lambda-url.us-east-1.on.aws/ now returns "Hello World from Python".

## Updating the function

Having deployed the function, updating it is pleasantly easy.

You create a new `function.zip` file - which I do like this:

```bash
rm -f function.zip # Delete if it exists
zip function.zip lambda_function.py 
```
And then deploy the update like so:
```bash
aws lambda update-function-code \
  --function-name lambda-python-hello-world \
  --zip-file fileb://function.zip
```

## Adding pure Python dependencies

Adding dependencies to the project was by far the most confusing aspect of this whole process.

Eventually I found a [good way to do it](https://github.com/pixegami/fastapi-tutorial/blob/4ec9247faf53e4c399ea18a4ac27c0e85a137955/README.md#deploying-fastapi-to-aws-lambda) thanks to the example code published to accompany [this YouTube video](https://www.youtube.com/watch?v=RGIM4JfsSk0) by Pixegami.

The trick is to include ALL of your depndencies _in the root of your zip file_.

Forget about `requirements.txt` and suchlike - you need to install copies of the actual dependencies themselves.

Here's the recipe that works for me. First, create a `requirements.txt` file listing your dependencies:

```
cowsay
```

Now use the `pip install -t` command to install those requirements into a specific directory - I use `lib`:
```bash
python3 -m pip install -t lib -r requirements.txt
```
Run `ls -lah lib` to confirm that the files are in there.
```
ls lib | cat
```
```
bin
cowsay
cowsay-5.0-py3.10.egg-info
```
Now use this recipe to add everything in `lib` to the root of your zip file:
```bash
(cd lib; zip ../function.zip -r .)
```
You can run this command to see the list of files in the zip:
```bash
unzip -l function.zip
```

Let's update `lambda_function.py` to demonstrate the `cowsay` library:
```python
import cowsay


def lambda_handler(event, context): 
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "text/plain"
        },
        "body": cowsay.get_output_string("pig", "Hello world, I am a pig")
    }
```
Add that updated `lambda_function.py` to the zip file again:
```bash
zip function.zip lambda_function.py
```
Deploy the update:
```
aws lambda update-function-code \
  --function-name lambda-python-hello-world \
  --zip-file fileb://function.zip
```
Hit refresh on the URL from earlier and you should see:
```
  _______________________
| Hello world, I am a pig |
  =======================
                       \
                        \
                         \
                          \
                                    ,.
                                   (_|,.
                                   ,' /, )_______   _
                               __j o``-'        `.'-)'
                               (")                 \'
                               `-j                |
                                 `-._(           /
                                    |_\  |--^.  /
                                   /_]'|_| /_)_/
                                       /_]'  /_]'
```
## Advanced Python dependencies

The above recipe works fine for dependencies that are written only in Python.

Where things get more complicated is when you want to use a dependency that includes native code.

I use a Mac. If I run `pip install -t lib -r requirements.txt` I'll get the Mac versions of those dependencies.

But AWS Lambda functions run on Amazon Linux. So we need to include version of our packages that are built for that platform in our zip file.

I first had to do this because I realized the `python3.9` Lambda runtime includes a truly ancient version of SQLite - version 3.7.17 [from 2013-05-20](http://www.sqlite.org/releaselog/3_7_17.html).

The [pysqlite3-binary](https://pypi.org/project/pysqlite3-binary/) package provides a much more recent SQLite, and [Datasette](https://datasette.io/) uses that automatically if it's installed.

I figured the best way to do this would be to run the `pip install` command inside an Amazon Linux Docker container. After much head scratching, I came up with this recipe for doing that:
```bash
docker run -t -v $(pwd):/mnt \
  public.ecr.aws/sam/build-python3.9:latest \
  /bin/sh -c "pip install -r /mnt/requirements.txt -t /mnt/lib"
```

- The `-v $(pwd):/mnt` flag mounts the current directory as `/mnt` inside the container.
- The `public.ecr.aws/sam/build-python3.9:latest` image is the official AWS Lambda Python 3.9 image.
- `/bin/sh -c "pip install -r /mnt/requirements.txt -t /mnt/lib"` runs `pip install` inside the container, but ensures the files are written to `/mnt/lib` which is the `lib` folder in our current directory.

This recipe works! The result is a `lib/` folder full of Amazon Linux Python packages, ready to be zipped up and deployed.

## Running an ASGI application

I want to deploy [Datasette](https://datasette.io/).

Datasetet is an [ASGI application](https://simonwillison.net/2019/Jun/23/datasette-asgi/).

But... AWS Lambda functions have their own weird interface to HTTP - the `event` and `context` parameters shown above.

[Mangum](https://github.com/jordaneremieff/mangum) is a well regarded library that bridges the gap between the two.

Here's how I got Datasette and Mangum working. It was surprisingly straight-forward!

I added the following to my `requirements.txt` file:

```
datasette
pysqlite3-binary
mangum
```
I deleted my `lib` folder:
```
rm -rf lib
```
Then I ran the magic incantation from above:

```bash
docker run -t -v $(pwd):/mnt \
  public.ecr.aws/sam/build-python3.9:latest \
  /bin/sh -c "pip install -r /mnt/requirements.txt -t /mnt/lib"
```
I added the dependencies to a new `function.zip` file:
```bash
rm -rf function.zip
(cd lib; zip ../function.zip -r .)
```
Then I added the following to `lambda_function.py`:
```python
import asyncio
from datasette.app import Datasette
import mangum


ds = Datasette(["fixtures.db"])
# Handler wraps the Datasette ASGI app with Mangum:
lambda_handler = mangum.Mangum(ds.app())
```
I added that to the zip:
```
zip function.zip lambda_function.py
```
Finally, I grabbed a copy of the standard Datasette `fixtures.db` database file and added that to the zip as well:

```bash
wget https://latest.datasette.io/fixtures.db
zip function.zip fixtures.db
```
The finished `function.zip` is 7.1MB. Time to deploy it:
```
aws lambda update-function-code \
  --function-name lambda-python-hello-world \
  --zip-file fileb://function.zip
```
This did the trick! I now had a Datasette instance running on Lambda.

The default Lambda configuration only provides 128MB of RAM, and I was getting occasional timeout errors. Bumping that up to 256MB fixed the problem:

```bash
aws lambda update-function-configuration \
  --function-name lambda-python-hello-world \
  --memory-size 256
```
## This should work for Starlette and FastAPI too

Mangum works with ASGI apps, so any app built using [Starlette](https://www.starlette.io/) or [FastAPI](https://fastapi.tiangolo.com/) should work exactly the same way.

## Pretty URLs

One thing I haven't figured out yet is how to assign a custom domain name to a Lambda function. I understand doing that involves several other AWS services, potentially Cloudfront and Rouh53. I'll update this once I figure those out.
