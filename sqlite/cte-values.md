# Combining CTEs and VALUES in SQLite

Here's how to use SQLite's `VALUES` syntax with a CTE to create a temporary table that you can then perform joins against in a query:

```sql
with x(c1, c2, c3) as (
  values
    ('a', 'b', 3),
    ('b', 'c', 4)
)
select * from x
```
[Try that here](https://latest.datasette.io/fixtures?sql=with+x%28c1%2C+c2%2C+c3%29+as+%28%0D%0A++values%0D%0A++++%28%27a%27%2C+%27b%27%2C+3%29%2C%0D%0A++++%28%27b%27%2C+%27c%27%2C+4%29%0D%0A%29%0D%0Aselect+*+from+x).

The output of this query is:

| c1 | c2 | c3 |
| --- | --- | --- |
| a | b | 3 |
| b | c | 4 |

The `with x(c1, c2, c3)` bit defines a temporary table for the duration of the query called `x` with columns called `c1`, `c2` and `c3`.

Then the `values (...), (...)` bit defines two rows within that table - and can define many more.

This is useful for injecting data that you can then join againts other tables - or for providing queries that include their own example data to illustrate different SQL concepts.
