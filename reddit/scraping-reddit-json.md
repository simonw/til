# Scraping Reddit via their JSON API

Reddit have long had an unofficial (I think) API where you can add `.json` to the end of any URL to get back the data for that page as JSON.

I wanted to track new posts on Reddit that mention my domain `simonwillison.net`.

https://www.reddit.com/domain/simonwillison.net/new/ shows recent posts from a specific domain.

https://www.reddit.com/domain/simonwillison.net/new.json is that data as JSON, which looks like this:

```json
{
  "kind": "Listing",
  "data": {
    "modhash": "la6xmexs8u301d6d105d24f94cdaa4457a00a1ea042c95f6e2",
    "dist": 25,
    "children": [
      {
        "kind": "t3",
        "data": {
          "approved_at_utc": null,
          "subreddit": "programming",
          "selftext": "",
          "author_fullname": "t2_2ks9",
          "saved": false,
          "mod_reason_title": null,
          "gilded": 0,
          "clicked": false,
          "title": "Joining CSV and JSON data with an in-memory SQLite database",
          "link_flair_richtext": [],
          "subreddit_name_prefixed": "r/programming"
```
Attempting to fetch this data with `curl` shows an error:
```
$ curl 'https://www.reddit.com/domain/simonwillison.net/new.json'
{"message": "Too Many Requests", "error": 429}
```
Turns out this rate limiting is [based on user-agent](https://www.reddit.com/r/redditdev/comments/3qbll8/429_too_many_requests/) - so to avoid it, set a custom user-agent:

```
$ curl --user-agent 'simonw/fetch-reddit' 'https://www.reddit.com/domain/simonwillison.net/new.json'
{"kind": "Listing", "data": ...
```
I used `jq` to tidy this up like so:

```jq
[.data.children[] | .data |  {
  id: .id,
  subreddit: .subreddit,
  url: .url,
  created_utc: .created_utc | todate,
  permalink: .permalink,
  num_comments: .num_comments
}]
```
Combined:
```
$ curl \
  --user-agent 'simonw/fetch-reddit' \
  'https://www.reddit.com/domain/simonwillison.net/new.json' \
  | jq '[.data.children[] | .data |  {
    id: .id,
    subreddit: .subreddit,
    url: .url,
    created_utc: .created_utc | todate,
    permalink: .permalink,
    num_comments: .num_comments
  }]' > simonwillison-net.json
```
Output looks like this:
```json
[
  {
    "id": "o3tjsx",
    "subreddit": "programming",
    "url": "https://simonwillison.net/2021/Jun/19/sqlite-utils-memory/",
    "created_utc": "2021-06-20T00:25:51Z",
    "permalink": "/r/programming/comments/o3tjsx/joining_csv_and_json_data_with_an_inmemory_sqlite/",
    "num_comments": 10
  },
  {
    "id": "nnsww6",
    "subreddit": "patient_hackernews",
    "url": "https://til.simonwillison.net/bash/finding-bom-csv-files-with-ripgrep",
    "created_utc": "2021-05-29T18:04:38Z",
    "permalink": "/r/patient_hackernews/comments/nnsww6/finding_csv_files_that_start_with_a_bom_using/",
    "num_comments": 1
  }
]
```
