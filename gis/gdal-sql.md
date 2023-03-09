# Using SQL with GDAL

Inspired [by Brad Neuberg](https://twitter.com/bradneuberg/status/1633875601789681666) I decided to take a look at the SQL features in the GDAL family of tools.

GDAL is a complex beast. I finally understand the difference between GDAL and GEOS:

- **[GEOS](https://libgeos.org/)** is an open source C/C++ library providing polygon and topology operations ("computational geometry") - it's used by tools like the Python [Shapely](https://shapely.readthedocs.io/) library, and is baked into all sorts of other GIS software such as PostGIS and QGIS. It handles things like points, polygons, multipolygons and linestrings and implements operations such as intersections, union, distance, area and length. It also provides algorithms for spatial indexing.
- **[GDAL](https://gdal.org/)** is "a translator library for raster and vector geospatial data formats" - it's built on top of GEOS and a whole host of other libraries and provides a wide range of tools (and library functions) for manipulating dozens of raster and vector formats - Shapefiles, GeoJSON, MBTiles, GeoTIFF and many more.

When you run `brew install gdal` on macOS you get a bunch of useful binary CLI tools:

```
brew list gdal | grep bin
```
```
/opt/homebrew/Cellar/gdal/3.6.2_4/bin/nearblack
../bin/gdal_create
../bin/ogrlineref
../bin/gdaladdo
../bin/gdalinfo
../bin/gdalmdimtranslate
../bin/gdaltindex
../bin/ogr2ogr
../bin/gdaldem
../bin/gdalwarp
../bin/gdal-config
../bin/gdalsrsinfo
../bin/gdalmdiminfo
../bin/gdal_viewshed
../bin/gdallocationinfo
../bin/gdalmanage
../bin/gdal_contour
../bin/gdaltransform
../bin/gdalbuildvrt
../bin/gdal_rasterize
../bin/ogrtindex
../bin/ogrinfo
../bin/gnmmanage
../bin/gnmanalyse
../bin/gdal_translate
../bin/gdal_grid
../bin/gdalenhance
```
The two I've figured out so far (at least with respect to executing SQL) are `ogrinfo` and `ogr2ogr`.

## Example Shapefile and GeoJSON files

The [Building a location to time zone API with SpatiaLite](https://datasette.io/tutorials/spatialite) Datasette tutorial has some handy data we can use here. We'll grab the Shapefile of timezones used in that tutorial:
```
wget https://github.com/evansiroky/timezone-boundary-builder/releases/download/2022g/timezones-with-oceans.shapefile.zip
unzip timezones-with-oceans.shapefile.zip
```
And also a GeoJSON version of just the first 10 records in that data (created by the [datasette-geojson plugin](https://datasette.io/plugins/datasette-geojson)):
```
wget https://timezones.datasette.io/timezones/timezones.geojson
```

The `ogrinfo` command can be used to get information about a file:
```
ogrinfo combined-shapefile-with-oceans.shp
```
```
INFO: Open of `combined-shapefile-with-oceans.shp'
      using driver `ESRI Shapefile' successful.
1: combined-shapefile-with-oceans (Polygon)
```
```
ogrinfo timezones.geojson
```
```
INFO: Open of `timezones.geojson'
      using driver `GeoJSON' successful.
1: timezones
```
In both cases the file has a single "layer" of geospatial data.

The `-so -al` option produces a summary of the file (`-so` means "summary only", `-al` means "all layers"):
```
ogrinfo -so -al combined-shapefile-with-oceans.shp
```
```
INFO: Open of `combined-shapefile-with-oceans.shp'
      using driver `ESRI Shapefile' successful.

Layer name: combined-shapefile-with-oceans
Metadata:
  DBF_DATE_LAST_UPDATE=2022-12-02
Geometry: Polygon
Feature Count: 445
Extent: (-180.000000, -90.000000) - (180.000000, 90.000000)
Layer SRS WKT:
GEOGCRS["WGS 84",
    DATUM["World Geodetic System 1984",
        ELLIPSOID["WGS 84",6378137,298.257223563,
            LENGTHUNIT["metre",1]]],
    PRIMEM["Greenwich",0,
        ANGLEUNIT["degree",0.0174532925199433]],
    CS[ellipsoidal,2],
        AXIS["latitude",north,
            ORDER[1],
            ANGLEUNIT["degree",0.0174532925199433]],
        AXIS["longitude",east,
            ORDER[2],
            ANGLEUNIT["degree",0.0174532925199433]],
    ID["EPSG",4326]]
Data axis to CRS axis mapping: 2,1
tzid: String (80.0)
```
```
ogrinfo -so -al timezones.geojson
```
```
INFO: Open of `timezones.geojson'
      using driver `GeoJSON' successful.

Layer name: timezones
Geometry: Unknown (any)
Feature Count: 10
Extent: (-17.022378, -17.129603) - (47.982380, 37.296206)
Layer SRS WKT:
GEOGCRS["WGS 84",
    DATUM["World Geodetic System 1984",
        ELLIPSOID["WGS 84",6378137,298.257223563,
            LENGTHUNIT["metre",1]]],
    PRIMEM["Greenwich",0,
        ANGLEUNIT["degree",0.0174532925199433]],
    CS[ellipsoidal,2],
        AXIS["geodetic latitude (Lat)",north,
            ORDER[1],
            ANGLEUNIT["degree",0.0174532925199433]],
        AXIS["geodetic longitude (Lon)",east,
            ORDER[2],
            ANGLEUNIT["degree",0.0174532925199433]],
    ID["EPSG",4326]]
Data axis to CRS axis mapping: 2,1
FID Column = id
id: Integer (0.0)
tzid: String (0.0)
```
The most useful bits of these are the "feature count" (the number of features, in this case timezone polygons) and the "extent" - the bounding box of the data.

For that Shapefile the extend is the entire world. The GeoJSON file only has ten records in it' so the extent is a smaller portion of the globe.

In both cases we also have a `tzid` property.

## Querying these with SQL

This query outputs a reduced set of columns from the Shapefile:
```
ogrinfo combined-shapefile-with-oceans.shp \
  -sql 'select tzid from "combined-shapefile-with-oceans" limit 4' \
  -geom=NO \
  -q
```
The `-geom=NO` flag here (the equals sign is required) prevents the geometries themselves from being included in the results.

The SQL query passed to `-sql` selects that `tzid` and also limits to the first four rows.

The `-q` option prevents the initial information about the file (the extent and suchlike) from being displayed.

The output looks like this:
```
ogrinfo combined-shapefile-with-oceans.shp -sql 'select tzid from "combined-shapefile-with-oceans" limit 4' -geom=NO -q
```
```
Layer name: combined-shapefile-with-oceans
OGRFeature(combined-shapefile-with-oceans):0
  tzid (String) = Africa/Abidjan

OGRFeature(combined-shapefile-with-oceans):1
  tzid (String) = Africa/Accra

OGRFeature(combined-shapefile-with-oceans):2
  tzid (String) = Africa/Addis_Ababa

OGRFeature(combined-shapefile-with-oceans):3
  tzid (String) = Africa/Algiers
```
As far as I can tell `ogrinfo` does not provide advanced options for formatting the output of its results - it's intended as a debugging and exploration tool, not as a conversion tool.

## ogr2ogr to convert to GeoJSON

The `ogr2ogr` command is much more powerful: it can be used to convert from one format to another, reflecting changes defined using the SQL query.

Here's how to take the first four records from the Shapefile and convert them to GeoJSON:
```
ogr2ogr -f GeoJSON \
  -sql 'select tzid from "combined-shapefile-with-oceans" limit 4' \
  /vsistdout/ \
  combined-shapefile-with-oceans.shp
```
The `-f GeoJSON` flag tells `ogr2ogr` to output GeoJSON.

The `-sql` flag is used to define the SQL query to run.

The `/vsistdout/` argument tells `ogr2ogr` to write the output to standard output. This is a pretty weird GDAL-ism! You can provide a regular filename here instead to write to a file.

I was surprised that the output file comes before the input file.

Let's pipe this through `jq` to see what it looks like (truncated):
```
ogr2ogr -f GeoJSON \
  -sql 'select tzid from "combined-shapefile-with-oceans" limit 4' \
  /vsistdout/ \
  combined-shapefile-with-oceans.shp | jq
```
```
{
  "type": "FeatureCollection",
  "name": "combined-shapefile-with-oceans",
  "crs": {
    "type": "name",
    "properties": {
      "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
    }
  },
  "features": [
    {
      "type": "Feature",
      "properties": {
        "tzid": "Africa/Abidjan"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [
          [
            [
```
Or to see just the `tzid` properties:
```
ogr2ogr -f GeoJSON \
  -sql 'select tzid from "combined-shapefile-with-oceans" limit 4' \
  /vsistdout/ \
  combined-shapefile-with-oceans.shp | \
  jq '.features[].properties.tzid'
```
```
"Africa/Abidjan"
"Africa/Accra"
"Africa/Addis_Ababa"
"Africa/Algiers"
```
There's a huge amount more depth to these tools - this is just what I've figured out so far.
