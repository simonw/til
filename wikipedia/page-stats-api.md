# The Wikipedia page stats API

Via https://alexgarcia.xyz/dataflow/examples/wiki-pageviews/ I found this API for retrieving daily pageview stats from Wikipedia for any article:

- https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/user/Python_(programming_language)/daily/20210101/20210501
- https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia.org/all-access/user/Simon_Willison/daily/20210101/20210501

Example response:

```json
{
  "items": [
    {
      "project": "en.wikipedia",
      "article": "Python_(programming_language)",
      "granularity": "daily",
      "timestamp": "2021010100",
      "access": "all-access",
      "agent": "user",
      "views": 7238
    },
    {
      "project": "en.wikipedia",
      "article": "Python_(programming_language)",
      "granularity": "daily",
      "timestamp": "2021010200",
      "access": "all-access",
      "agent": "user",
      "views": 8449
    },
    {
      "project": "en.wikipedia",
      "article": "Python_(programming_language)",
      "granularity": "daily",
      "timestamp": "2021010300",
      "access": "all-access",
      "agent": "user",
      "views": 8669
    }
  ]
}
```
