# Export a Mastodon timeline to SQLite

I've been playing around with [the Mastodon timelines API](https://docs.joinmastodon.org/methods/timelines/). It's pretty fun!

I'm [running my own instance](https://til.simonwillison.net/mastodon/custom-domain-mastodon) which means I don't feel limited by politeness in terms of rate limits - if I'm just using my own instance's resources I feel fine hammering it.

Many instances (including mine) expose a public timeline API. You can use that to request all "local" posts on the server - since my server only has one user (me) that's all of my stuff.

That API starts here: https://fedi.simonwillison.net/api/v1/timelines/public?local=1

If you fetch it through `curl -i` to include headers you'll spot some interesting headers:

```
$ curl -s -i 'https://fedi.simonwillison.net/api/v1/timelines/public?local=1'
...
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 294
X-RateLimit-Reset: 2022-11-05T00:40:00.971772Z
Cache-Control: no-store
Vary: Accept, Accept-Encoding, Origin
Link: <https://fedi.simonwillison.net/api/v1/timelines/public?local=1&max_id=109277272598366124>; rel="next", <https://fedi.simonwillison.net/api/v1/timelines/public?local=1&min_id=109288139761544382>; rel="prev"
```
The rate limit stuff is cool, but the thing that instantly caught my eye was the `Link:` header. It looks like Mastodon implements cursor-based pagination in that header.

I just so happen to have written a tool for working with that kind of header! [paginate-json](https://github.com/simonw/paginate-json), which fetches every page by following those `rel="next"` links until they run out.

Here's how to download everything from that feed and save it to a single newline-delimited JSON file (the `--nl` option):

```
paginate-json 'https://fedi.simonwillison.net/api/v1/timelines/public?local=1' --nl > /tmp/simon.json
```
Output:
```
https://fedi.simonwillison.net/api/v1/timelines/public?local=1
20
https://fedi.simonwillison.net/api/v1/timelines/public?local=1&max_id=109277272598366124
20
https://fedi.simonwillison.net/api/v1/timelines/public?local=1&max_id=109276505589113334
20
https://fedi.simonwillison.net/api/v1/timelines/public?local=1&max_id=109276498877771086
13
https://fedi.simonwillison.net/api/v1/timelines/public?local=1&max_id=109276387855048126
0
```
And here's how to load the resulting file into a SQLite database using `sqlite-utils`, which also supports [newline-delimited JSON](https://sqlite-utils.datasette.io/en/stable/cli.html#inserting-newline-delimited-json):

    cat /tmp/simon.json | sqlite-utils insert /tmp/simon.db posts - --pk id --nl --replace

The `--pk id` option sets the primary key on the newly created `posts` table to `id`. The `--replace` option means any records that clash with an existing ID will be replaced - this means I can safely run the command multiple times.

I can even combine the two commands like this:
```
paginate-json 'https://fedi.simonwillison.net/api/v1/timelines/public?local=1' --nl \
  | sqlite-utils insert /tmp/simon.db posts - --pk id --nl --replace
```
The result is a SQLite database!

[Here it is in Datasette Lite](https://lite.datasette.io/?url=https%3A%2F%2Fgist.githubusercontent.com%2Fsimonw%2F2f021a5155a8b251c5959e8eaa4af299%2Fraw%2F6711f2d2f314c875118d0c7f51ca080e8306b081%2Fdemo.db#/demo/posts) as a demo.
