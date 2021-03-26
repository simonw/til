# Figuring out if a text value in SQLite is a valid integer or float

Given a table with a `TEXT` column in SQLite I want to figure out if every value in that table is actually the text representation of an integer or floating point value, so I can decide if it's a good idea to change the type of the column (using [sqlite-utils transform](https://sqlite-utils.datasette.io/en/stable/python-api.html#transforming-a-table)).

To do this efficiently, I want a SQLite idiom that will tell me if a string value is a valid integer or floating point number.

After [much tinkering](https://github.com/simonw/sqlite-utils/issues/179) I've found two recipes for this that seem to work well.

This evaluates to true if value contains a valid integer representation:
```sql
cast(cast(value AS INTEGER) AS TEXT) = value
```
And this does the same thing for floating point numbers:
```sql
cast(cast(value AS REAL) AS TEXT) in (value, value || '.0')
```
The `|| '.0'` bit there is needed because `cast('1' as REAL)` returns `1.0`, not just `1`.

(Note that `1.200` will not pass this test and will be incorrectly considered an invalid floating point representation)

## Demos

The float version:

```sql
select
  value,
  cast(cast(value AS REAL) AS TEXT) in (value, value || '.0') as is_valid_float
from
  (
    select
      '1' as value
    union
    select
      '1.1' as value
    union
    select
      'dog' as value
    union
    select
      null as value
  )
```
[Try that here](https://latest.datasette.io/fixtures?sql=select%0D%0A++value%2C%0D%0A++cast%28cast%28value+AS+REAL%29+AS+TEXT%29+in+%28value%2C+value+%7C%7C+%27.0%27%29+as+is_valid_float%0D%0Afrom%0D%0A++%28%0D%0A++++select%0D%0A++++++%271%27+as+value%0D%0A++++union%0D%0A++++select%0D%0A++++++%271.1%27+as+value%0D%0A++++union%0D%0A++++select%0D%0A++++++%27dog%27+as+value%0D%0A++++union%0D%0A++++select%0D%0A++++++null+as+value%0D%0A++%29)

| value | is_valid_float |
| ----- | -------------- |
| null  | null           |
| 1     | 1              |
| 1.1   | 1              |
| dog   | 0              |

The integer version:
```sql
select
  value,
  cast(cast(value AS INTEGER) AS TEXT) = value as is_valid_int
from
  (
    select
      '1' as value
    union
    select
      '1.1' as value
    union
    select
      'dog' as value
    union
    select
      null as value
  )
```
[Try that here](https://latest.datasette.io/fixtures?sql=select%0D%0A++value%2C%0D%0A++cast%28cast%28value+AS+INTEGER%29+AS+TEXT%29+%3D+value+as+is_valid_int%0D%0Afrom%0D%0A++%28%0D%0A++++select%0D%0A++++++%271%27+as+value%0D%0A++++union%0D%0A++++select%0D%0A++++++%271.1%27+as+value%0D%0A++++union%0D%0A++++select%0D%0A++++++%27dog%27+as+value%0D%0A++++union%0D%0A++++select%0D%0A++++++null+as+value%0D%0A++%29)

| value | is_valid_int |
| ----- | ------------ |
| null  | null         |
| 1     | 1            |
| 1.1   | 0            |
| dog   | 0            |
