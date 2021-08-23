# Searching all columns of a table in Datasette

I came up with this trick today, when I wanted to run a `LIKE` search against every column in a table.

The trick is to generate a SQL query that does a `LIKE` search against every column of a table. We can generate that query using another query:

```sql
select
  'select * from "' || :table || '" where ' || group_concat(
    '"' || name || '" like ''%'' || :search || ''%''',
    ' or '
  )
from
  pragma_table_info(:table)
```
Here's what you get when you [run that query](https://fivethirtyeight.datasettes.com/fivethirtyeight?sql=select%0D%0A++%27select+*+from+%22%27+%7C%7C+%3Atable+%7C%7C+%27%22+where+%27+%7C%7C+group_concat%28%0D%0A++++%27%22%27+%7C%7C+name+%7C%7C+%27%22+like+%27%27%25%27%27+%7C%7C+%3Asearch+%7C%7C+%27%27%25%27%27%27%2C%0D%0A++++%27+or+%27%0D%0A++%29%0D%0Afrom%0D%0A++pragma_table_info%28%3Atable%29&table=avengers%2Favengers) against the [avengers example table](https://fivethirtyeight.datasettes.com/fivethirtyeight/avengers%2Favengers) from FiveThirtyEight (pretty-printed):

```sql
select
  *
from
  "avengers/avengers"
where
  "URL" like '%' || :search || '%'
  or "Name/Alias" like '%' || :search || '%'
  or "Appearances" like '%' || :search || '%'
  or "Current?" like '%' || :search || '%'
  or "Gender" like '%' || :search || '%'
  or "Probationary Introl" like '%' || :search || '%'
  or "Full/Reserve Avengers Intro" like '%' || :search || '%'
  or "Year" like '%' || :search || '%'
  or "Years since joining" like '%' || :search || '%'
  or "Honorary" like '%' || :search || '%'
  or "Death1" like '%' || :search || '%'
  or "Return1" like '%' || :search || '%'
  or "Death2" like '%' || :search || '%'
  or "Return2" like '%' || :search || '%'
  or "Death3" like '%' || :search || '%'
  or "Return3" like '%' || :search || '%'
  or "Death4" like '%' || :search || '%'
  or "Return4" like '%' || :search || '%'
  or "Death5" like '%' || :search || '%'
  or "Return5" like '%' || :search || '%'
  or "Notes" like '%' || :search || '%'
```
Here's [an example search](https://fivethirtyeight.datasettes.com/fivethirtyeight?sql=select%0D%0A++*%0D%0Afrom%0D%0A++%22avengers%2Favengers%22%0D%0Awhere%0D%0A++%22URL%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22Name%2FAlias%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22Appearances%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22Current%3F%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22Gender%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22Probationary+Introl%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22Full%2FReserve+Avengers+Intro%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22Year%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22Years+since+joining%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22Honorary%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22Death1%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22Return1%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22Death2%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22Return2%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22Death3%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22Return3%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22Death4%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22Return4%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22Death5%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22Return5%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22Notes%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27&search=Grim+Reaper) using that generated query.

## Same trick for the entire database

Here's a query that generates a query that searches every column in every table in the database!

```sql
with tables as (
  select
    name as table_name
  from
    sqlite_master
  where
    type = 'table'
),
queries as (
  select
    'select ''' || tables.table_name || ''' as _table, rowid from "' || tables.table_name || '" where ' || group_concat(
      '"' || name || '" like ''%'' || :search || ''%''',
      ' or '
    ) as query
  from
    pragma_table_info(tables.table_name),
    tables
  group by
    tables.table_name
)
select
  group_concat(query, ' union all ')
from
  queries
```
I tried this against the FiveThirtyEight database and the query it produced was way beyond the URL length limit for Cloud Run.

