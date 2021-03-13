# Querying for items stored in UTC that were created on a Thursday in PST

This came up as [a question](https://news.ycombinator.com/item?id=26443148) on Hacker News. How can you query a SQLite database for items that were created on a Thursday in PST, when the data is stored in UTC?

I have datetimes stored in UTC, so I first needed to convert them to PST by applying the 8 hour time difference, using `datetime(author_date, '-8 hours') as author_date_pst`.

Then I used `strftime('%w')` to get the day of week (as a number contained in a string).

Then I can filter for that equalling '4' for Thursday.

```sql
select
  author_date,
  datetime(author_date, '-8 hours') as author_date_pst,
  strftime('%w', datetime(author_date, '-8 hours')) as dayofweek_pst,
  *
from
  commits
where
  dayofweek_pst = '4' -- Thursday
```
[Try this query](https://github-to-sqlite.dogsheep.net/github?sql=select+author_date%2C%0D%0Adatetime%28author_date%2C+%27-8+hours%27%29+as+author_date_pst%2C+%0D%0Astrftime%28%27%25w%27%2C+datetime%28author_date%2C+%27-8+hours%27%29%29+as+dayofweek_pst%2C%0D%0A*+from+commits%0D%0Awhere+dayofweek_pst+%3D+%274%27+--+Thursday+).

SQLite documentation for date time functions is at https://sqlite.org/lang_datefunc.html
