# Writing Fly logs to S3

[Fly](https://fly.io/) offers [fly-log-shipper](https://github.com/superfly/fly-log-shipper) as a container you can run in a Fly application to send all of the logs from your other applications to a logging provider.

Several providers are supported. I decided to write them to an S3 bucket.

## Bucket credentials

I used my [s3-credentials](https://github.com/simonw/s3-credentials) tool to generate an access key and secret locked down to just one newly created bucket:

```
s3-credentials create my-project-fly-logs \
  --format ini \
  --bucket-region us-west-1 \
  --create-bucket \
  > logging-credentials.txt
```
I chose `us-west-1` or Northern California as the region, as it is closest to me.

That command output the following:

```
Created bucket: my-project-fly-logs in region: us-west-1
Created  user: 's3.read-write.my-project-fly-logs' with permissions boundary: 'arn:aws:iam::aws:policy/AmazonS3FullAccess'
Attached policy s3.read-write.my-project-fly-logs to user s3.read-write.my-project-fly-logs
Created access key for user: s3.read-write.my-project-fly-logs
```

The full set of configuration needed by `fly-log-shipper` for S3 is:

- `ORG` - Fly organisation slug
- `ACCESS_TOKEN` - Fly personal access token
- `AWS_ACCESS_KEY_ID`	- AWS Access key with access to the log bucket
- `AWS_SECRET_ACCESS_KEY` - AWS secret access key
- `AWS_BUCKET` - AWS S3 bucket to store logs in
- `AWS_REGION` - Region for the bucket

I created a personal access token at https://fly.io/user/personal_access_tokens

## Creating the app

I created a new Fly application to run the container like so:

    fly apps create --name my-project-log-shipper --org my-project-org

## Setting the secrets

I set all of the configuration variables as secrets in one go like this:
```
fly secrets set \
  ORG="my-project-org" \
  ACCESS_TOKEN="..." \
  AWS_ACCESS_KEY_ID="AKIAWXFXAIOZIPTTHMBQ" \
  AWS_SECRET_ACCESS_KEY="..." \
  AWS_BUCKET="my-project-fly-logs" \
  AWS_REGION="us-west-1" \
  -a my-project-shipper
```

## Deploying the app

It turns out you still need a `fly.toml` file to successfully deploy - I tried without and got healthcheck errors.

Here's the TOML file I used:

```toml
app = "my-project-log-shipper"

[metrics]
  port = 9598
  path = "/metrics"
```

Then I passed that to the `fly deploy` command like this:

```
fly deploy --image ghcr.io/superfly/fly-log-shipper:v0.0.1 -a my-project-log-shipper -c fly.toml
```
Output:
```
==> Verifying app config
--> Verified app config
==> Building image
Searching for image 'ghcr.io/superfly/fly-log-shipper:v0.0.1' locally...
Searching for image 'ghcr.io/superfly/fly-log-shipper:v0.0.1' remotely...
image found: img_19gm46rqwn14x0jk
==> Creating release
--> release v1 created

--> You can detach the terminal anytime without stopping the deployment
==> Monitoring deployment

 1 desired, 1 placed, 1 healthy, 0 unhealthy
--> v1 deployed successfully
```
I used [Transmit](https://panic.com/transmit/) to inspect the bucket and my logs are showing up there as intended.

I can also now list my log files using `s3-credentials list-bucket` and the credentials I saved earlier:

```
% s3-credentials list-bucket -a logging-credentials.txt my-project-fly-logs --csv 
Key,LastModified,ETag,Size,StorageClass,Owner
my-project-admin/2022-05-25//1653507279-b9534d49-546a-47cb-bd93-36e08b8457ee.log.gz,2022-05-25 19:34:40+00:00,"""8b499f523bd2f5e9438cf2c0d42eab8c""",335,STANDARD,
my-project-admin/2022-05-25//1653507625-fc3c0f32-b3e8-4681-98ce-a4fe2960d1b2.log.gz,2022-05-25 19:40:26+00:00,"""5fe1f6fbf747706930edcfd00e3dd4fe""",444,STANDARD,
my-project-admin/2022-05-25//1653508693-7f4da568-e462-46a2-9904-e3ac801c7fee.log.gz,2022-05-25 19:58:14+00:00,"""794c57787a692a17d1fbfb78df442d58""",353,STANDARD,
my-project-postgresql/2022-05-25//1653507222-60e072e2-fd78-437f-a097-c063df424224.log.gz,2022-05-25 19:33:43+00:00,"""5d9965b79260e6a0f27cff5f02eee71d""",3376,STANDARD,
my-project-postgresql/2022-05-25//1653507525-b3a04523-8732-4072-92c0-57dd06a680b1.log.gz,2022-05-25 
```
