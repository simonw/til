# Cumulative total over time in SQL

This is a quick trick for creating a cumulative chart of the total number of items created over time based just on their creation date.

[Try it here](https://github-to-sqlite.dogsheep.net/github?sql=select%0D%0A++created_at%2C%0D%0A++%28%0D%0A++++select%0D%0A++++++count%28*%29%0D%0A++++from%0D%0A++++++repos+repos2%0D%0A++++where%0D%0A++++++repos2.owner+%3D+%3Ap0%0D%0A++++++and+repos2.created_at+%3C%3D+repos.created_at%0D%0A++%29+as+cumulative%0D%0Afrom%0D%0A++repos%0D%0Awhere%0D%0A++%22owner%22+%3D+%3Ap0%0D%0Aorder+by%0D%0A++created_at+desc&p0=9599#g.mark=line&g.x_column=created_at&g.x_type=temporal&g.y_column=cumulative&g.y_type=quantitative)

```sql
select
  created_at,
  (
    select
      count(*)
    from
      repos repos2
    where
      repos2.owner = 9599
      and repos2.created_at <= repos.created_at
  ) as cumulative
from
  repos
where
  "owner" = 9599
order by
  created_at desc
```
I imagine there's a more elegant way to do this using a window function but this works fine.
