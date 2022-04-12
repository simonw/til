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

<img width="1200" alt="image" src="https://user-images.githubusercontent.com/9599/163033038-e02fe482-21df-445e-874f-94236072883b.png">

But the track page was less useful, even with the `?_size=1000` parameter:

    http://127.0.0.1:8001/amtrak/track?_size=1000

![CleanShot 2022-04-12 at 11 53 27@2x](https://user-images.githubusercontent.com/9599/163033296-bfa915f6-d0de-4219-b89c-b6384c826f59.png)

This is because there are 10,768 segments of track in the database, so even showing 1,000 at a time results in a very spotty map.

## Using GUnion

The solution was to combine the track segments together using the [SpatiaLite GUnion function](http://www.gaia-gis.it/gaia-sins/spatialite-sql-4.2.0.html#p14). I used the following custom SQL query:
```sql
select GUnion(geometry) as geometry from track
```
The `as geometry` is required because the mapping plugin looks for a column of that name.

Here's the result:

<img width="1202" alt="image" src="https://user-images.githubusercontent.com/9599/163033681-527a0158-cded-40c5-9efa-9d912eeaa04a.png">

This also works for queries that pull out a subset of the data. Here's the combination of every track in FRAREGIONS 7:

<img width="1198" alt="image" src="https://user-images.githubusercontent.com/9599/163033991-c82dafbf-8348-496f-8300-2ae8d35eacd5.png">

Using this query:

```sql
select GUnion(geometry) as geometry from track where "FRAREGIONS" = :p0
```