Here's the result if [run against latest.datasette.io/fixtures](https://latest.datasette.io/fixtures?sql=with+tables+as+%28%0D%0A++select%0D%0A++++name+as+table_name%0D%0A++from%0D%0A++++sqlite_master%0D%0A++where%0D%0A++++type+%3D+%27table%27%0D%0A%29%2C%0D%0Aqueries+as+%28%0D%0A++select%0D%0A++++%27select+%27%27%27+%7C%7C+tables.table_name+%7C%7C+%27%27%27+as+_table%2C+rowid+from+%22%27+%7C%7C+tables.table_name+%7C%7C+%27%22+where+%27+%7C%7C+group_concat%28%0D%0A++++++%27%22%27+%7C%7C+name+%7C%7C+%27%22+like+%27%27%25%27%27+%7C%7C+%3Asearch+%7C%7C+%27%27%25%27%27%27%2C%0D%0A++++++%27+or+%27%0D%0A++++%29+as+query%0D%0A++from%0D%0A++++pragma_table_info%28tables.table_name%29%2C%0D%0A++++tables%0D%0A++group+by%0D%0A++++tables.table_name%0D%0A%29%0D%0Aselect%0D%0A++group_concat%28query%2C+%27+union+all+%27%29%0D%0Afrom%0D%0A++queries):

