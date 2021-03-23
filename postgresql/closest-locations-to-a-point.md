# Closest locations to a point

Here's a PostgreSQL SQL query that returns the closest locations to a point, based on a brute-force approach where the database calculates the distance (in miles) to every single row and then sorts by that distance.

It's adapted from [this StackOverflow answer](https://gis.stackexchange.com/a/31629), which helpfully points out that if you want kilometers rather than miles you can swap the `3959` constant for `6371` instead.

There are much more efficient ways to do this if you are using PostGIS, described in this [Nearest-Neighbour Searching](https://postgis.net/workshops/postgis-intro/knn.html) tutorial - but if you're not using PostGIS this works pretty well.

I ran this against a table with over 9,000 rows and got results back in less than 20ms.

```sql
with locations_with_distance as (
  select
    *,
    (
      3959 * acos (
        cos (radians(%(latitude)s::float)) * cos(radians(latitude)) * cos(
          radians(longitude) - radians(%(longitude)s::float)
        ) + sin (radians(%(latitude)s::float)) * sin(radians(latitude))
      )
    ) as distance_miles
  from
    location
)
select
  *
from
  locations_with_distance
order by
  distance_miles
limit
  20
```
The `%(latitude)s` and `%(longitude)s` bits are named parameters when working with the Python [psycopg2](https://pypi.org/project/psycopg2/) library - they also work with [django-sql-dashboard](https://pypi.org/project/django-sql-dashboard/) which I used to prototype this query.
