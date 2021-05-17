# KNN queries with SpatiaLite

The latest version of SpatiaLite adds KNN support, which makes it easy to efficiently answer the question "what are the X closest records to this point".

The USGS earthquakes GeoJSON is a great dataset for experimenting with these features.

Documentation for that is here: https://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php

`https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson` currently contains 10,642 features.

To turn that into a SpatiaLite database using the latest version of [geojson-to-sqlite](https://github.com/simonw/geojson-to-sqlite):
```bash
curl 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson' | \
  geojson-to-sqlite usgs.db quakes - --spatial-index
```
This will create a `usgs.db` SpatiaLite database with a spatial index.

Open it in Datasette like this:

```bash
datasette --load-extension=spatialite usgs.db
```

(Running `datasette install datasette-cluster-map` first will let you see them on a map.)

Use this SQL query to run KNN searches returning the ten closest earthquakes to a point:
```sql
SELECT
  knn.distance,
  quakes.title,
  quakes.mag,
  quakes.time,
  quakes.url,
  y(quakes.geometry) as latitude,
  x(quakes.geometry) as longitude
FROM
  knn
  join quakes on knn.fid = quakes.rowid
WHERE
  f_table_name = 'quakes'
  AND ref_geometry = MakePoint(cast(:longitude as real), cast(:latitude as real))
  AND max_items = 10
```
