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
