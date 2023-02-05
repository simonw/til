# The SQLite now argument is stable within the same query

I stumbled across an interesting little detail of SQLite today, running the following query:

```sql
select strftime('%s','now') || substr(strftime('%f','now'),4) as t1
union all
select strftime('%s','now') || substr(strftime('%f','now'),4)
union all
select strftime('%s','now') || substr(strftime('%f','now'),4)
union all
select strftime('%s','now') || substr(strftime('%f','now'),4)
union all
select strftime('%s','now') || substr(strftime('%f','now'),4)
union all
select strftime('%s','now') || substr(strftime('%f','now'),4)
```
That `strftime()` pattern is [described here](https://stackoverflow.com/questions/17574784/sqlite-current-timestamp-with-milliseconds/56895050#56895050) and [in this TIL](https://til.simonwillison.net/sqlite/track-timestamped-changes-to-a-table), it returns the current Unix timestamp in milliseconds.

The [result of the above query](https://latest.datasette.io/_memory?sql=select+strftime%28%27%25s%27%2C%27now%27%29+%7C%7C+substr%28strftime%28%27%25f%27%2C%27now%27%29%2C4%29+as+t1%0D%0Aunion+all%0D%0Aselect+strftime%28%27%25s%27%2C%27now%27%29+%7C%7C+substr%28strftime%28%27%25f%27%2C%27now%27%29%2C4%29%0D%0Aunion+all%0D%0Aselect+strftime%28%27%25s%27%2C%27now%27%29+%7C%7C+substr%28strftime%28%27%25f%27%2C%27now%27%29%2C4%29%0D%0Aunion+all%0D%0Aselect+strftime%28%27%25s%27%2C%27now%27%29+%7C%7C+substr%28strftime%28%27%25f%27%2C%27now%27%29%2C4%29%0D%0Aunion+all%0D%0Aselect+strftime%28%27%25s%27%2C%27now%27%29+%7C%7C+substr%28strftime%28%27%25f%27%2C%27now%27%29%2C4%29%0D%0Aunion+all%0D%0Aselect+strftime%28%27%25s%27%2C%27now%27%29+%7C%7C+substr%28strftime%28%27%25f%27%2C%27now%27%29%2C4%29) is:

| t1 |
| --- |
| 1675631847614 |
| 1675631847614 |
| 1675631847614 |
| 1675631847614 |
| 1675631847614 |
| 1675631847614 |

I was expecting each timestamp to differ by a few milliseconds, but they're all the same.

I spotted why in the [SQLite Date and Time Functions](https://www.sqlite.org/lang_datefunc.html) documentation:

> The 'now' argument to date and time functions always returns exactly the same value for multiple invocations within the same [sqlite3_step()](https://www.sqlite.org/c3ref/step.html) call.
