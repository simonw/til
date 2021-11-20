# Using build-arg variables with Cloud Run deployments

For [datasette/issues/1522](https://github.com/simonw/datasette/issues/1522) I wanted to use a Docker build argument in a `Dockerfile` that would then be deployed to Cloud Run.

I needed this to be able to control the version of Datasette that was deployed. Here's my simplified `Dockerfile`:

```dockerfile
FROM python:3-alpine

ARG DATASETTE_REF
# Copy to environment variable for use in CMD later
ENV VERSION_NOTE=$DATASETTE_REF

RUN pip install https://github.com/simonw/datasette/archive/${DATASETTE_REF}.zip

# Need to use "shell form" here to get variable substition:
CMD datasette -h 0.0.0.0 -p 8080 --version-note $VERSION_NOTE
```
I can build this on my laptop like so:

    docker build -t datasette-build-arg-demo . \
      --build-arg DATASETTE_REF=c617e1769ea27e045b0f2907ef49a9a1244e577d

Then run it like this:

    docker run -p 5000:8080 --rm datasette-build-arg-demo

And visit `http://localhost:5000/-/versions` to see the version number to confirm it worked.

I wanted to deploy this to Cloud Run, using [this recipe](https://til.simonwillison.net/cloudrun/ship-dockerfile-to-cloud-run).

Unfortunately, the `gcloud builds submit` command doesn't have a mechanism for specifying `--build-arg`.

Instead, you need to use a YAML file and pass it with the `gcloud builds submit --config cloudbuild.yml` option. The YAML should look like this:

```yaml
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gc.io/MY-PROJECT/MY-NAME', '.', '--build-arg', 'DATASETTE_REF=c617e1769ea27e045b0f2907ef49a9a1244e577d']
- name: 'gcr.io/cloud-builders/docker'
  args: ['push', $IMAGE]
```

Since I want to dynamically populate my YAML file, I ended up using the following pattern in a `./deploy.sh` script:

```bash
#!/bin/bash
# https://til.simonwillison.net/cloudrun/using-build-args-with-cloud-run

if [[ -z "$DATASETTE_REF" ]]; then
    echo "Must provide DATASETTE_REF environment variable" 1>&2
    exit 1
fi

NAME="datasette-apache-proxy-demo"
PROJECT=$(gcloud config get-value project)
IMAGE="gcr.io/$PROJECT/$NAME"

# Need YAML so we can set --build-arg
echo "
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', '$IMAGE', '.', '--build-arg', 'DATASETTE_REF=$DATASETTE_REF']
- name: 'gcr.io/cloud-builders/docker'
  args: ['push', '$IMAGE']
" > /tmp/cloudbuild.yml

gcloud builds submit --config /tmp/cloudbuild.yml

rm /tmp/cloudbuild.yml

gcloud run deploy $NAME \
  --allow-unauthenticated \
  --platform=managed \
  --image $IMAGE \
  --port 80
```
