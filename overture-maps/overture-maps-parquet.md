# Exploring the Overture Maps places data using DuckDB, sqlite-utils and Datasette

The [Overture Maps Foundation](https://overturemaps.org/) published [their first data release](https://overturemaps.org/overture-maps-foundation-releases-first-world-wide-open-map-dataset/) yesterday, and it's a really big deal. Here are my notes and first impressions of the data I've explored so far.

I'm particularly excited about the "places" data, which consists of nearly 60 million place of interest listings (businesses, attractions, anything that might show up as a point on map) from around the world, covered by a [very permissive license](https://cdla.dev/permissive-2-0/).

## Pulling GeoJSON for every country boundary

The files have been released as Parquet on Amazon S3 (and Microsoft Azure). The [official README](https://github.com/OvertureMaps/data/blob/main/README.md) has some hints on getting started.

[DuckDB](https://duckdb.org/) has the ability to query Parquet files on static hosting such as S3 without first downloading the entire files, using HTTP range requests.

I started by trying one of their demo queries. I ran everything in a Jupyter notebook.

First I installed `duckdb`:

```
%pip install duckdb`
```
After some trial and error I found I needed to run the following to enable the features I needed:
```python
import duckdb
db = duckdb.connect()
db.execute("INSTALL spatial")
db.execute("INSTALL httpfs")
db.execute("""
LOAD spatial;
LOAD httpfs;
SET s3_region='us-west-2';
""")
```
Next I ran the example query to grab the GeoJSON polygon borders for every country:
```python
db.execute("""
COPY (
    SELECT
           type,
           subType,
           localityType,
           adminLevel,
           isoCountryCodeAlpha2,
           JSON(names) AS names,
           JSON(sources) AS sources,
           ST_GeomFromWkb(geometry) AS geometry
      FROM read_parquet('s3://overturemaps-us-west-2/release/2023-07-26-alpha.0/theme=admins/type=*/*', filename=true, hive_partitioning=1)
     WHERE adminLevel = 2
       AND ST_GeometryType(ST_GeomFromWkb(geometry)) IN ('POLYGON','MULTIPOLYGON')
) TO '/tmp/countries.geojson'
WITH (FORMAT GDAL, DRIVER 'GeoJSON');
""")
```
<img width="1076" alt="Screenshot of that running in Jupyter notebook, which displays a progress bar" src="https://github.com/simonw/til/assets/9599/7f9cb0d4-fd45-4e8b-8cf4-afcbc582c5e9">

This took quite a while to run - the end result was a 138M `/tmp/countries.geojson` file!

Adding `limit 10` to that inner SELECT query got me a faster response with a smaller set of countries.

138M is a lot of data to work with. I ran the following command to pull out just the first country (Kazakhstan) and put it in my clipboard:
```bash
cat /tmp/countries.geojson | jq '.features[0]' | pbcopy
```
Then I pasted that into https://geojson.io/ and it looked like this:

<img width="1252" alt="Kazakhstan displayed with a detailed border outline on geojson.io" src="https://github.com/simonw/til/assets/9599/aed994ff-7865-4c51-81f9-4479fa78bc0a">

## Accessing places

The place data is the most interesting part of this.

I started out by running a remote query to try and count it.

First I needed to figure out the correct URL to query. After some trial and experimentation I got to this:

```
s3://overturemaps-us-west-2/release/2023-07-26-alpha.0/theme=places/type=*/*"
```
I ran a `count(*)` against that like so:
```python
places_url = "s3://overturemaps-us-west-2/release/2023-07-26-alpha.0/theme=places/type=*/*"
db.execute("select count(*) from read_parquet('{}') limit 1".format(places_url)).fetchall()
```
And got this back just a few seconds later:
```
[(59175720,)]
```
DuckDB can run queries like this really quickly, because it knows how to fetch just the header blocks of the Parquet files and read them to get a row count without fetching everything.

I decided to pull back full details of every place in my local town of Half Moon Bay. I figured out a GeoJSON boundary for that using https://boundingbox.klokantech.com/

```json
[[
    [-122.5292336382,37.4239030609],
    [-122.403920833,37.4239030609],
    [-122.403920833,37.5611068793],
    [-122.5292336382,37.5611068793],
    [-122.5292336382,37.4239030609]
]]
```
I tried running a remote query that would return places within that boundary, but quickly got tired waiting for it to complete. I don't think this dataset is set up for fast spatial queries without fetching most if not all of the file.

So I decided to download the entire thing instead.

## Downloading all 60m places

I figured out this recipe for downloading the full places dataset.

First, I installed the AWS CLI tool with `pipx`:
```bash
pipx install awscli
```
Then I ran this (after some trial and error to get the URL right):
```bash
mkdir /tmp/places
aws s3 cp --recursive 's3://overturemaps-us-west-2/release/2023-07-26-alpha.0/theme=places/' /tmp/places
```
This gave me a progress bar - it turns out it needed to download 30 files totalling 8GB:
```
Completed 79.8 MiB/8.0 GiB (7.5 MiB/s) with 30 file(s) remaining   
```
## Filtering for places in Half Moon Bay

With the data downloaded, I switched to querying locally. Here's a count:

```python
db.execute("""
select count(*) from read_parquet(
    '/tmp/places/type=place/*'
)
""").fetchall()
```
This returned the same count as before:
```
[(59175720,)]
```
I used my bounding box from earlier to count just the places in Half Moon Bay:
```python
%%time
db.execute("""
select
  count(*)
from
  read_parquet('/tmp/places/type=place/*')
where
  bbox.minx > -122.5292336382 
  and bbox.maxx < -122.403920833 
  and bbox.miny > 37.4239030609 
  and bbox.maxy < 37.5611068793
""").fetchall()
```
Adding `%%time` to a Jupyter cell causes it to report the time taken. I got back:
```
CPU times: user 3.32 s, sys: 550 ms, total: 3.87 s
Wall time: 493 ms

[(931,)]
```
So that's 931 places in Half Moon Bay.

## Exporting the places to SQLite

I use [Datasette](https://datasette.io/) for exploring data. Datasette needs that data to be in a SQLite database.

I used my [sqlite-utils](https://sqlite-utils.datasette.io/) library running in Jupyter to convert those 931 records to SQLite.

First I needed the data as a list of Python dictionaries:
```python
cursor = db.execute("""
select *
from read_parquet('/tmp/foop/type=place/*')
where
    bbox.minx > -122.5292336382 
    AND bbox.maxx < -122.403920833 
    AND bbox.miny > 37.4239030609 
    AND bbox.maxy < 37.5611068793
""")
rows = cursor.fetchall()
columns = [desc[0] for desc in cursor.description]
dicts = [dict(zip(columns, row)) for row in rows]
```
Now I can insert those into a table in a SQLite database:
```python
# %pip install sqlite-utils first if it's not installed
import sqlite_utils

hmb = sqlite_utils.Database("/tmp/hmb.db")
hmb["places"].insert_all(dicts, pk="id", replace=True)
```
The `replace=True` means that if I run this again it will replace the existing data based on matching primary keys, so I can run this command as often as I like.

I have [Datasette Desktop](https://datasette.io/desktop) installed, which means I can open the SQLite database quickly like this:

```
!open /tmp/hmb.db
```
Here's the schema:
```python
print(hmb.schema)
```
```sql
CREATE TABLE [places] (
   [id] TEXT PRIMARY KEY,
   [updatetime] TEXT,
   [version] INTEGER,
   [names] TEXT,
   [categories] TEXT,
   [confidence] FLOAT,
   [websites] TEXT,
   [socials] TEXT,
   [emails] TEXT,
   [phones] TEXT,
   [brand] TEXT,
   [addresses] TEXT,
   [sources] TEXT,
   [bbox] TEXT,
   [geometry] BLOB,
   [type] TEXT
)
```
That `bbox` column is particularly interesting, it contains JSON that looks like this:
```json
{
    "minx": -122.43049,
    "maxx": -122.43049,
    "miny": 37.46352,
    "maxy": 37.46352
}
```
The [datasette-cluster-map](https://datasette.io/plugins/datasette-cluster-map) plugin can show things on a map, but it needs the table to have `latitude` and `longitude` columns in order to do so.

I added those columns to the table using [the .convert() method](https://sqlite-utils.datasette.io/en/stable/python-api.html#converting-data-in-columns) like this:
```python
import json
hmb["places"].convert("bbox", lambda v: {
    "longitude": json.loads(v)["minx"],
    "latitude": json.loads(v)["miny"]
}, multi=True)
```
The `multi=True` option means that output columns will be created for every key in the dictionary returned  by that conversion function.

This did the trick! It added `latitude` and `longitude` columns using the `minx` and `miny` from the bounding boxes.

I hit `refresh` in Datasette (the database was already open there) and got the following:

![A Datasette Desktop window showing a map of Half Moon Bay california with 900 markers dotted around it](https://github.com/simonw/til/assets/9599/497aa4ac-a98b-44dd-a135-bef11b7d1300)

You can try this out yourself at https://hmb-overture-demo.vercel.app/hmb/places

I published that demo using [datasette-publish-vercel](https://datasette.io/plugins/datasette-publish-vercel) like this:

```bash
datasette install datasette-publish-vercel
datasette publish vercel hmb.db \
  --project hmb-overture-demo \
  --install datasette-cluster-map \
  --license 'CDLA permissive v2' \
  --license_url 'https://cdla.dev/permissive-2-0/'
```
