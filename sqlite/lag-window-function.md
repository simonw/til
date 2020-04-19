# Lag window function in SQLite

Here's [how to use a lag window function](https://covid-19.datasettes.com/covid?sql=with+italy+as+%28%0D%0A++select%0D%0A++++rowid%2C%0D%0A++++day%2C%0D%0A++++country_or_region%2C%0D%0A++++province_or_state%2C%0D%0A++++admin2%2C%0D%0A++++fips%2C%0D%0A++++confirmed%2C%0D%0A++++deaths%2C%0D%0A++++recovered%2C%0D%0A++++active%2C%0D%0A++++latitude%2C%0D%0A++++longitude%2C%0D%0A++++last_update%2C%0D%0A++++combined_key%0D%0A++from%0D%0A++++johns_hopkins_csse_daily_reports%0D%0A++where%0D%0A++++%22country_or_region%22+%3D+%3Ap0%0D%0A++order+by%0D%0A++++confirmed+desc%0D%0A%29%0D%0Aselect%0D%0A++day%2C%0D%0A++confirmed+-+lag%28confirmed%2C+1%29+OVER+%28%0D%0A++++ORDER+BY%0D%0A++++++day%0D%0A++%29+as+new_cases%0D%0Afrom%0D%0A++italy%0D%0Aorder+by+day+desc+limit+50&p0=Italy#g.mark=bar&g.x_column=day&g.x_type=ordinal&g.y_column=new_cases&g.y_type=quantitative) to calculate new cases per day when the table just has total cases over time on different dates.

The key clause is this:
```sql
select
  day,
  confirmed - lag(confirmed, 1) OVER (
    ORDER BY
      day
  ) as new_cases
```

So the syntax is `lag(column, 1) over (order by day)` - to get the previous value of `column` based on the `day`.

Full example query (using a CTE as well):

```sql
with italy as (
  select
    rowid,
    day,
    country_or_region,
    province_or_state,
    admin2,
    fips,
    confirmed,
    deaths,
    recovered,
    active,
    latitude,
    longitude,
    last_update,
    combined_key
  from
    johns_hopkins_csse_daily_reports
  where
    "country_or_region" = :p0
  order by
    confirmed desc
)
select
  day,
  confirmed - lag(confirmed, 1) OVER (
    ORDER BY
      day
  ) as new_cases
from
  italy
order by day desc limit 50
```

Originally tweeted here: https://twitter.com/simonw/status/1246482954630492200
