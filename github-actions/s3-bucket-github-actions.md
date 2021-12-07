# Storing files in S3 bucket between GitHub Actions runs

For my [git-history live demos](https://github.com/simonw/git-history/issues/30) I needed to store quite large files (~200MB SQLite databases) in between GitHub Actions runs, to avoid having to recreate the entire file from scratch every time.

## Creating the bucket and credentials

I used my [s3-credentials](https://github.com/simonw/s3-credentials) tool to create an S3 bucket with permanent, locked-down credentials.

```
~ % s3-credentials create git-history-demos --public --create-bucket
Created bucket: git-history-demos
Attached bucket policy allowing public access
Created  user: 's3.read-write.git-history-demos' with permissions boundary: 'arn:aws:iam::aws:policy/AmazonS3FullAccess'
Attached policy s3.read-write.git-history-demos to user s3.read-write.git-history-demos
Created access key for user: s3.read-write.git-history-demos
{
    "UserName": "s3.read-write.git-history-demos",
    "AccessKeyId": "AKIAWXFXAIOZOLWKY4FP",
    "Status": "Active",
    "SecretAccessKey": “…”,;
    "CreateDate": "2021-12-07 07:11:48+00:00"
}
```
I saved the new access key and secret key to `SECRETS` in my repository called `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.

## Downloading the files as part of the Actions workflow

Since I used `--public` to create the bucket, I could download files inside the action like this:

    curl -o ca-fires.db https://s3.amazonaws.com/git-history-demos/ca-fires.db

If I had not used `--public` I could use `s3-credentials get-object` instead:

    s3-credentials get-object git-history-demos ca-fires.db -o ca-fires.db

I would need to expose the secrets as environment variables first, see below.

I actually wanted to attempt the download but keep running if the file was not there, because in this case my scripts will generate the file from scratch if it's not already in the bucket. I used this pattern for that:

```yaml
    - name: Download ca-fires.db
      run: curl --fail -o ca-fires.db https://s3.amazonaws.com/git-history-demos/ca-fires.db
      continue-on-error: true
```

## Uploading the files to the bucket

My step to upload the generated files to the bucket looks like this:

```yaml
    - name: Upload databases to S3
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      run: |-
        s3-credentials put-object git-history-demos pge-outages.db pge-outages.db
        s3-credentials put-object git-history-demos ca-fires.db ca-fires.db
        s3-credentials put-object git-history-demos sf-bay-511.db sf-bay-511.db
```
Here I'm passing through the repository secrets as environment variables that `s3-credentials put-object` can then use.

Full workflow is here: https://github.com/simonw/git-history/blob/main/.github/workflows/deploy-demos.yml
