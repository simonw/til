# Finding duplicate records by matching name and nearby distance

I wanted to find potentially duplicate records in my data, based on having the exact same name and being geographically located within 500 meters of each other.

This worked:
```sql
with potential_duplicates as (
  select
    a.id as one,
    b.id as two,
    ST_Distance(a.point, b.point) as distance_m
  from location a, location b 
    where a.name = b.name
    and a.id > b.id
    and ST_Distance(a.point, b.point) < 500
)
select * from potential_duplicates
```
I'm using a CTE here because it makes it easy to further customize the output with an additional query.

A few tricks in here:

- Alias the `location` twice as `a` and `b` in order to join against itself to find duplicates
- The `ST_Distance(a.point, b.point) < 500` clause returns locations within 500m of each other
- The `a.id > b.id` clause solves a problem I had with the first version of this query where each pairing was returned twice, with `one` and `two` swapped. By requiring `a` to have a higher `id` than `b` I avoid this problem entirely - and also prevent rows from matching themselves (where `a.id = b.id`).
