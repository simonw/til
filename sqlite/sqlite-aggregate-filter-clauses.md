# SQLite aggregate filter clauses

SQLite supports aggregate filter clauses, as described in this [SQL Pivot in all databases](https://modern-sql.com/use-case/pivot) tutorial.

An example query:
```sql
select
  year,
  sum(revenue) filter (where month = 1) as jan_revenue,
  sum(revenue) filter (where month = 2) as feb_revenue
from invoices
group by year
```
Here's an example using `sqlite-utils` to initially populate a database table:
```
/tmp % echo 'year,month,revenue
2019,1,110
2019,1,30
2019,2,34
2019,2,112
2020,1,40
2020,1,50
2020,2,110' | sqlite-utils insert data.db invoices - --csv
/tmp % sqlite-utils rows data.db invoices
[{"year": "2019", "month": "1", "revenue": "110"},
 {"year": "2019", "month": "1", "revenue": "30"},
 {"year": "2019", "month": "2", "revenue": "34"},
 {"year": "2019", "month": "2", "revenue": "112"},
 {"year": "2020", "month": "1", "revenue": "40"},
 {"year": "2020", "month": "1", "revenue": "50"},
 {"year": "2020", "month": "2", "revenue": "110"}]
```
And the results of that query:
```
/tmp % sqlite-utils data.db 'select
  year,
  sum(revenue) filter (where month = 1) as jan_revenue,
  sum(revenue) filter (where month = 2) as feb_revenue
from invoices
group by year' -t
  year    jan_revenue    feb_revenue
------  -------------  -------------
  2019            140            146
  2020             90            110
```
