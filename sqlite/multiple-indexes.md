# SQLite can use more than one index for a query

I was trying to figure out if SQLite has the ability to use more than one index as part of executing a single query, or if it only ever picks a single index that it thinks will give the best performance.

[1.5. Multiple AND-Connected WHERE-Clause Terms](https://www.sqlite.org/queryplanner.html#_multiple_and_connected_where_clause_terms) in the query planner documentation gives the impression that the single best index is selected if there are multiple options:

> So which index, Idx1 or Idx2, will SQLite choose? If the [ANALYZE](https://www.sqlite.org/lang_analyze.html) command has been run on the database, so that SQLite has had an opportunity to gather statistics about the available indices, then SQLite will know that the Idx1 index usually narrows the search down to a single item (our example of fruit='Orange' is the exception to this rule) whereas the Idx2 index will normally only narrow the search down to two rows. So, if all else is equal, SQLite will choose Idx1 with the hope of narrowing the search to as small a number of rows as possible.

I tried that on my global-power-plants table, which has an index `owner` and another on `country_long`:

```sql
explain query plan
select
  country_long,
  count(*)
from
  [global-power-plants]
where
  owner = 'Cypress Creek Renewables'
```
Sure enough, [that query](https://global-power-plants.datasettes.com/global-power-plants?sql=explain+query+plan+select+country_long%2C+count(*)+from+[global-power-plants]+where+owner+%3D+%27Cypress+Creek+Renewables%27) indicates that only one of the indexes was used:

`SEARCH TABLE global-power-plants USING INDEX "global-power-plants_owner" (owner=?)`

Interesting to note that `explain query plan select country_long, count(*) from [global-power-plants]` reports using a covering index scan:

`SCAN TABLE global-power-plants USING COVERING INDEX "global-power-plants_country_long"`

## But SQLite uses multiple indexes for UNION queries

On a hunch, I decided to try the following query:

```sql
explain query plan
select country_long, count(*) from [global-power-plants]
union all
select owner, count(*) from [global-power-plants]
```

To my surprise, [this returned results](https://global-power-plants.datasettes.com/global-power-plants?sql=explain+query+plan%0D%0Aselect+country_long%2C+count(*)+from+[global-power-plants]%0D%0Aunion+all%0D%0Aselect+owner%2C+count(*)+from+[global-power-plants]&p0=Cypress+Creek+Renewables) that indicated both indexes were used:

id | parent | notused | detail
-- | -- | -- | --
1 | 0 | 0 | COMPOUND QUERY
2 | 1 | 0 | LEFT-MOST SUBQUERY
6 | 2 | 0 | SCAN TABLE global-power-plants USING COVERING INDEX "global-power-plants_country_long"
16 | 1 | 0 | UNION ALL
20 | 16 | 0 | SCAN TABLE global-power-plants USING COVERING INDEX "global-power-plants_owner"

So there are queries for which multiple indexes can be used at the same time.