```sql
select
  '123_starts_with_digits' as _table,
  rowid
from
  "123_starts_with_digits"
where
  "content" like '%' || :search || '%'
union all
select
  'Table With Space In Name' as _table,
  rowid
from
  "Table With Space In Name"
where
  "pk" like '%' || :search || '%'
  or "content" like '%' || :search || '%'
union all
select
  'attraction_characteristic' as _table,
  rowid
from
  "attraction_characteristic"
where
  "pk" like '%' || :search || '%'
  or "name" like '%' || :search || '%'
union all
select
  'binary_data' as _table,
  rowid
from
  "binary_data"
where
  "data" like '%' || :search || '%'
union all
select
  'complex_foreign_keys' as _table,
  rowid
from
  "complex_foreign_keys"
where
  "pk" like '%' || :search || '%'
  or "f1" like '%' || :search || '%'
  or "f2" like '%' || :search || '%'
  or "f3" like '%' || :search || '%'
union all
select
  'compound_primary_key' as _table,
  rowid
from
  "compound_primary_key"
where
  "pk1" like '%' || :search || '%'
  or "pk2" like '%' || :search || '%'
  or "content" like '%' || :search || '%'
union all
select
  'compound_three_primary_keys' as _table,
  rowid
from
  "compound_three_primary_keys"
where
  "pk1" like '%' || :search || '%'
  or "pk2" like '%' || :search || '%'
  or "pk3" like '%' || :search || '%'
  or "content" like '%' || :search || '%'
union all
select
  'custom_foreign_key_label' as _table,
  rowid
from
  "custom_foreign_key_label"
where
  "pk" like '%' || :search || '%'
  or "foreign_key_with_custom_label" like '%' || :search || '%'
union all
select
  'facet_cities' as _table,
  rowid
from
  "facet_cities"
where
  "id" like '%' || :search || '%'
  or "name" like '%' || :search || '%'
union all
select
  'facetable' as _table,
  rowid
from
  "facetable"
where
  "pk" like '%' || :search || '%'
  or "created" like '%' || :search || '%'
  or "planet_int" like '%' || :search || '%'
  or "on_earth" like '%' || :search || '%'
  or "state" like '%' || :search || '%'
  or "city_id" like '%' || :search || '%'
  or "neighborhood" like '%' || :search || '%'
  or "tags" like '%' || :search || '%'
  or "complex_array" like '%' || :search || '%'
  or "distinct_some_null" like '%' || :search || '%'
union all
select
  'foreign_key_references' as _table,
  rowid
from
  "foreign_key_references"
where
  "pk" like '%' || :search || '%'
  or "foreign_key_with_label" like '%' || :search || '%'
  or "foreign_key_with_blank_label" like '%' || :search || '%'
  or "foreign_key_with_no_label" like '%' || :search || '%'
  or "foreign_key_compound_pk1" like '%' || :search || '%'
  or "foreign_key_compound_pk2" like '%' || :search || '%'
union all
select
  'infinity' as _table,
  rowid
from
  "infinity"
where
  "value" like '%' || :search || '%'
union all
select
  'no_primary_key' as _table,
  rowid
from
  "no_primary_key"
where
  "content" like '%' || :search || '%'
  or "a" like '%' || :search || '%'
  or "b" like '%' || :search || '%'
  or "c" like '%' || :search || '%'
union all
select
  'primary_key_multiple_columns' as _table,
  rowid
from
  "primary_key_multiple_columns"
where
  "id" like '%' || :search || '%'
  or "content" like '%' || :search || '%'
  or "content2" like '%' || :search || '%'
union all
select
  'primary_key_multiple_columns_explicit_label' as _table,
  rowid
from
  "primary_key_multiple_columns_explicit_label"
where
  "id" like '%' || :search || '%'
  or "content" like '%' || :search || '%'
  or "content2" like '%' || :search || '%'
union all
select
  'roadside_attraction_characteristics' as _table,
  rowid
from
  "roadside_attraction_characteristics"
where
  "attraction_id" like '%' || :search || '%'
  or "characteristic_id" like '%' || :search || '%'
union all
select
  'roadside_attractions' as _table,
  rowid
from
  "roadside_attractions"
where
  "pk" like '%' || :search || '%'
  or "name" like '%' || :search || '%'
  or "address" like '%' || :search || '%'
  or "latitude" like '%' || :search || '%'
  or "longitude" like '%' || :search || '%'
union all
select
  'searchable' as _table,
  rowid
from
  "searchable"
where
  "pk" like '%' || :search || '%'
  or "text1" like '%' || :search || '%'
  or "text2" like '%' || :search || '%'
  or "name with . and spaces" like '%' || :search || '%'
union all
select
  'searchable_fts' as _table,
  rowid
from
  "searchable_fts"
where
  "text1" like '%' || :search || '%'
  or "text2" like '%' || :search || '%'
  or "name with . and spaces" like '%' || :search || '%'
union all
select
  'searchable_fts_docsize' as _table,
  rowid
from
  "searchable_fts_docsize"
where
  "docid" like '%' || :search || '%'
  or "size" like '%' || :search || '%'
union all
select
  'searchable_fts_segdir' as _table,
  rowid
from
  "searchable_fts_segdir"
where
  "level" like '%' || :search || '%'
  or "idx" like '%' || :search || '%'
  or "start_block" like '%' || :search || '%'
  or "leaves_end_block" like '%' || :search || '%'
  or "end_block" like '%' || :search || '%'
  or "root" like '%' || :search || '%'
union all
select
  'searchable_fts_segments' as _table,
  rowid
from
  "searchable_fts_segments"
where
  "blockid" like '%' || :search || '%'
  or "block" like '%' || :search || '%'
union all
select
  'searchable_fts_stat' as _table,
  rowid
from
  "searchable_fts_stat"
where
  "id" like '%' || :search || '%'
  or "value" like '%' || :search || '%'
union all
select
  'searchable_tags' as _table,
  rowid
from
  "searchable_tags"
where
  "searchable_id" like '%' || :search || '%'
  or "tag" like '%' || :search || '%'
union all
select
  'select' as _table,
  rowid
from
  "select"
where
  "group" like '%' || :search || '%'
  or "having" like '%' || :search || '%'
  or "and" like '%' || :search || '%'
  or "json" like '%' || :search || '%'
union all
select
  'simple_primary_key' as _table,
  rowid
from
  "simple_primary_key"
where
  "id" like '%' || :search || '%'
  or "content" like '%' || :search || '%'
union all
select
  'sortable' as _table,
  rowid
from
  "sortable"
where
  "pk1" like '%' || :search || '%'
  or "pk2" like '%' || :search || '%'
  or "content" like '%' || :search || '%'
  or "sortable" like '%' || :search || '%'
  or "sortable_with_nulls" like '%' || :search || '%'
  or "sortable_with_nulls_2" like '%' || :search || '%'
  or "text" like '%' || :search || '%'
union all
select
  'table/with/slashes.csv' as _table,
  rowid
from
  "table/with/slashes.csv"
where
  "pk" like '%' || :search || '%'
  or "content" like '%' || :search || '%'
union all
select
  'tags' as _table,
  rowid
from
  "tags"
where
  "tag" like '%' || :search || '%'
union all
select
  'units' as _table,
  rowid
from
  "units"
where
  "pk" like '%' || :search || '%'
  or "distance" like '%' || :search || '%'
  or "frequency" like '%' || :search || '%'
```
[It works!](https://latest.datasette.io/fixtures?sql=select%0D%0A++%27123_starts_with_digits%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22123_starts_with_digits%22%0D%0Awhere%0D%0A++%22content%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27Table+With+Space+In+Name%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22Table+With+Space+In+Name%22%0D%0Awhere%0D%0A++%22pk%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22content%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27attraction_characteristic%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22attraction_characteristic%22%0D%0Awhere%0D%0A++%22pk%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22name%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27binary_data%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22binary_data%22%0D%0Awhere%0D%0A++%22data%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27complex_foreign_keys%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22complex_foreign_keys%22%0D%0Awhere%0D%0A++%22pk%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22f1%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22f2%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22f3%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27compound_primary_key%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22compound_primary_key%22%0D%0Awhere%0D%0A++%22pk1%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22pk2%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22content%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27compound_three_primary_keys%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22compound_three_primary_keys%22%0D%0Awhere%0D%0A++%22pk1%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22pk2%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22pk3%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22content%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27custom_foreign_key_label%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22custom_foreign_key_label%22%0D%0Awhere%0D%0A++%22pk%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22foreign_key_with_custom_label%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27facet_cities%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22facet_cities%22%0D%0Awhere%0D%0A++%22id%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22name%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27facetable%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22facetable%22%0D%0Awhere%0D%0A++%22pk%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22created%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22planet_int%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22on_earth%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22state%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22city_id%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22neighborhood%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22tags%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22complex_array%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22distinct_some_null%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27foreign_key_references%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22foreign_key_references%22%0D%0Awhere%0D%0A++%22pk%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22foreign_key_with_label%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22foreign_key_with_blank_label%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22foreign_key_with_no_label%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22foreign_key_compound_pk1%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22foreign_key_compound_pk2%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27infinity%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22infinity%22%0D%0Awhere%0D%0A++%22value%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27no_primary_key%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22no_primary_key%22%0D%0Awhere%0D%0A++%22content%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22a%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22b%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22c%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27primary_key_multiple_columns%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22primary_key_multiple_columns%22%0D%0Awhere%0D%0A++%22id%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22content%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22content2%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27primary_key_multiple_columns_explicit_label%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22primary_key_multiple_columns_explicit_label%22%0D%0Awhere%0D%0A++%22id%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22content%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22content2%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27roadside_attraction_characteristics%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22roadside_attraction_characteristics%22%0D%0Awhere%0D%0A++%22attraction_id%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22characteristic_id%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27roadside_attractions%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22roadside_attractions%22%0D%0Awhere%0D%0A++%22pk%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22name%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22address%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22latitude%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22longitude%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27searchable%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22searchable%22%0D%0Awhere%0D%0A++%22pk%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22text1%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22text2%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22name+with+.+and+spaces%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27searchable_fts%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22searchable_fts%22%0D%0Awhere%0D%0A++%22text1%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22text2%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22name+with+.+and+spaces%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27searchable_fts_docsize%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22searchable_fts_docsize%22%0D%0Awhere%0D%0A++%22docid%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22size%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27searchable_fts_segdir%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22searchable_fts_segdir%22%0D%0Awhere%0D%0A++%22level%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22idx%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22start_block%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22leaves_end_block%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22end_block%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22root%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27searchable_fts_segments%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22searchable_fts_segments%22%0D%0Awhere%0D%0A++%22blockid%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22block%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27searchable_fts_stat%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22searchable_fts_stat%22%0D%0Awhere%0D%0A++%22id%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22value%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27searchable_tags%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22searchable_tags%22%0D%0Awhere%0D%0A++%22searchable_id%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22tag%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27select%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22select%22%0D%0Awhere%0D%0A++%22group%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22having%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22and%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22json%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27simple_primary_key%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22simple_primary_key%22%0D%0Awhere%0D%0A++%22id%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22content%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27sortable%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22sortable%22%0D%0Awhere%0D%0A++%22pk1%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22pk2%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22content%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22sortable%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22sortable_with_nulls%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22sortable_with_nulls_2%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22text%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27table%2Fwith%2Fslashes.csv%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22table%2Fwith%2Fslashes.csv%22%0D%0Awhere%0D%0A++%22pk%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22content%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27tags%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22tags%22%0D%0Awhere%0D%0A++%22tag%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0Aunion+all%0D%0Aselect%0D%0A++%27units%27+as+_table%2C%0D%0A++rowid%0D%0Afrom%0D%0A++%22units%22%0D%0Awhere%0D%0A++%22pk%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22distance%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27%0D%0A++or+%22frequency%22+like+%27%25%27+%7C%7C+%3Asearch+%7C%7C+%27%25%27&search=museum&_hide_sql=1)
