# Querying the GitHub archive with the ClickHouse playground

Via [this comment](https://news.ycombinator.com/item?id=34197637) on Hacker News I started exploring the [ClickHouse Playground](https://clickhouse.com/docs/en/getting-started/playground/). It's really cool, and among other things it allows CORS-enabled API hits that can query a decade of history from the GitHub events archive in less than a second.

## ClickHouse

[ClickHouse](https://clickhouse.com/) is an open source column-oriented database, originally developed at Yandex but spun out into a separate, VC-funded company in 2021. It's designed for big data analytical queries - in a similar space to HBase, BigQuery and DuckDB.

It turns out it can do that trick with HTTP range queries where you can point it at the URL to a Parquet or `.native.zst` file (ClickHouse native format, optionally compressed using [Facebook Zstandard](https://github.com/facebook/zstd)) and run queries without downloading the entire file first.

## Exploring the Playground

The ClickHouse Playground is a free hosted environment for trying out ClickHouse. You can access it here:

https://play.clickhouse.com/play?user=play

Try this query, taken from the [ClickHouse Everything You Always Wanted To Know
About GitHub (But Were Afraid To Ask)](https://ghe.clickhouse.tech/) tutorial:

```sql
SELECT count() FROM github_events WHERE event_type = 'WatchEvent'
```

<img width="834" alt="The playground interface says Elapsed: 0.043 sec, read 341.54 million rows, 341.54 MB - and returns a count() of 341429632" src="https://user-images.githubusercontent.com/9599/210161204-5ec2c8fa-3d22-44f7-b95d-5d5f71bdce8a.png">

## github_events

The `github_events` table contains a copy of the [GH Archive](https://www.gharchive.org/) - a project that archives and makes available the public GitHub timeline, I think using data from the [public events API](https://docs.github.com/en/rest/activity/events?apiVersion=2022-11-28#list-public-events). GH Archive then makes that data available as compressed newline-delimited JSON in [this bucket](https://data.gharchive.org/). The archive stretches back to February 2011, and is constantly updated.

The ClickHouse demo table is continually updated with the latest archived data, by [this script](https://github.com/ClickHouse/github-explorer/blob/main/update.sh), which runs every 10 minutes.

You can do all sorts of fun stuff with it. Here's my recent activity acrosss all of GitHub:

```sql
SELECT
  created_at,
  actor_login,
  repo_name,
  event_type,
  title
FROM
  github_events
WHERE
  actor_login = 'simonw'
  AND repo_name != 'simonw/disaster-data'
ORDER BY
  created_at DESC
LIMIT
  100
```
[This link](https://play.clickhouse.com/play?user=play#U0VMRUNUCiAgY3JlYXRlZF9hdCwKICBhY3Rvcl9sb2dpbiwKICByZXBvX25hbWUsCiAgZXZlbnRfdHlwZSwKICB0aXRsZQpGUk9NCiAgZ2l0aHViX2V2ZW50cwpXSEVSRQogIGFjdG9yX2xvZ2luID0gJ3NpbW9udycKICBBTkQgcmVwb19uYW1lICE9ICdzaW1vbncvZGlzYXN0ZXItZGF0YScKT1JERVIgQlkKICBjcmVhdGVkX2F0IERFU0MKTElNSVQKICAxMDA=) executes that query.

There are 77 tables total in the Playground instance - you can get a list of them like this:
```sql
SELECT database, name FROM system.tables
```

## API access

You can access the API via `curl` like this:

```bash
curl 'https://play.clickhouse.com/' \
  -X POST \
  -H 'Authorization: Basic cGxheTo=' \
  --data-raw $'
    SELECT created_at, actor_login, repo_name
    FROM github_events
    WHERE event_type = \'WatchEvent\'
    ORDER BY created_at DESC LIMIT 100'
```
This defaults to returning TSV without column headers, like this:
```tsv
2023-01-01 03:59:59	Willmac16	nlohmann/json
2023-01-01 03:59:59	Samrose-Ahmed	Stebalien/stash-rs
2023-01-01 03:59:57	CodePromoter	aplus-framework/image
```
To get back data in JSON instead, add `?default_format=JSON` to the URL. Here I'm piping that through `jq` to pretty print it:
```bash
curl 'https://play.clickhouse.com/?default_format=JSON' \
  -X POST \
  -H 'Authorization: Basic cGxheTo=' \
  --data-raw $'
    SELECT created_at, actor_login, repo_name
    FROM github_events
    WHERE event_type = \'WatchEvent\'
    ORDER BY created_at DESC LIMIT 1' | jq
```
Output:
```json
{
  "meta": [
    {
      "name": "created_at",
      "type": "DateTime"
    },
    {
      "name": "actor_login",
      "type": "LowCardinality(String)"
    },
    {
      "name": "repo_name",
      "type": "LowCardinality(String)"
    }
  ],
  "data": [
    {
      "created_at": "2023-01-01 03:59:59",
      "actor_login": "Willmac16",
      "repo_name": "nlohmann/json"
    }
  ],
  "rows": 1,
  "rows_before_limit_at_least": 341429632,
  "statistics": {
    "elapsed": 0.925636889,
    "rows_read": 341540363,
    "bytes_read": 10567093585
  }
}
```
More format options [are documented here](https://clickhouse.com/docs/en/interfaces/formats/).

## CORS requests from JavaScript

This pattern works for running queries from JavaScript. CORS is enabled - I pasted this into the Firefox DevTools console on https://www.example.com/ and it returned the results I expected:

```javascript
r = await fetch("https://play.clickhouse.com/?user=play", {
  method: "POST",
  body: `SELECT
        created_at,
        event_type,
        actor_login,
        repo_name,
        number,
        title,
        body
      FROM
        github_events
      WHERE
         actor_login = 'simonw'
      ORDER BY
        created_at desc
      LIMIT
        100
      FORMAT JSON`,
});
d = await r.json();
```
Here I'm using `FORMAT JSON` at the end of the query itself, and passing the requested user as `?user=play` rather than sending an `Authorization` header.
