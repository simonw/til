# Consecutive groups in SQL using window functions

I have a database table with all of my Swarm checkins since 2011, created using my [swarm-to-sqlite](https://datasette.io/tools/swarm-to-sqlite) tool.

I wanted to run a query to show the date ranges I had spent in different countries, based on the country of the venue of each of those checkins.

I ended up learning how to perform operations against groups of rows identified by a consecutive sequence of values in a column, using window functions.

Here's a simplified version of the query I ended up with (the final query with joins [is here](https://gist.github.com/simonw/ac5362c1fed588bf2b87e058692c12f1)):

```sql
with ordered as (
  select 
    created,
    country,
    lag(country) over (order by created desc)
      as previous_country
  from 
    raw
),
grouped as (
  select 
    country, 
    created, 
    count(*) filter (
      where previous_country is null
      or previous_country != country
    ) over (
      order by created desc
      rows between unbounded preceding
      and current row
    ) as grp
  from 
    ordered
)
select
  country,
  date(min(created)) as start,
  date(max(created)) as end,
  cast(
    julianday(date(max(created))) -
    julianday(date(min(created))) as integer
  ) as days
from 
  grouped
group by
  country, grp
order by
  start desc;
```

Here's [the raw data](https://lite.datasette.io/?install=datasette-copyable&csv=https://gist.github.com/simonw/a2e67fd50cd025984dd1e97d88e7656d#/data/raw) I ran that against:

| created             | city             | country        |
|---------------------|------------------|----------------|
| 2023-06-08T08:16:36 | London           | United Kingdom |
| 2023-05-11T21:05:35 | San Francisco    | United States  |
| 2023-05-08T01:56:49 | Half Moon Bay    | United States  |
| 2023-05-04T22:35:05 | San Francisco    | United States  |
| 2023-05-02T20:10:39 | Stanford         | United States  |
| 2023-04-24T20:47:46 | San Francisco    | United States  |
| 2023-04-20T20:13:53 | Salt Lake City   | United States  |
| 2023-04-19T00:43:10 | San Francisco    | United States  |
| 2023-03-02T19:43:55 | Nashville        | United States  |
| 2019-09-20T18:25:45 | Palo Alto        | United States  |
| 2019-09-20T14:52:47 | San Francisco    | United States  |
| 2019-09-02T18:08:32 | San Francisco    | United States  |
| 2019-08-31T10:16:03 | Laval            | France         |
| 2019-08-26T13:01:12 |                  | France         |
| 2019-08-26T12:55:03 | Chartres         | France         |
| 2019-08-25T12:51:16 | Paris            | France         |
| 2019-08-07T08:16:37 |                  | Madagascar     |
| 2019-08-07T06:44:50 |                  | Madagascar     |
| 2019-08-03T15:08:30 |                  | Madagascar     |
| 2019-08-02T17:13:51 |                  | Madagascar     |
| 2019-07-31T15:03:17 |                  | Madagascar     |
| 2019-07-25T06:29:22 | Le Mesnil-Amelot | France         |
| 2019-06-30T21:57:26 | San Francisco    | United States  |
| 2019-06-30T18:27:28 | San Francisco    | United States  |
| 2019-06-02T02:34:59 | Sacramento       | United States  |
| 2019-05-29T15:54:49 | San Francisco    | United States  |
| 2019-05-04T23:04:18 | Cleveland        | United States  |
| 2018-09-10T09:47:22 | Ilfracombe       | United Kingdom |
| 2018-09-09T15:30:32 | Bideford         | United Kingdom |
| 2018-08-30T22:27:08 | London           | United Kingdom |
| 2018-08-29T19:45:13 | London           | United Kingdom |
| 2018-08-10T01:44:17 | San Francisco    | United States  |
| 2018-08-09T00:38:03 | San Francisco    | United States  |
| 2018-08-05T20:53:56 | San Francisco    | United States  |

And [the output of the query](https://lite.datasette.io/?install=datasette-copyable&csv=https://gist.github.com/simonw/a2e67fd50cd025984dd1e97d88e7656d#/data?sql=with+ordered+as+%28%0A++select+%0A++++created%2C%0A++++country%2C%0A++++lag%28country%29+over+%28order+by+created+desc%29%0A++++++as+previous_country%0A++from+%0A++++raw%0A%29%2C%0Agrouped+as+%28%0A++select+%0A++++country%2C+%0A++++created%2C+%0A++++count%28*%29+filter+%28%0A++++++where+previous_country+is+null%0A++++++or+previous_country+%21%3D+country%0A++++%29+over+%28%0A++++++order+by+created+desc%0A++++++rows+between+unbounded+preceding%0A++++++and+current+row%0A++++%29+as+grp%0A++from+%0A++++ordered%0A%29%0Aselect%0A++country%2C%0A++date%28min%28created%29%29+as+start%2C%0A++date%28max%28created%29%29+as+end%2C%0A++cast%28%0A++++julianday%28date%28max%28created%29%29%29+-%0A++++julianday%28date%28min%28created%29%29%29+as+integer%0A++%29+as+days%0Afrom+%0A++grouped%0Agroup+by%0A++country%2C+grp%0Aorder+by%0A++start+desc%3B):

| country        | start      | end        |   days |
|----------------|------------|------------|--------|
| United Kingdom | 2023-06-08 | 2023-06-08 |      0 |
| United States  | 2019-09-02 | 2023-05-11 |   1347 |
| France         | 2019-08-25 | 2019-08-31 |      6 |
| Madagascar     | 2019-07-31 | 2019-08-07 |      7 |
| France         | 2019-07-25 | 2019-07-25 |      0 |
| United States  | 2019-05-04 | 2019-06-30 |     57 |
| United Kingdom | 2018-08-29 | 2018-09-10 |     12 |
| United States  | 2018-08-05 | 2018-08-10 |      5 |

## How that query works

There are three steps to the query.

1. Extend the raw data with an extra `previous_country` column which shows the country for the previous row, using the `lag()` window function.
2. Group the data by country, using another window function to assign a group number to each row. That group number increments whenever the country changes.
3. Group the data by country and group number, and use `min()` and `max()` to find the start and end dates for each group and to calculate the number of days in each group.

The first two steps are implemented using CTEs. Let's break those down:

```sql
with ordered as (
  select 
    created,
    country,
    lag(country) over (order by created desc)
      as previous_country
  from 
    raw
)
select * from ordered
```
[Truncated output](https://lite.datasette.io/?install=datasette-copyable&csv=https://gist.github.com/simonw/a2e67fd50cd025984dd1e97d88e7656d#/data?sql=with+ordered+as+%28%0A++select+%0A++++created%2C%0A++++country%2C%0A++++lag%28country%29+over+%28order+by+created+desc%29%0A++++++as+previous_country%0A++from+%0A++++raw%0A%29%0Aselect+*+from+ordered):

| created             | country        | previous_country   |
|---------------------|----------------|--------------------|
| 2023-06-08T08:16:36 | United Kingdom |                    |
| 2023-05-11T21:05:35 | United States  | United Kingdom     |
| 2023-05-08T01:56:49 | United States  | United States      |
| 2023-05-04T22:35:05 | United States  | United States      |
| 2019-08-31T10:16:03 | France         | United States      |
| 2019-08-26T13:01:12 | France         | France             |
| 2019-08-25T12:51:16 | France         | France             |
| 2019-08-07T08:16:37 | Madagascar     | France             |
| 2019-08-07T06:44:50 | Madagascar     | Madagascar         |
| 2019-07-31T15:03:17 | Madagascar     | Madagascar         |
| 2019-07-25T06:29:22 | France         | Madagascar         |

The magic here is this window function:

```sql
lag(country) over (order by created desc) as previous_country
```
That `over (order by created desc)` part means "consider all rows in this table, ordered by the `created` column in descending order". `lag(country)` means "take the value of the `country` column from the previous row within that window".

The next CTE adds a `grp` column which increments whenever the country changes:

```sql
with ordered as (
  select 
    created,
    country,
    lag(country) over (order by created desc)
      as previous_country
  from 
    raw
),
grouped as (
  select 
    country, 
    created, 
    count(*) filter (
      where previous_country is null
      or previous_country != country
    ) over (
      order by created desc
      rows between unbounded preceding
      and current row
    ) as grp
  from 
    ordered
)
select * from grouped
```
[Truncated output](https://lite.datasette.io/?install=datasette-copyable&csv=https://gist.github.com/simonw/a2e67fd50cd025984dd1e97d88e7656d#/data?sql=with+ordered+as+%28%0A++select+%0A++++created%2C%0A++++country%2C%0A++++lag%28country%29+over+%28order+by+created+desc%29%0A++++++as+previous_country%0A++from+%0A++++raw%0A%29%2C%0Agrouped+as+%28%0A++select+%0A++++country%2C+%0A++++created%2C+%0A++++count%28*%29+filter+%28%0A++++++where+previous_country+is+null%0A++++++or+previous_country+%21%3D+country%0A++++%29+over+%28%0A++++++order+by+created+desc%0A++++++rows+between+unbounded+preceding%0A++++++and+current+row%0A++++%29+as+grp%0A++from+%0A++++ordered%0A%29%0Aselect+*+from+grouped):

| country        | created             |   grp |
|----------------|---------------------|-------|
| United Kingdom | 2023-06-08T08:16:36 |     1 |
| United States  | 2023-05-11T21:05:35 |     2 |
| United States  | 2023-05-08T01:56:49 |     2 |
| United States  | 2023-05-04T22:35:05 |     2 |
| France         | 2019-08-31T10:16:03 |     3 |
| France         | 2019-08-26T13:01:12 |     3 |
| France         | 2019-08-26T12:55:03 |     3 |
| Madagascar     | 2019-08-07T08:16:37 |     4 |
| Madagascar     | 2019-08-07T06:44:50 |     4 |
| France         | 2019-07-25T06:29:22 |     5 |
| United States  | 2019-06-30T21:57:26 |     6 |

This window function is more complicated:

```sql
count(*) filter (
  where previous_country is null
  or previous_country != country
) over (
  order by created desc
  rows between unbounded preceding
  and current row
) as grp
```
The `over` clause here defines a window that includes all of the rows up to and including the current one, ordered by `created` in descending order.

The `count(*) filter (...)` part counts the number of rows in that window where either `previous_country` is null or `previous_country != country`.

The final step is to group by country and group number, and to use `min()` and `max()` to find the start and end dates for each group and to calculate the number of days in each group:

```sql
...
select
  country,
  date(min(created)) as start,
  date(max(created)) as end,
  cast(
    julianday(date(max(created))) -
    julianday(date(min(created))) as integer
  ) as days
from 
  grouped
group by
  country, grp
order by
  start desc;
```
Grouping by `country, grp` returns a single row per group. The `min(created)` and `max(created)` functions can then find  the earliest and latest dates in each group.

I'm using `date()` to turn those `created` timestamps into `YYYY-MM-DD` dates.

Finally, I use `julianday()` to convert those dates into Julian day numbers, and then subtract the two numbers to get the number of days between them. The result is a floating point number, so I use `cast(... as integer)` to convert it to an integer.
