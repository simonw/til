# GUnion to combine geometries in SpatiaLite

I was playing around with [datanews/amtrak-geojson](https://github.com/datanews/amtrak-geojson), which provides GeoJSON for Amtrak stations and track segments.

I loaded it into SQLite using [geojson-to-sqlite](https://datasette.io/tools/geojson-to-sqlite) like this:

    curl "https://raw.githubusercontent.com/datanews/amtrak-geojson/master/amtrak-stations.geojson" | \
      geojson-to-sqlite /tmp/amtrak.db stations - --spatialite
    curl "https://raw.githubusercontent.com/datanews/amtrak-geojson/master/amtrak-track.geojson" | \
      geojson-to-sqlite /tmp/amtrak.db track - --spatialite

Then I installed [datasette-geojson-map](https://datasette.io/plugins/datasette-geojson-map) in order to visualize it, and opened it in Datasette:

    datasette install datasette-geojson-map
    datasette /tmp/amtrak.db --load-extension spatialite

The stations table rendered a map just fine. I added `?_size=1000` to the URL to see all of the stations rather than just the first 100:

    http://127.0.0.1:8001/amtrak/stations?_size=1000

<img width="1200" alt="The table view includes a map of the USA showing all 500 stations as markers" src="https://user-images.githubusercontent.com/9599/163033038-e02fe482-21df-445e-874f-94236072883b.png">

But the track page was less useful, even with the `?_size=1000` parameter:

    http://127.0.0.1:8001/amtrak/track?_size=1000

![The track page shows the USA map but with only a small number of little black squiggles, not a full track map for the country](https://user-images.githubusercontent.com/9599/163033296-bfa915f6-d0de-4219-b89c-b6384c826f59.png)

This is because there are 10,768 segments of track in the database, so even showing 1,000 at a time results in a very spotty map.

## Using GUnion

The solution was to combine the track segments together using the [SpatiaLite GUnion function](http://www.gaia-gis.it/gaia-sins/spatialite-sql-4.2.0.html#p14). I used the following custom SQL query:
```sql
select GUnion(geometry) as geometry from track
```
The `as geometry` is required because the mapping plugin looks for a column of that name.

Here's the result:

<img width="1202" alt="This time there is a map showing Amtrak track across the whole of the USA" src="https://user-images.githubusercontent.com/9599/163033681-527a0158-cded-40c5-9efa-9d912eeaa04a.png">

This also works for queries that pull out a subset of the data. Here's the combination of every track in FRAREGIONS 7:

<img width="1198" alt="A map just of California showing Amtrak railways there" src="https://user-images.githubusercontent.com/9599/163033991-c82dafbf-8348-496f-8300-2ae8d35eacd5.png">

Using this query:

```sql
select GUnion(geometry) as geometry from track where "FRAREGIONS" = :p0
```

## Different colours for different sections

Thanks to faceting I noticed there are 8 different FRAREGIONS. `datasette-geojson-map` supports [styled map features](https://datasette.io/plugins/datasette-geojson-map#user-content-styling-map-features), so I decided to try and show the different regions in different colours.

This query did th trick:

```sql
select
  'FRA Region ' || FRAREGIONS as title,
  case
    FRAREGIONS
    when 1 then "#dfff00"
    when 2 then "#ffbf00"
    when 3 then "#ff7f50"
    when 4 then "#de3163"
    when 5 then "#9fe2bf"
    when 6 then "#40e0d0"
    when 7 then "#6495ed"
    when 8 then "#ccccff"
    else "#000000"
  end as stroke,
  GUnion(geometry) as geometry
from
  track
group by
  FRAREGIONS
```

<img width="1197" alt="Each region now shows as a different coloured line" src="https://user-images.githubusercontent.com/9599/163035751-f0d465df-bc44-4822-82c6-24715680663f.png">
