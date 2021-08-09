# Tailing Google Cloud Run request logs and importing them into SQLite

The `gcloud` CLI tool has [the alpha ability to tail log files](https://cloud.google.com/logging/docs/reference/tools/gcloud-logging#live-tailing) - but it's a bit of a pain to setup.

You have to install two extras for it. First, this:

    gcloud alpha logging tail

That installs the functionality, but as the documentation will tell you:

> To use `gcloud alpha logging tail`, you need to have Python 3 and the `grpcio` Python package installed.

Assuming you have Python 3, the problem you have to solve is *which Python* is the `gcloud` tool using to run. After digging around in the source code using `cat $(which gcloud)` I spotted the following:

    CLOUDSDK_PYTHON=$(order_python python3 python2 python2.7 python)

So it looks like (on macOS at least) it prefers to use the `python3` binary if it can find it.

So this works to install `grpcio` somewhere it can see it:

    python3 -m pip install grpcio

Having done that, you can start running commands. `gcloud logging logs list` shows a list of logs:

```
~ % gcloud logging logs list
NAME
projects/datasette-222320/logs/cloudaudit.googleapis.com%2Factivity
projects/datasette-222320/logs/cloudaudit.googleapis.com%2Fdata_access
projects/datasette-222320/logs/cloudaudit.googleapis.com%2Fsystem_event
projects/datasette-222320/logs/cloudbuild
projects/datasette-222320/logs/clouderrorreporting.googleapis.com%2Finsights
projects/datasette-222320/logs/cloudtrace.googleapis.com%2FTraceLatencyShiftDetected
projects/datasette-222320/logs/run.googleapis.com%2Frequests
projects/datasette-222320/logs/run.googleapis.com%2Fstderr
projects/datasette-222320/logs/run.googleapis.com%2Fstdout
projects/datasette-222320/logs/run.googleapis.com%2Fvarlog%2Fsystem
```
Then you can use `gcloud alpha logging tail projects/datasette-222320/logs/run.googleapis.com%2Frequests` to start logging. Only you also need a `CLOUDSDK_PYTHON_SITEPACKAGES=1` environment variable so that `gcloud` knows to look for the `grpcio` dependency.

    CLOUDSDK_PYTHON_SITEPACKAGES=1 \
      gcloud alpha logging tail projects/datasette-222320/logs/run.googleapis.com%2Frequests

The default format is verbose YAML. A log entry looks like this:

```yaml
httpRequest:
  latency: 0.123684963s
  remoteIp: 66.249.69.240
  requestMethod: GET
  requestSize: '510'
  requestUrl: https://www.niche-museums.com/browse/museums.json?_facet_size=max&country=United+States&_facet=osm_city&_facet=updated&_facet=osm_suburb&_facet=osm_footway&osm_city=Santa+Cruz
  responseSize: '6403'
  serverIp: 142.250.125.121
  status: 200
  userAgent: Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)
insertId: 611171fe000a38a469d59595
labels:
  instanceId: 00bf4bf02dab164592dbbb9220b56c3ce64cb0f1c1f37812d1d61e851a931e9964ba539c2ede42886773c82662cc28aa858749d2697f537ff7a61e7b
  service: niche-museums
logName: projects/datasette-222320/logs/run.googleapis.com%2Frequests
receiveTimestamp: '2021-08-09T18:20:46.935658405Z'
resource:
  labels:
    configuration_name: niche-museums
    location: us-central1
    project_id: datasette-222320
    revision_name: niche-museums-00039-sur
    service_name: niche-museums
  type: cloud_run_revision
severity: INFO
timestamp: '2021-08-09T18:20:46.669860Z'
trace: projects/datasette-222320/traces/306a0d6e7e055ba66172003a74c926c2
```

I decided to import into a SQLite database so I could use [Datasette](https://datasette.io/) to analyze the log files (hooray for facets).

Adding `--format json` switches the output to JSON - but it's a pretty-printed array of JSON objects, something like this:

```json
[
  {
    "httpRequest": {
      "latency": "0.112114537s",
      "remoteIp": "40.77.167.88",
      "requestMethod": "GET",
      "requestSize": "534",
      "requestUrl": "https://datasette.io/content/repos?forks=0&_facet=homepage&_facet=size&_facet=open_issues&open_issues=3&size=564&_sort=readme_html",
      "responseSize": "72757",
      "serverIp": "216.239.38.21",
      "status": 200,
      "userAgent": "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"
    },
    "insertId": "6111722f000b5b4c4d4071e2",
    "labels": {
      "instanceId": "00bf4bf02d1d7fe4402c3aff8a34688d9a910e6ee6d2545ceebc1edefb99461481e6d9f9ae8de4e907e3d18b98ea9c7f57b2abb527c8857d9163ed193db766c349a1ee",
      "service": "datasette-io"
    },
    "logName": "projects/datasette-222320/logs/run.googleapis.com%2Frequests",
    "receiveTimestamp": "2021-08-09T18:21:36.061693305Z",
    "resource": {
      "labels": {
        "configuration_name": "datasette-io",
        "location": "us-central1",
        "project_id": "datasette-222320",
        "revision_name": "datasette-io-00416-coy",
        "service_name": "datasette-io"
      },
      "type": "cloud_run_revision"
    },
    "severity": "INFO",
    "timestamp": "2021-08-09T18:21:35.744268Z",
    "trace": "projects/datasette-222320/traces/016d640caf845fbf8709486bc8dff9c7"
  }
]
```

I want to stream the logs into `sqlite-utils` using [newline-delimited JSON](https://sqlite-utils.datasette.io/en/stable/cli.html#inserting-newline-delimited-json) since that can insert while the data is still being tailed.

I ended up using two new `jq` recipes:

    cat example.json | jq -cn --stream 'fromstream(1|truncate_stream(inputs))'

This turns an `[{"array": "of objects"}, {"like": "this one"}]` into a stream of newline-delimited objects. I [found the recipe here](https://github.com/stedolan/jq/issues/1984#issuecomment-568918146) - I don't understand it.

As you can see above, the objects are nested. I want them as flat objects so that `sqlite-utils insert` will create a separate column for each nested value. I used [this recipe](https://til.simonwillison.net/jq/flatten-nested-json-objects-jq) for that.

The end result was this:

```
CLOUDSDK_PYTHON_SITEPACKAGES=1 gcloud alpha logging tail \
  projects/datasette-222320/logs/run.googleapis.com%2Frequests \
  --format json \
| jq -cn --stream 'fromstream(1|truncate_stream(inputs))' \
| jq -c '[leaf_paths as $path | {
  "key": $path | join("_"), "value": getpath($path)
}] | from_entries' \
| sqlite-utils insert /tmp/logs.db logs - --nl --alter --batch-size 1
```
That last line inserts the data into the `/tmp/logs.db` database file. `--nl` means "expect newline-delimited JSON", `--alter` means "add new columns if they are missing", `--batch-size 1` means "commit after every record" (so I can see them in Datasette while they are streaming in).

The resulting schema looks like this (via `sqlite-utils schema /tmp/logs.db`):
```sql
CREATE TABLE [logs] (
   [httpRequest_latency] TEXT,
   [httpRequest_remoteIp] TEXT,
   [httpRequest_requestMethod] TEXT,
   [httpRequest_requestSize] TEXT,
   [httpRequest_requestUrl] TEXT,
   [httpRequest_responseSize] TEXT,
   [httpRequest_serverIp] TEXT,
   [httpRequest_status] INTEGER,
   [httpRequest_userAgent] TEXT,
   [insertId] TEXT,
   [labels_instanceId] TEXT,
   [labels_service] TEXT,
   [logName] TEXT,
   [receiveTimestamp] TEXT,
   [resource_labels_configuration_name] TEXT,
   [resource_labels_location] TEXT,
   [resource_labels_project_id] TEXT,
   [resource_labels_revision_name] TEXT,
   [resource_labels_service_name] TEXT,
   [resource_type] TEXT,
   [severity] TEXT,
   [timestamp] TEXT,
   [trace] TEXT,
   [httpRequest_referer] TEXT
);
```

Then I ran `datasette /tmp/logs.db` to start exploring the logs. Faceting by `resource_labels_service_name` was particularly useful.

<img width="1340" alt="Screenshot of logs in Datasette" src="https://user-images.githubusercontent.com/9599/128755995-fab7e478-82a5-4d80-a959-f89f7dd39209.png">

The `httpRequest_latency` column contains text data that looks like `0.012572683s` - thankfully if you cast it to a `float` the trailing `s` will be ignored. Here's an example query showing the services with the highest average latency:

```sql
select
  resource_labels_service_name,
  avg(cast(httpRequest_latency as float)) as avg_latency,
  count(*)
from
  logs
group by
  resource_labels_service_name
order by
  avg_latency desc
```
