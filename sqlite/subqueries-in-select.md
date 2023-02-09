# Subqueries in select expressions in SQLite

I figured out a single SQL query for the following today. Given a table of GitHub repositories, for each repository return:

1. The repository name
2. The date of the most recent release from that repository (the `releases` table is a many-to-one against `repos`)
3. The total number of releases
4. **The three most recent releases** (as a JSON array of objects)

Then sort by the total number of releases and return the top 10.

Normally I would use a join, group by and count for the first three - but the fourth question here isn't possible to solve using a regular join.

Instead, I ended up using a pattern that involves subqueries in the `select` part of the query. Here's what that looks like:

```sql
select
  repos.full_name,
  (
    select
      max(created_at)
    from
      releases
    where
      repo = repos.id
  ) as max_created_at,
  (
    select
      count(*)
    from
      releases
    where
      repo = repos.id
  ) as releases_count,
  (
    select
      json_group_array(
        json_object(
          'id',
          id,
          'name',
          name,
          'created_at',
          created_at
        )
      )
    from
      (
        select
          *
        from
          releases
        where
          repo = repos.id
        order by
          created_at desc
        limit
          3
      )
  ) as recent_releases
from
  repos
order by
  releases_count desc
limit
  10
```
[Try that here](https://latest-with-plugins.datasette.io/github?sql=select%0D%0A++repos.full_name%2C%0D%0A++%28%0D%0A++++select%0D%0A++++++max%28created_at%29%0D%0A++++from%0D%0A++++++releases%0D%0A++++where%0D%0A++++++repo+%3D+repos.id%0D%0A++%29+as+max_created_at%2C%0D%0A++%28%0D%0A++++select%0D%0A++++++count%28*%29%0D%0A++++from%0D%0A++++++releases%0D%0A++++where%0D%0A++++++repo+%3D+repos.id%0D%0A++%29+as+releases_count%2C%0D%0A++%28%0D%0A++++select%0D%0A++++++json_group_array%28%0D%0A++++++++json_object%28%0D%0A++++++++++%27id%27%2C%0D%0A++++++++++id%2C%0D%0A++++++++++%27name%27%2C%0D%0A++++++++++name%2C%0D%0A++++++++++%27created_at%27%2C%0D%0A++++++++++created_at%0D%0A++++++++%29%0D%0A++++++%29%0D%0A++++from%0D%0A++++++%28%0D%0A++++++++select%0D%0A++++++++++*%0D%0A++++++++from%0D%0A++++++++++releases%0D%0A++++++++where%0D%0A++++++++++repo+%3D+repos.id%0D%0A++++++++order+by%0D%0A++++++++++created_at+desc%0D%0A++++++++limit%0D%0A++++++++++3%0D%0A++++++%29%0D%0A++%29+as+recent_releases%0D%0Afrom%0D%0A++repos%0D%0Aorder+by%0D%0A++releases_count+desc%0D%0Alimit%0D%0A++10).

Here are the first three rows of the output. The `recent_releases` column includes a JSON array with details of the three most recent releases for each of those repositories.

| full_name                  | max_created_at       |   releases_count | recent_releases                                                                                                                                                                                             |
|----------------------------|----------------------|------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| simonw/datasette           | 2022-12-15T02:02:42Z |              121 | [{"id":86103928,"name":"1.0a2","created_at":"2022-12-15T02:02:42Z"},{"id":84755750,"name":"1.0a1","created_at":"2022-12-01T21:30:39Z"},{"id":84496148,"name":"1.0a0","created_at":"2022-11-29T19:57:54Z"}]  |
| simonw/sqlite-utils        | 2022-10-25T22:34:30Z |              104 | [{"id":80981028,"name":"3.30","created_at":"2022-10-25T22:34:30Z"},{"id":75560168,"name":"3.29","created_at":"2022-08-28T03:48:36Z"},{"id":72130482,"name":"3.28","created_at":"2022-07-15T22:56:01Z"}]     |
| dogsheep/twitter-to-sqlite | 2021-09-21T17:39:08Z |               28 | [{"id":50003635,"name":"0.22","created_at":"2021-09-21T17:39:08Z"},{"id":48150315,"name":"0.21.4","created_at":"2021-08-20T00:14:08Z"},{"id":28876263,"name":"0.21.3","created_at":"2020-07-23T14:56:02Z"}] |

Note that this query doesn't use a regular join at all - it's `select complex-set-of-things from repos order by releases_count desc limit 10`.

The first two subqueries in the select statement are relatively simple:

```sql
  (
    select
      max(created_at)
    from
      releases
    where
      repo = repos.id
  ) as max_created_at,
  (
    select
      count(*)
    from
      releases
    where
      repo = repos.id
  ) as releases_count,
```
These could be handled by a regular join, but I'm including them here to illustrate the general concept - you can run a query inside the `select` that references the outer query (`where repo = repos.id`) and then give it an `as max_created_at` alias to provide a name for the resulting column.

The third subquery is more complex.

I want to return a single string value with JSON representing the most recent releases for the repository.

I select those three most recent releases like this:

```sql
select
  *
from
  releases
where
  repo = repos.id
order by
  created_at desc
limit
  3
```
Then I use the SQLite `json_group_array()` aggregate function to combine those three results into a JSON array string - and the `json_object()` scalar function to create JSON objects for each release.

```sql
  (
    select
      json_group_array(
        json_object(
          'id',
          id,
          'name',
          name,
          'created_at',
          created_at
        )
      )
    from
      (
        select
          *
        from
          releases
        where
          repo = repos.id
        order by
          created_at desc
        limit
          3
      )
  ) as recent_releases
```
The nested `select ... limit 3` is here purely to allow me to limit to three releases - I could write the query without it, but I'd end up with a JSON array of _every_ release for each repo - which would be a lot of data, since `simonw/datasette` has 121 releases!

This trick is really powerful. It's reminiscent of some of the things you can do with GraphQL - and in fact the [Super Graph](https://github.com/Hc747/super-graph) project uses PostgreSQL queries [that look something like this](https://twitter.com/dosco/status/1250886122974130182) compiled from GraphQL queries.

## Exploring this with explain query plan

While experimenting with this query I built a new prototype Datasette plugin called [datasette-explain](https://github.com/simonw/datasette-explain) to show the output of SQLite's `explain query plan select ...` command, re-formatted into a nested list.

The "Try that here" link above demonstrates that plugin. Here's the formatted `explain query plan` output:

```
SCAN repos
CORRELATED SCALAR SUBQUERY 2
    SEARCH releases USING COVERING INDEX idx_releases_repo (repo=?)
CORRELATED SCALAR SUBQUERY 1
    SEARCH releases USING INDEX idx_releases_repo (repo=?)
CORRELATED SCALAR SUBQUERY 4
    CO-ROUTINE (subquery-3)
        SEARCH releases USING INDEX idx_releases_repo (repo=?)
        USE TEMP B-TREE FOR ORDER BY
    SCAN (subquery-3)
USE TEMP B-TREE FOR ORDER BY
```
Some jargon definitions here to help decipher this:

- `SCAN` means "scan through every row in the entire table" - we start by scanning all of `repos`.
- `SEARCH ... USING COVERING INDEX` means a query can be answered using just data in the index itself. This is used for the `count(*)` subquery, which can be answered using only that data - because the `releases.repo` column is indexed.
- `SEARCH ... USING INDEX` answers a question using an index, but still has to look up details in the associated table rows. The `max(created_at)` subquery uses this, because `created_at` is not indexed.
- `CORRELATED SCALAR SUBQUERY`: a scalar subquery is a subquery that returns a single value - all three of our subqueries in the `select` clauses do this. `CORRELATED` means that the subquery is correlated with the outer query - it references the outer query's table (`repos` in this case).
- `CO-ROUTINE`: I don't fully understand these. Here's [the SQLite documentation explanation](https://www.sqlite.org/optoverview.html#subquery_co_routines).
- `USE TEMP B-TREE FOR ORDER BY` means that the query is using a temporary B-tree to sort the results.

## Achieving the same thing with window functions

[Anton Zhiyanov](https://twitter.com/ohmypy/status/1623586489358553088) provided this alternative SQL function which achieves the same result using window functions instead of subqueries:

```sql
with cte as (
  select
    repos.full_name,
    max(releases.created_at) over (partition by repos.id) as max_created_at,
    count(*) over (partition by repos.id) as releases_count,
    releases.id as rel_id,
    releases.name as rel_name,
    releases.created_at as rel_created_at,
    rank() over (partition by repos.id order by releases.created_at desc) as rel_rank
  from repos
    join releases on releases.repo = repos.id
)
select
  full_name,
  max_created_at,
  releases_count,
  json_group_array(
    json_object(
      'id', rel_id,
      'name', rel_name,
      'created_at', rel_created_at
    )
  ) as recent_releases
from cte
where rel_rank <= 3
group by full_name
order by releases_count desc
limit 10;
```
[Try that out here](https://latest-with-plugins.datasette.io/github?sql=with+cte+as+%28%0D%0A++select%0D%0A++++repos.full_name%2C%0D%0A++++max%28releases.created_at%29+over+%28partition+by+repos.id%29+as+max_created_at%2C%0D%0A++++count%28*%29+over+%28partition+by+repos.id%29+as+releases_count%2C%0D%0A++++releases.id+as+rel_id%2C%0D%0A++++releases.name+as+rel_name%2C%0D%0A++++releases.created_at+as+rel_created_at%2C%0D%0A++++rank%28%29+over+%28partition+by+repos.id+order+by+releases.created_at+desc%29+as+rel_rank%0D%0A++from+repos%0D%0A++++join+releases+on+releases.repo+%3D+repos.id%0D%0A%29%0D%0Aselect%0D%0A++full_name%2C%0D%0A++max_created_at%2C%0D%0A++releases_count%2C%0D%0A++json_group_array%28%0D%0A++++json_object%28%0D%0A++++++%27id%27%2C+rel_id%2C%0D%0A++++++%27name%27%2C+rel_name%2C%0D%0A++++++%27created_at%27%2C+rel_created_at%0D%0A++++%29%0D%0A++%29+as+recent_releases%0D%0Afrom+cte%0D%0Awhere+rel_rank+%3C%3D+3%0D%0Agroup+by+full_name%0D%0Aorder+by+releases_count+desc%0D%0Alimit+10%3B).

The key trick here is the `rank() over` line:

```sql
rank() over (partition by repos.id order by releases.created_at desc) as rel_rank
```
This adds an integer called `rel_rank` to each row in that CTE showing the relative ranking of each release, ordered by their created date. [This version of the query](https://latest-with-plugins.datasette.io/github?sql=with+cte+as+%28%0D%0A++select%0D%0A++++repos.full_name%2C%0D%0A++++max%28releases.created_at%29+over+%28partition+by+repos.id%29+as+max_created_at%2C%0D%0A++++count%28*%29+over+%28partition+by+repos.id%29+as+releases_count%2C%0D%0A++++releases.id+as+rel_id%2C%0D%0A++++releases.name+as+rel_name%2C%0D%0A++++releases.created_at+as+rel_created_at%2C%0D%0A++++rank%28%29+over+%28partition+by+repos.id+order+by+releases.created_at+desc%29+as+rel_rank%0D%0A++from+repos%0D%0A++++join+releases+on+releases.repo+%3D+repos.id%0D%0A%29%0D%0Aselect+*+from+cte) shows the contents of the `cte` table, which starts like this:

| full_name                      | max_created_at       |   releases_count |   rel_id | rel_name                                                       | rel_created_at       |   rel_rank |
|--------------------------------|----------------------|------------------|----------|----------------------------------------------------------------|----------------------|------------|
| simonw/datasette               | 2022-12-15T02:02:42Z |              121 | 86103928 | 1.0a2                                                          | 2022-12-15T02:02:42Z |          1 |
| simonw/datasette               | 2022-12-15T02:02:42Z |              121 | 84755750 | 1.0a1                                                          | 2022-12-01T21:30:39Z |          2 |
| simonw/datasette               | 2022-12-15T02:02:42Z |              121 | 84496148 | 1.0a0                                                          | 2022-11-29T19:57:54Z |          3 |

Then later in the query the `from cte where rel_rank <= 3` filters to just the first three releases for each repository, such that the `group by` can be used in conjunction with `json_group_array()` to generate the JSON for just those three.

The `explain query plan` for this variant looks like this:

```
CO-ROUTINE cte
    CO-ROUTINE (subquery-3)
        CO-ROUTINE (subquery-4)
            SCAN releases
            SEARCH repos USING INTEGER PRIMARY KEY (rowid=?)
            USE TEMP B-TREE FOR ORDER BY
        SCAN (subquery-4)
    SCAN (subquery-3)
SCAN cte
USE TEMP B-TREE FOR GROUP BY
USE TEMP B-TREE FOR ORDER BY
```

## Using a left join to include repos with no releases

There's a catch with this query though: since it's using a regular join between `repos` and `releases` it won't return a row at all for any repository that does not have at least one associated release.

We can fix that using a `left join`, like this:

```sql
  from repos
    left join releases on releases.repo = repos.id
```
This almost has the desired effect, but if [you run it](https://latest-with-plugins.datasette.io/github?sql=with+cte+as+(%0D%0A++select%0D%0A++++repos.full_name%2C%0D%0A++++max(releases.created_at)+over+(partition+by+repos.id)+as+max_created_at%2C%0D%0A++++count(*)+over+(partition+by+repos.id)+as+releases_count%2C%0D%0A++++releases.id+as+rel_id%2C%0D%0A++++releases.name+as+rel_name%2C%0D%0A++++releases.created_at+as+rel_created_at%2C%0D%0A++++rank()+over+(partition+by+repos.id+order+by+releases.created_at+desc)+as+rel_rank%0D%0A++from+repos%0D%0A++++left+join+releases+on+releases.repo+%3D+repos.id%0D%0A)%0D%0Aselect%0D%0A++full_name%2C%0D%0A++max_created_at%2C%0D%0A++releases_count%2C%0D%0A++json_group_array(%0D%0A++++json_object(%0D%0A++++++%27id%27%2C+rel_id%2C%0D%0A++++++%27name%27%2C+rel_name%2C%0D%0A++++++%27created_at%27%2C+rel_created_at%0D%0A++++)%0D%0A++)+as+recent_releases%0D%0Afrom+cte%0D%0Awhere+rel_rank+%3C%3D+3%0D%0Agroup+by+full_name%0D%0Aorder+by+releases_count+desc) you'll notice that it returns rows that look like this:

| full_name                                                            | max_created_at       |   releases_count | recent_releases                                                    |
|----------------------------------------------------------------------|----------------------|------------------|--------------------------------------------------------------------|
| zerok/covid19-aut-stats                                              |                      |                1 | [{"id":null,"name":null,"created_at":null}]                        |
| yml/sybarval_dataviz                                                 |                      |                1 | [{"id":null,"name":null,"created_at":null}]                        |

There are two things wrong here: `releases_count` is 1 when it should be 0, and the `recent_releases` returns an array with an object full of nulls.

We can fix the first problem by changing this line:
```sql
count(*) over (partition by repos.id) as releases_count,
```
To this:
```sql
count(releases.id) over (partition by repos.id) as releases_count,
```
This will only increment the counter for rows where that column isn't null, which fixes the problem and returns a 0 value.

For the second problem, we can add a filter to the end of the `json_group_array()` aggregation like this:

```sql
  json_group_array(
    json_object(
      'id', rel_id,
      'name', rel_name,
      'created_at', rel_created_at
    )
  ) filter (where rel_id is not null) as recent_releases
```
This excludes the left joined release data with the null values, which results in an empty `[]` for repos with no releases.

The finished query looks like this:

```sql
with cte as (
  select
    repos.full_name,
    max(releases.created_at) over (partition by repos.id) as max_created_at,
    count(releases.id) over (partition by repos.id) as releases_count,
    releases.id as rel_id,
    releases.name as rel_name,
    releases.created_at as rel_created_at,
    rank() over (partition by repos.id order by releases.created_at desc) as rel_rank
  from repos
    left join releases on releases.repo = repos.id
)
select
  full_name,
  max_created_at,
  releases_count,
  json_group_array(
    json_object(
      'id', rel_id,
      'name', rel_name,
      'created_at', rel_created_at
    )
  ) filter (where rel_id is not null) as recent_releases
from cte
where rel_rank <= 3
group by full_name
order by releases_count desc
```
