# The simplest recursive CTE

I found this really simple recursive CTE useful for ensuring I understood how to write recursive CTEs.
```sql
with recursive counter(x) as (
  select 0
    union
  select x + 1 from counter
)
select * from counter limit 5;
```
This query [returns five rows](https://latest.datasette.io/_memory?sql=with+recursive+counter%28x%29+as+%28%0D%0A++select+0%0D%0A++++union%0D%0A++select+x+%2B+1+from+counter%0D%0A%29%0D%0Aselect+*+from+counter+limit+10%3B) from a single column `x` - from 0 to 4.

|   x |
|-----|
|   0 |
|   1 |
|   2 |
|   3 |
|   4 |

If you write `with recursive counter as ...`, omitting the `(x)`, you get the following error:

> `no such column: x`

You can fix that by assigning `x` as the alias in the first part of that union:
```sql
with recursive counter as (
  select 0 as x
    union
  select x + 1 from counter
)
select * from counter limit 5;
```
So that `counter(x)` formulation is really just a way to define the column names up front.

This query returns two columns, `x` and `y`:

```sql
with recursive counter(x, y) as (
  select 0 as x, 1 as y
    union
  select x + 1, y + 2 from counter
)
select * from counter limit 5;
```
|   x |   y |
|-----|-----|
|   0 |   1 |
|   1 |   3 |
|   2 |   5 |
|   3 |   7 |
|   4 |   9 |
```
