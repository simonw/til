# Publishing to a public Google Cloud bucket with gsutil

I decided to publish static CSV files to accompany my https://cdc-vaccination-history.datasette.io/ project, using a Google Cloud bucket (see [cdc-vaccination-history issue #9](https://github.com/simonw/cdc-vaccination-history/issues/9)).

The Google Cloud tutorial on [https://cloud.google.com/storage/docs/hosting-static-website-http#gsutil](https://cloud.google.com/storage/docs/hosting-static-website-http#gsutil) was very helpful.

## Creating the bucket

I used an authenticated `gsutil` session that I already had from my work with Google Cloud Run.

To create a new bucket:

    gsutil mb gs://cdc-vaccination-history-csv.datasette.io/

`mb` is the [make bucket](https://cloud.google.com/storage/docs/gsutil/commands/mb) command.

I had already verified my `datasette.io` bucket with Google, otherwise this step would not have worked.

## Uploading files

    gsutil cp *.csv gs://cdc-vaccination-history-csv.datasette.io

Using the [gsutil cp command](https://cloud.google.com/storage/docs/gsutil/commands/cp).

## Making them available to the public

This command allows anyone to download from the bucket:

    gsutil iam ch allUsers:objectViewer gs://cdc-vaccination-history-csv.datasette.io

## DNS

I configured `cdc-vaccination-history-csv` as a `CNAME` pointing to `c.storage.googleapis.com.`

https://cdc-vaccination-history-csv.datasette.io/ now shows an XML directory listing.
