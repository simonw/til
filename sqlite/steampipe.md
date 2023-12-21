# Running Steampipe extensions in sqlite-utils and Datasette

[Steampipe](https://steampipe.io/) build software that lets you query different APIs directly from SQL databases.

Their original product only worked with PostgreSQL, but last week [they announced](https://steampipe.io/blog/2023-12-sqlite-extensions) new support for SQLite, with ports of 100 of their existing extensions.

That's 100 new SQLite extensions released into the world at the same time!

Here's the [full list of SQLite extensions](https://hub.steampipe.io/plugins?engines=sqlite) they released.

You can install and use these via their CLI tool, but they also make them available as `.so` files directly via GitHub releases.

Here's how to run those on a Mac, using both [sqlite-utils](https://sqlite-utils.datasette.io/) and [Datasette](https://datasette.io/).

## Downloading an extension

Let's start with the Hacker News API plugin, [turbot/steampipe-plugin-hackernews](https://github.com/turbot/steampipe-plugin-hackernews). I like this one because it doesn't require an API key.

First grab the [latest release](https://github.com/turbot/steampipe-plugin-hackernews/releases/latest) of the extension. I'm on an M2 MacBook so I grabbed the `steampipe_sqlite_hackernews.darwin_arm64.tar.gz ` file:

```bash
curl -OL https://github.com/turbot/steampipe-plugin-hackernews/releases/download/v0.8.1/steampipe_sqlite_hackernews.darwin_arm64.tar.gz
tar -xzvf steampipe_sqlite_hackernews.darwin_arm64.tar.gz
```
We now have a `steampipe_sqlite_hackernews.so` file.

## Loading extensions with sqlite-utils

With [sqlite-utils](https://sqlite-utils.datasette.io/) installed, try running this:

```bash
sqlite-utils memory --load-extension steampipe_sqlite_hackernews.so \
  'select id, title, time from hackernews_top limit 3'
```
On my computer this produces a warning box like this:

!["steampipe_sqlite_hackernews.- so" can't be opened because Apple cannot check it for malicious software. This software needs to be updated. Contact the developer for more information. Firefox downloaded this file today at 12:40 PM. Button: OK](https://static.simonwillison.net/static/2023/steampipe-warning.png)

This is because the binary has not been signed by the developer.

We can work around this error by opening up the system Security preferences pane and finding this option:

![Security Allow applications downloaded from App Store • App Store and identified developers "steampipe_sqlite_hackernews.so" was blocked from use because it is not from an identified developer. Button: Allow Anyway](https://static.simonwillison.net/static/2023/steampipe-allow-anyway.png)

Click "Allow Anyway" then try running the command again.

One more dialog:

![Same as the first, but now the buttons are Open, Show in Finder and Cancel.](https://static.simonwillison.net/static/2023/steampipe-last.png)

Click "Open" and the script should run correctly.

Now I can run this again:
```bash
sqlite-utils memory --load-extension steampipe_sqlite_hackernews.so \
  'select id, title, time from hackernews_top limit 3'
```
And get back:
```json
[{"id": 38706914, "title": "Gameboy Music and Sound Archive for MIDI", "time": "2023-12-20 09:45:05"},
 {"id": 38717114, "title": "Show HN: Talk to any ArXiv paper just by changing the URL", "time": "2023-12-21 04:48:20"},
 {"id": 38716075, "title": "OpenAI Begins Tackling ChatGPT Data Leak Vulnerability", "time": "2023-12-21 01:38:10"}]
```
We just queried the Hacker News API using SQL!

The [sqlite-utils-shell](https://github.com/simonw/sqlite-utils-shell) plugin provides an interactive interface for trying out more queries:
```bash
sqlite-utils install sqlite-utils-shell
sqlite-utils shell --load-extension steampipe_sqlite_hackernews.so
```
You can enter queries followed by a semicolon:
```
sqlite-utils>  select id, about from hackernews_user where id in ('simonw', 'patio11');
id       about
-------  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
patio11  Howdy. I&#x27;m Patrick. I work for the Internet, at Stripe, on helping startups. Previously: Starfighter, Appointment Reminder, Bingo Card Creator.<p>blog: https:&#x2F;&#x2F;www.kalzumeus.com<p>My best email is patrick@ the blog domain. Open invitation: if you&#x27;re reading this, I&#x27;m happy to receive email about any software&#x2F;startup&#x2F;etc topic from you at any time. I generally reply to about 60% of unsolicited email from HNers, and if I don&#x27;t reply to you, it is only because I got busy, not because of anything you said.<p>I write a lot.  Most of what I write here is unless otherwise stated in my personal capacity, and opinions expressed may not be shared by employers, clients, friends, etc.
simonw   JSK Fellow 2020. Creator of Datasette, co-creator of Django. Co-founder of Lanyrd, YC Winter 2011.<p>https:&#x2F;&#x2F;simonwillison.net&#x2F; and https:&#x2F;&#x2F;til.simonwillison.net&#x2F;
sqlite-utils> 
```
## Running extensions in Datasette

Once you've jumped through the security hooks to enable an extension it can be used directly with Datasette as well. Let's try two at once - the Hacker News one and the [crt.sh](https://hub.steampipe.io/plugins/turbot/crtsh) plugin for querying certificate transparency logs.

Download [the latest steampipe-plugin-crtsh](https://github.com/turbot/steampipe-plugin-crtsh/releases/latest) file - for macOS I used:

```bash
curl -OL https://github.com/turbot/steampipe-plugin-crtsh/releases/download/v0.4.0/steampipe_sqlite_crtsh.darwin_arm64.tar.gz
tar -xzvf steampipe_sqlite_crtsh.darwin_arm64.tar.gz
```
Now load both extensions like this:
```bash
datasette \
  --load-extension steampipe_sqlite_crtsh.so \
  --load-extension steampipe_sqlite_hackernews.so \
  --setting sql_time_limit_ms 20000
```
That `--setting sql_time_limit_ms 20000` line bumps up the default time limit on SQL queries from 1s to 20s - useful for some of these API calls since they can be a little slow.

Now we can query the certificate transparency log with SQL like this:

```sql
select
  dns_names,
  not_after
from
  crtsh_certificate
where
  query = 'datasette.io'
order by not_after desc;
```
![Screenshot of Datasette running that SQL query. The top results are lambda-demo.datasette.io 	2024-10-01 sqlite-utils.datasette.io 	2024-09-27 sqlite-utils.datasette.io 	2024-09-27 docs.datasette.io 	2024-05-13 docs.datasette.io 	2024-05-13 shot-scraper.datasette.io 	2024-04-17 shot-scraper.datasette.io 	2024-04-17](https://static.simonwillison.net/static/2023/steampipe-crt-datasette.jpg)

Here's more detailed documentation of the kind of queries you can now run:

- [Tables in crt.sh](https://hub.steampipe.io/plugins/turbot/crtsh/tables)
- [Tables in Hacker News](https://hub.steampipe.io/plugins/turbot/hackernews/tables)
