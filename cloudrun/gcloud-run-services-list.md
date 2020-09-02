# Using the gcloud run services list command

The `gcloud run services list` command lists your services running on Google Cloud Run:

```
~ % gcloud run services list --platform=managed
   SERVICE                        REGION       URL                                                            LAST DEPLOYED BY                                              LAST DEPLOYED AT
✔  calands                        us-central1  https://calands-j7hipcg4aq-uc.a.run.app                        ...@gmail.com                                           2020-09-02T00:15:29.563846Z
✔  cloud-run-hello                us-central1  https://cloud-run-hello-j7hipcg4aq-uc.a.run.app                ...@gmail.com                                           2020-09-02T00:16:07.835843Z
✔  covid-19                       us-central1  https://covid-19-j7hipcg4aq-uc.a.run.app                       ...@gmail.com                                           2020-09-02T00:16:46.979188Z
...
```

It has two useful but under-documented options: `--filter` which filters based on a special filter language, and `--format` which customizes the output format.

## --filter

I found the `--filter` option really hard to figure out. It has [documentation here](https://cloud.google.com/sdk/gcloud/reference/topic/filters) describing the predicate language it uses, but I had to apply trial and error to find options that worked for `gcloud run services`. Here are a few I found.

To see data for just one specific service by name, use `--filter=SERVICE:covid-19`. Lowercase `service` doesn't work for some reason.

```
~ % gcloud run services list --platform=managed --filter=SERVICE:covid-19
   SERVICE   REGION       URL                                       LAST DEPLOYED BY     LAST DEPLOYED AT
✔  covid-19  us-central1  https://covid-19-j7hipcg4aq-uc.a.run.app  ...@gmail.com  2020-09-02T00:16:46.979188Z
```

To filter by labels that you have set on your services, use `--filter="metadata.labels.name=value"`. It took me a while to figure out I needed the `metadata.` prefix here.

Here's a filter for every service that does NOT have a label called `service` (I apply a label of 'service' to all of my services so I can [see them separately in billing](https://til.simonwillison.net/til/til/cloudrun_use-labels-for-billing-breakdown.md)).

```
gcloud run services list --platform=managed --filter='NOT metadata.labels.service:*'
```

## --format

The `--format` option is [documented here](https://cloud.google.com/sdk/gcloud/reference/topic/formats). Here's what I've worked out.

`gcloud run services list --platform=managed --format=json` outputs JSON. `--format=yaml` outputs YAML.

Two more interesting ones are `--format='table(colums go here)'` and `--format='csv(columns go here)'`. For example:
```
~ % gcloud run services list --platform=managed --format='table(SERVICE,URL)'
SERVICE                        URL
calands                        https://calands-j7hipcg4aq-uc.a.run.app
covid-19                       https://covid-19-j7hipcg4aq-uc.a.run.app
```

Or for CSV:
```
~ % gcloud run services list --platform=managed --format='csv(SERVICE,URL)'
service,url
calands,https://calands-j7hipcg4aq-uc.a.run.app
covid-19,https://covid-19-j7hipcg4aq-uc.a.run.app
```
Other values I found that work include `REGION`, `labels` and `metadata`. The latter two output a not-valid-JSON (possibly Python `repr()`) nested structure:
```
~ % gcloud run services list --platform=managed --format='table(SERVICE,labels,metadata)' --filter=SERVICE:covid-19
SERVICE   LABELS                                                                   METADATA
covid-19  {'service': 'covid-19', 'cloud.googleapis.com/location': 'us-central1'}  {'annotations': {'client.knative.dev/user-image': 'gcr.io/datasette-222320/datasette', 'run.googleapis.com/client-name': 'gcloud', 'run.googleapis.com/client-version': '302.0.0', 'serving.knative.dev/creator': 'swillison@gmail.com', 'serving.knative.dev/lastModifier': 'swillison@gmail.com'}, 'creationTimestamp': '2020-03-10T18:47:04.923274Z', 'generation': 670, 'labels': {'cloud.googleapis.com/location': 'us-central1', 'service': 'covid-19'}, 'name': 'covid-19', 'namespace': '99025868001', 'resourceVersion': 'AAWuSY0eaHQ', 'selfLink': '/apis/serving.knative.dev/v1/namespaces/99025868001/services/covid-19', 'uid': '6ff64723-a38d-4784-ac5e-07a745061845'}
```

