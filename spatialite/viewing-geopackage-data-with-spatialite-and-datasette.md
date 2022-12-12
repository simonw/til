# Viewing GeoPackage data with SpatiaLite and Datasette

I managed to display a polygon fom a GeoPackage database file today, using SpatiaLite and Datasette.

## GeoPackage

[GeoPackage](https://www.geopackage.org/) is a standard format for distributing geospatial data as SQLite databases.

I'm still not entirely clear which binary format it uses to store geometries, but I've figured out how to view them by jumping through quite a few hoops.

I started with an example file from here: https://gisdata.mn.gov/dataset/struc-dnr-wld-mgmt-areas-pub

I could browse this in Datasette like so:

    datasette struc_dnr_wld_mgmt_areas_pub.gpkg

But this showed the `geom` columns as pure binary data.

## Using SpatiaLite with Datasette

Datasette can load the SpatiaLite extension, if it is available.

Unfortunately it's very easy to end up with a Python 3 version on OS X which entirely disables loading SQLite extensions.

The version you can install from Homebrew does not have this limitation. You can get an install of Datasette that uses that extension-enabled Python using `brew install datasette`.

I found I had to use the full path to my Homebrew installation to get that to work, like so:

```
/usr/local/Cellar/datasette/0.61.1/bin/datasette \
  struc_dnr_wld_mgmt_areas_pub.gpkg --load-extension spatialite   
```

To convert the GeoPackage column to a SpatiaLite column, you can use either of these functions:

```sql
select GeomFromGPB(geom) from dnr_wildlife_management_areas_public_facilities_lines
-- or
select CastAutomagic(geom) from dnr_wildlife_management_areas_public_facilities_lines
```
Once it's a SpatiaLite geometry you can convert to GeoJSON like this:
```sql
select AsGeoJSON(GeomFromGPB(geom)) from dnr_wildlife_management_areas_public_facilities_lines
```
This gave me back GeoJSON! But it looked like this (truncated):
```json
{
    "type": "LineString",
    "coordinates": [
        [
            363204.8576250001,
            5155661.741125
        ],
        [
            363227.3801250001,
            5155745.02675
        ],
        [
            363215.0977499997,
            5155760.594499999
        ]
    ]
}
```
Those don't look like regular latitude/longitude values. They're not - they are in a different projection.

The `gpkg_geometry_columns` table has a `srs_id` column, and it showed that for this geometry column the SRID is 26915 - https://epsg.io/26915 says that's "NAD83 / UTM zone 15N" for "North America - between 96°W and 90°W - onshore and offshore".

So we need to convert it to WGS84, also known as SRID 4326, which is preferred by the GeoJSON ecosystem.

After much digging around I figured out this SQL query:

```sql
select AsGeoJSON(ST_Transform(SetSRID(GeomFromGPB(geom), 26915), 4326))
from dnr_wildlife_management_areas_public_facilities_lines
```

The geometry object we get back from `GeomFromGPB()` doesn't have an SRID associated with it, so we need to specify that it's in 26915 using `SetSRID()`. Having done that, we can use `ST_Transform()` to transform it to WGS84.

## InitSpatialMetadata() to fix ST_Transform()

The first time I tried this I got this error:

> `ST_Transform exception - unable to find the origin SRID`

After a LOT of frustration, I figured out this was because the database (here the `struc_dnr_wld_mgmt_areas_pub.gpkg` file) was missing the `spatial_ref_sys` table it needs to look up different SRIDs.

This isn't a surprise, because it's not a SpatiaLite databsae - it's a regular SQLite database.

You can create those tables in a database by calling this SpatiaLite function:

```sql
select InitSpatialMetadata();
```

Datasette can't call this function because it writes to the database file, so I used `sqlite-utils` instead - again using a version installed by Homebrew so it could load the extension:

```
/usr/local/Cellar/sqlite-utils/3.28/bin/sqlite-utils \
  query struc_dnr_wld_mgmt_areas_pub.gpkg 'select InitSpatialMetadata()'
```
This did the job! Having run this, I could open Datasette against the database file (now upgraded to a SpatiaLite database) and view GeoJSON with:

```sql
select AsGeoJSON(ST_Transform(SetSRID(GeomFromGPB(geom), 26915), 4326))
from dnr_wildlife_management_areas_public_facilities_lines
```

## Viewing it on a map

Install the [datasette-geojson-map](https://datasette.io/plugins/datasette-geojson-map) by Chris Amico to see that data on a map.

The plugin needs you to return a `geometry` column, like this:

```sql
select ST_Transform(SetSRID(GeomFromGPB(geom), 26915), 4326) as geometry
from dnr_wildlife_management_areas_public_facilities_lines
```

<img width="1146" alt="A map showing geometries returned by Datasette" src="https://user-images.githubusercontent.com/9599/206952011-ce799edb-732e-4e87-a559-e06a7b0401e5.png">

This plugin works against SpatiaLite geometries, not GeoJSON, so I dropped the `AsGeoJSON()` call.

The binary data here is being rendered using [datasette-render-binary](https://datasette.io/plugins/datasette-render-binary).
