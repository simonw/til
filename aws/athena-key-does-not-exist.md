# Athena error: The specified key does not exist

I was trying to run Athena queries against compressed JSON log files stored in an S3 bucket.

No matter what I tried, I got the following error:

> The specified key does not exist. (Service: Amazon S3; Status Code: 404; Error Code: NoSuchKey; Request ID: 4GHB3YX6DQHYTCPF; S3 Extended Request ID: 0LSAhwbo21RaZ+8/FOgKf1oh+dIkV0WO8DvtYmwQdBzddfILchiSyamFLenD8IOmrN+lDPxKTFP/7my0DKbVvw==; Proxy: null), S3 Extended Request ID: 0LSAhwbo21RaZ+8/FOgKf1oh+dIkV0WO8DvtYmwQdBzddfILchiSyamFLenD8IOmrN+lDPxKTFP/7my0DKbVvw== (Path: s3://my-logs-bucket/my-fly-app/2022-05-27/1653693921-a96e5844-02db-4e3e-9e9a-3eef00910271.log.gz)

This is using the Fly log shipping recipe [described here previously](https://til.simonwillison.net/fly/fly-logs-to-s3).

I couldn't find any search results online for this error in the context of Athena.

After much head scratching... I spotted that the files in my bucket had keys that looked like this:

- `my-fly-app/2022-05-27//1653693921-a96e5844-02db-4e3e-9e9a-3eef00910271.log.gz`

Note that there's a `//` after the date instead of a `/`. But in the error message from Athena the same key is identified as `my-fly-app/2022-05-27/1653693921-a96e5844-02db-4e3e-9e9a-3eef00910271.log.gz` - without the double slash.

It looks like Athena has a bug where it can't read files with `//` in their key!

The fix was to first fix my log shipper so that it wrote files without that prefix. Upgrading to the most recent version in the Fly repo seemed to handle that.

Then I needed to rename all of my existing keys. This wasn't easy: S3 doesn't have a bulk rename operation, so I ended up having to run a script that looked like this:

```bash
aws s3 --recursive mv \
  s3://my-logs-bucket/my-fly-app/2022-08-28// \
  s3://my-logs-bucket/my-fly-app//2022-08-28/

aws s3 --recursive mv \
  s3://my-logs-bucket/my-fly-app//2022-09-23// \
  s3://my-logs-bucket/my-fly-app//2022-09-23/
```
With a command for every single one of my folders that were mis-named.

Having done this, Athena started working against my bucket!
