# Splitting on commas in SQLite

I had an input string in `x,y,z` format and I needed to split it into three separate values in SQLite. I managed to do it using a confusing combination of the `instr()` and `substr()` functions.

Here's what I came up with:

```sql
with comma_locations as (
  select instr(:path, ',') as first_comma,
  instr(:path, ',') + instr(substr(:path, instr(:path, ',') + 1), ',') as second_comma
), variables as (
  select
    substr(:path, 0, first_comma) as first,
    substr(:path, first_comma + 1, second_comma - first_comma - 1) as second,
    substr(:path, second_comma + 1) as third
  from comma_locations
)
select * from variables
```

Against an input of `x12,y1234,z12345` it returns this:

| first | second | third |
| --- | --- | --- |
| x12 | y1234 | z12345 |

Here's [a live demo of the query](https://latest.datasette.io/fixtures?sql=with+comma_locations+as+%28%0D%0A++select+instr%28%3Apath%2C+%27%2C%27%29+as+first_comma%2C%0D%0A++instr%28%3Apath%2C+%27%2C%27%29+%2B+instr%28substr%28%3Apath%2C+instr%28%3Apath%2C+%27%2C%27%29+%2B+1%29%2C+%27%2C%27%29+as+second_comma%0D%0A%29%2C+variables+as+%28%0D%0A++select%0D%0A++++substr%28%3Apath%2C+0%2C+first_comma%29+as+first%2C%0D%0A++++substr%28%3Apath%2C+first_comma+%2B+1%2C+second_comma+-+first_comma+-+1%29+as+second%2C%0D%0A++++substr%28%3Apath%2C+second_comma+%2B+1%29+as+third%0D%0A++from+comma_locations%0D%0A%29%0D%0Aselect+*+from+variables&path=x12%2Cy1234%2Cz12345).
