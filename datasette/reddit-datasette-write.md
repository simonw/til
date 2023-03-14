# Scraping Reddit and writing data to the Datasette write API

Today I built a system for monitoring Reddit for new posts that link to various domains that I own.

I modelled it on my existing [scrape-hacker-news-by-domain](https://github.com/simonw/scrape-hacker-news-by-domain) project, which I described in some detail in [this blog post](https://simonwillison.net/2022/Dec/2/datasette-write-api/).

The goal of the Reddit scraper was to do the following:

1. Frequently check Reddit for new links to any page on `simonwillison.net` or `datasette.io`, using the unofficial search API - the Reddit search page with `.json` appended to the URL.
2. Record the results to a GitHub repository
3. Submit any new results to my personal Datasette Cloud instance via the Write API
4. Use [datasette-atom](https://datasette.io/plugins/datasette-atom) to provide a feed of new posts I can subscribe to in netNewsWire

## The scraper

Not much to say about the scraper. It looks like this:
```bash
curl -H $USER_AGENT \
  'https://www.reddit.com/search/.json?q=site%3Asimonwillison.net&sort=new' \
  | jq > simonwillison-net.json
```
Where `USER_AGENT` is set to this, because Reddit doesn't like `curl` hitting it with the default agent:

    User-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36

The HTML version of this page is https://www.reddit.com/search/?q=site%3Asimonwillison.net&sort=new

It then repeats the same thing for `datasette.io` and commits the results. The code lives in this scheduled GitHub Actions file: https://github.com/simonw/scrape-reddit-by-domain/blob/main/.github/workflows/scrape.yml

## Creating the table

I created myself a Datasette signed API token with full permissions that would expire after five minutes using the `/-/create-token` interface.

I set that as an environment variable like so:

```bash
export DS_TOKEN='dstok_...'
```

Then I ran this to create the table and populate it with some initial data:

```bash
cat simonwillison-net.json | jq '{
  table: "reddit_posts",
  rows: [.data.children[].data | {
    id,
    subreddit,
    title,
    url,
    ups,
    num_comments,
    created_utc: (.created_utc | todateiso8601),
    subreddit_subscribers,
    domain,
    permalink: ("https://www.reddit.com" + .permalink)
  }],
  pk: "id"
}' | \
  curl -X POST -H "Content-Type: application/json" \
    -H "Authorization: Bearer $DS_TOKEN" \
    -d @- https://simon.datasette.cloud/data/-/create
```

This uses `jq` to extract the bits of the JSON I care about and reformat them into a smaller set of colunms. It constructs a JSON document that matches that expected by the `/-/create` API, [documented here](https://docs.datasette.io/en/1.0a2/json_api.html#creating-a-table-from-example-data).

(I used ChatGPT to figure out that `jq` recipe, in particular the `| todateiso8601` part.)

It pipes the resulting JSON to `curl` and makes an authenticated POST request to the `/-/create` API. This created the `reddit_posts` table and populated it with the initial data.

## Submitting new rows from GitHub Actions

With the table created, I could now create a long-lived API token that would allow me to write to the table.

I used the `/-/create-token` interface again but this time I created a token that would never expire but that only had write and alter permission to the new `reddit_posts` table I had just created.

I wrote the following script to submit all rows from all JSON files in the current directory:

```bash
#!/bin/bash
for file in *.json
do
  cat $file | jq '{
  rows: [.data.children[].data | {
    id,
    subreddit,
    title,
    url,
    ups,
    num_comments,
    created_utc: (.created_utc | todateiso8601),
    subreddit_subscribers,
    domain,
    permalink: ("https://www.reddit.com" + .permalink)
  }],
  replace: true
}' | \
  curl -X POST -H "Content-Type: application/json" \
    -H "Authorization: Bearer $DS_TOKEN" \
    -d @- https://simon.datasette.cloud/data/reddit_posts/-/insert
done
```
This uses the `/-/insert` API instead, which is a little different from the `/-/create` API. It doesn't take a `table` argument, instead expecting the table name to be part of the URL.

I also send `replace: true` - this ensures that any existing rows with a primary key that matches incoming data will be replaced by the updated version.

I ran `chmod 755 submit-to-datasette-cloud.sh` and added it to the GitHub repository.

## Running it in GitHub Actions

Having set the `DS_TOKEN` secret for my repository, I added the following to the `scrape.yml` file:

```yaml
    - name: Submit latest to Datasette Cloud
      env:
        DS_TOKEN: ${{ secrets.DS_TOKEN }}
      run: |-
        ./submit-to-datasette-cloud.sh
```
Now every time the workflow runs (once an hour) any new records will be submitted up to Datasette Cloud.

## Configuring the Atom feed

I used the [datasette-public](https://datasette.io/plugins/datasette-public) plugin to make the `reddit_posts` table public. You can see that here:

https://simon.datasette.cloud/data/reddit_posts

Then I used the [datasette-write](https://datasette.io/plugins/datasette-write) plugin to create a SQL view defined like this:

```sql
create view reddit_posts_atom as select
  'reddit:' || id as atom_id,
  title as atom_title,
  permalink as atom_link,
  created_utc as atom_updated,
  '<a href="' || url || '">' || url || '</a><br><br>'
  || 'Subreddit: ' || subreddit || '<br>'
  || 'Comments: ' || num_comments || '<br>'
  || 'Upvotes: ' || ups || '<br>'
  || 'Subscribers: ' || subreddit_subscribers as atom_content_html
from
  reddit_posts
order by
  created_utc desc
limit
  100;
```
This follows the conventions required by the [datasette-atom](https://datasette.io/plugins/datasette-atom) plugin.

I made that view public too, and now you can visit it here:

https://simon.datasette.cloud/data/reddit_posts_atom

Or subscribe to the Atom feed here:

https://simon.datasette.cloud/data/reddit_posts_atom.atom
