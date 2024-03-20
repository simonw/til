# Reviewing your history of public GitHub repositories using ClickHouse

There's a story going around at the moment that people have found code from their private GitHub repositories in the AI training data known as The Stack, using this search tool: https://huggingface.co/spaces/bigcode/in-the-stack

I'm very doubtful that private data has been included in that training set. I think it's far more likely that the repositories in question were public at some point in the time, and were gathered up by the https://www.softwareheritage.org/ project when they archived code from GitHub.

But how can we tell if a private repository was public at some point in the past?

GitHub have [a security audit log](https://github.com/settings/security-log) for logged in users, but sadly it appears to only cover the past six months.

For a longer history, we can look things up in the [GitHub Archive](https://www.gharchive.org/) project, which has been recording public events from the GitHub API since 2011.

The [ClickHouse](https://clickhouse.com/) team provide a public tool for querying that data using SQL as a demo of their software. We can use that to try and find out if a repository was public at some point in the past.

Access the tool here - no login required: https://play.clickhouse.com/play

Now execute the following SQL, replacing my username with yours in both places where it occurs:

```sql
with public_events as (
  select
    created_at as timestamp,
    'Private repo made public' as action,
    repo_name
  from github_events 
  where actor_login = 'simonw'
  and event_type in ('PublicEvent')
),
most_recent_public_push as (
  select
    max(created_at) as timestamp,
    'Most recent public push' as action,
    repo_name
  from github_events
  where event_type = 'PushEvent'
  and actor_login = 'simonw'
  group by repo_name
),
combined as (
  select * from public_events
  union all select * from most_recent_public_push
)
select * from combined order by timestamp
```
The result is a combined timeline showing two things:
- `PublicEvent` events - which [GitHub describes](https://docs.github.com/en/rest/using-the-rest-api/github-event-types?apiVersion=2022-11-28#publicevent) as "When a private repository is made public. Without a doubt: the best GitHub event."
- The most recent `PushEvent` for each repository. Repositories which started life public won't show up in the `PublicEvent` list, so this aims to capture them.

Here's an extract from the data I get back when I run the query for myself:

![2017-09-10: Most recent public push, simonw/github-large-file-test - 2017-09-12: Most recent public push, simonw/Houston-Shelters - 2017-09-26: Private repo made public, simonw/squirrelspotter - 2017-10-01: Private repo made public, simonw/simonwillisonblog - 2017-10-12: Most recent public push, simonw/ratelimitcache - 2017-10-15: Most recent public push, simonw/irma-scraped-data - 2017-10-15: Most recent public push, simonw/fema-history - 2017-11-06: Most recent public push, simonw/factory_worker_python - 2017-11-13: Private repo made public, simonw/datasette](https://github.com/simonw/til/assets/9599/5541e0d0-9b34-4eb6-bb43-6a2fd91ce7d1)
