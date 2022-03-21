# Identifying column combination patterns in a SQLite table

Given a large, heterogeneous table I wanted to identify patterns in the rows in terms of which columns were not null.

Imagine a table like this for example:

    id  field1  field2  field3  field4

I want to know how many records have values for (id, field1, field2) compared to the number of rows with values for (id, field3, field4).

I worked out the following query pattern for answering this question:

```sql
select
    case when [pk] is not null then 'pk, ' else '' end ||
    case when [created] is not null then 'created, ' else '' end ||
    case when [planet_int] is not null then 'planet_int, ' else '' end ||
    case when [on_earth] is not null then 'on_earth, ' else '' end ||
    case when [state] is not null then 'state, ' else '' end ||
    case when [_city_id] is not null then '_city_id, ' else '' end ||
    case when [_neighborhood] is not null then '_neighborhood, ' else '' end ||
    case when [tags] is not null then 'tags, ' else '' end ||
    case when [complex_array] is not null then 'complex_array, ' else '' end ||
    case when [distinct_some_null] is not null then 'distinct_some_null, ' else '' end
  as columns,
  count(*) as num_rows
from
  [facetable]
group by
  columns
order by
  num_rows desc
```
[Try that here](https://latest.datasette.io/fixtures?sql=select%0D%0A++++case+when+%5Bpk%5D+is+not+null+then+%27pk%2C+%27+else+%27%27+end+%7C%7C%0D%0A++++case+when+%5Bcreated%5D+is+not+null+then+%27created%2C+%27+else+%27%27+end+%7C%7C%0D%0A++++case+when+%5Bplanet_int%5D+is+not+null+then+%27planet_int%2C+%27+else+%27%27+end+%7C%7C%0D%0A++++case+when+%5Bon_earth%5D+is+not+null+then+%27on_earth%2C+%27+else+%27%27+end+%7C%7C%0D%0A++++case+when+%5Bstate%5D+is+not+null+then+%27state%2C+%27+else+%27%27+end+%7C%7C%0D%0A++++case+when+%5B_city_id%5D+is+not+null+then+%27_city_id%2C+%27+else+%27%27+end+%7C%7C%0D%0A++++case+when+%5B_neighborhood%5D+is+not+null+then+%27_neighborhood%2C+%27+else+%27%27+end+%7C%7C%0D%0A++++case+when+%5Btags%5D+is+not+null+then+%27tags%2C+%27+else+%27%27+end+%7C%7C%0D%0A++++case+when+%5Bcomplex_array%5D+is+not+null+then+%27complex_array%2C+%27+else+%27%27+end+%7C%7C%0D%0A++++case+when+%5Bdistinct_some_null%5D+is+not+null+then+%27distinct_some_null%2C+%27+else+%27%27+end%0D%0A++as+columns%2C%0D%0A++count%28*%29+as+num_rows%0D%0Afrom%0D%0A++%5Bfacetable%5D%0D%0Agroup+by%0D%0A++columns%0D%0Aorder+by%0D%0A++num_rows+desc).

This has the desired effect: it gives me back all of the combinations of not-null columns in the table, with a count for each one.

(Running this on a table with 1,000,000+ rows took about 40 seconds, so I had to use `datasette data.db --setting sql_time_limit_ms 100000` to bump up the default time limit in Datasette.)

One remaining problem: how to generate the above query for an arbitrary table. I came up with the following SQL query for generating a SQL query like the above:

```sql
select 'select
' || group_concat('    case when [' || name || '] is not null then ' || quote(name || ', ') || ' else '''' end', ' ||
') || '
  as columns,
  count(*) as num_rows
from
  [' || :table || ']
group by
  columns
order by
  num_rows desc' as query from pragma_table_info(:table)
```
[Try that out](https://latest-with-plugins.datasette.io/fixtures?sql=select+%27select%0D%0A%27+%7C%7C+group_concat%28%27++++case+when+%5B%27+%7C%7C+name+%7C%7C+%27%5D+is+not+null+then+%27+%7C%7C+quote%28name+%7C%7C+%27%2C+%27%29+%7C%7C+%27+else+%27%27%27%27+end%27%2C+%27+%7C%7C%0D%0A%27%29+%7C%7C+%27%0D%0A++as+columns%2C%0D%0A++count%28*%29+as+num_rows%0D%0Afrom%0D%0A++%5B%27+%7C%7C+%3Atable+%7C%7C+%27%5D%0D%0Agroup+by%0D%0A++columns%0D%0Aorder+by%0D%0A++num_rows+desc%27+as+query+from+pragma_table_info%28%3Atable%29&table=facetable) in a demo that includes the [datasette-query-links](https://datasette.io/plugins/datasette-query-links) plugin.
This takes `:table` as an input and generates SQL which can be used to generate column-combination counts.
