# How to deploy a folder with a Dockerfile to Cloud Run

I deployed https://metmusem.datasettes.com/ by creating a folder on my computer containing a Dockerfile and then shipping that folder up to Google Cloud Run.

Normally I use [datasette publish cloudrun](https://docs.datasette.io/en/stable/publish.html#publishing-to-google-cloud-run) to deploy to Cloud Run, but in this case I decided to do it by hand.

I created a folder and dropped two files into it: a `Dockerfile` and a `metadata.json`. BUT... this trick would work with more files in the same directory - it uploads the entire directory contents to be built by Google's cloud builder.

`Dockerfile`
```dockerfile
FROM python:3.6-slim-stretch
RUN apt update
RUN apt install -y python3-dev gcc wget
ADD metadata.json metadata.json
RUN wget -q "https://static.simonwillison.net/static/2018/MetObjects.db"
RUN pip install datasette
RUN datasette inspect MetObjects.db --inspect-file inspect-data.json

EXPOSE $PORT

CMD datasette serve MetObjects.db --host 0.0.0.0 --cors --port $PORT --inspect-file inspect-data.json -m metadata.json
```
The `PORT` is provided by Cloud Run. It's 8080 but they may change that in the future, so it's best to use an environment variable.

Here's the `metadata.json`:
```json
{
    "title": "The Metropolitan Museum of Art Open Access",
    "source": "metmuseum/openaccess",
    "source_url": "https://github.com/metmuseum/openaccess",
    "license": "CC0",
    "license_url": "https://creativecommons.org/publicdomain/zero/1.0/"
}
```
Finally here's my `deploy.sh` script which I used to run the deploy. This needs to be run from within that directory:
```bash
#!/bin/bash
NAME="metmuseum"
PROJECT=$(gcloud config get-value project)
IMAGE="gcr.io/$PROJECT/$NAME"

gcloud builds submit --tag $IMAGE
gcloud run deploy --allow-unauthenticated --platform=managed --image $IMAGE $NAME --memory 2Gi
```
Before running the script I had installed the Cloud Run SDK and run `gcloud init` to login.

The `NAME` variable ends up being used as the name of both my built image and my service. This needs to be unique in your Cloud Run account, or your deploy will over-write an existing service.

Cloud Run deployed my site to https://metmuseum-j7hipcg4aq-uc.a.run.app/

I then used the "Domain mappings" feature in the Cloud Run web console to point a better web address at it.
