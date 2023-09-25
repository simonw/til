# Geospatial SQL queries in SQLite using TG, sqlite-tg and datasette-sqlite-tg

[TG](https://github.com/tidwall/tg) is an exciting new project in the world of open source geospatial libraries. It's a single C file (an amalgamation, similar to that provided by SQLite) which implements the subset of geospatial operations that I most frequently find myself needing:

- Handling GeoJSON, WKT and WKB formats
- Point in polygon checks
- Shape intersection checks
- Geospatial indexing to speed up the above

TG was released on Friday. I posted [a note](https://simonwillison.net/2023/Sep/23/tg-polygon-indexing/) that "I think this could make the basis of a really useful SQLite extension—a lighter-weight alternative to SpatiaLite" in a couple of places...

... and Alex Garcia clearly agreed, because he built [sqlite-tg](https://github.com/asg017/sqlite-tg) over the weekend, and then packaged it up as a [Python package](https://pypi.org/project/sqlite-tg/), `sqlite-utils` and Datasette plugins, a [Ruby gem](https://rubygems.org/gems/sqlite-tg), a [Deno package](https://deno.land/x/sqlite_tg) and [an npm package](https://www.npmjs.com/package/sqlite-tg) too!

It's still an early alpha, but it's actually very easy to try it out. Here's how I got it working in [Datasette](https://datasette.io/).

## Installation

Since Alex released it as a Datasette plugin, you can run this:

```bash
datasette install datasette-sqlite-tg
```
Confirm installation with:
```bash
datasette plugins
```
This should just work. In my case I ran into a problem because I'd previously installed an earlier alpha and needed to upgrade the underlying `sqlite-tg` dependency, which I did like this:
```bash
datasette install sqlite-tg==0.0.1a6
```
This won't be necessary for you if you are installing it for the first time.

## Trying it out

`sqlite-tg` can work with three formats: WKT, WKB and GeoJSON.

These queries can be used to convert one to the other. Here's how to convert a WKT bounding box around San Francisco to GeoJSON:

```sql
select tg_to_geojson('POLYGON((
  -122.51610563264538 37.81424532146113,
  -122.51610563264538 37.69618409220847,
  -122.35290547288255 37.69618409220847,
  -122.35290547288255 37.81424532146113,
  -122.51610563264538 37.81424532146113
))')
```
This outputs (after pretty-printing):
```json
{
  "type": "Polygon",
  "coordinates": [
    [
      [-122.51610563264538, 37.81424532146113],
      [-122.51610563264538, 37.69618409220847],
      [-122.35290547288255, 37.69618409220847],
      [-122.35290547288255, 37.81424532146113],
      [-122.51610563264538, 37.81424532146113]
    ]
  ]
}
```
This is already useful: having an easily installed mechanism for converting between WKT and GeoJSON with a SQL query is a great thing to have.

Let's convert a point within San Francisco to WKB binary format:
```sql
select hex(tg_to_wkb('POINT(-122.4075 37.787994)'))
```
Outputs:
```
0101000000AE47E17A149A5EC0DCB8C5FCDCE44240
```
We can convert that back to GeoJSON like this:
```sql
select tg_to_geojson(x'0101000000AE47E17A149A5EC0DCB8C5FCDCE44240')
```
This is using SQLite's `x'...'` syntax to treat a hexadecimal string as a blob literal.

And here's how to confirm that our point exists within our polygon bounding box for San Francisco:
```sql
select tg_intersects('{
  "type": "Polygon",
  "coordinates": [
    [
      [-122.51610563264538, 37.81424532146113],
      [-122.51610563264538, 37.69618409220847],
      [-122.35290547288255, 37.69618409220847],
      [-122.35290547288255, 37.81424532146113],
      [-122.51610563264538, 37.81424532146113]
    ]
  ]
}', 'POINT(-122.4075 37.787994)')
```
I'm mixing GeoJSON and WKT here. I get back:
```
1
```
Because the point and the polygon intersect. Try that with Times Square in New York:
```sql
select tg_intersects('{
  "type": "Polygon",
  "coordinates": [
    [
      [-122.51610563264538, 37.81424532146113],
      [-122.51610563264538, 37.69618409220847],
      [-122.35290547288255, 37.69618409220847],
      [-122.35290547288255, 37.81424532146113],
      [-122.51610563264538, 37.81424532146113]
    ]
  ]
}', 'POINT(-73.985130 40.758896)')
```
And we get back:
```
0
```
Let's try something a bit more challenging.

## Timezone lookups

I've worked with timezone lookups using SpatiaLite and Datasette before - I even wrote [a tutorial about it](https://datasette.io/tutorials/spatialite).

I decided to try implementing a version of that on top of `sqlite-tg`.

I grabbed the latest release of `timezones.geojson.zip` from [evansiroky/timezone-boundary-builder/](https://github.com/evansiroky/timezone-boundary-builder/releases) and unzipped it to get a `combined.geojson` file that starts like this:

```json
{
  "type": "FeatureCollection",
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
              -5.440683,
              4.896553
            ],
            [
              -5.303699,
              4.912035
            ],
```
Then I loaded that into a SQLite database table using this `sqlite-utils` mechanism (explained in [What’s new in sqlite-utils 3.20 and 3.21: --lines, --text, --convert](https://simonwillison.net/2022/Jan/11/sqlite-utils/)).

```bash
sqlite-utils insert timezones.db timezones combined.json \
  --text --convert '
import json

def convert(s):
    data = json.loads(s)
    for feature in data["features"]:
        tzid = feature["properties"]["tzid"]
        yield {"tzid": tzid, "geometry": feature["geometry"]}
' --pk tzid
```
This Bash one-liner loads the entire `combined.json` file (140MB of it) into memory and then runs a snippet of Python to loop through all of those features and yield `{"tzid": "...", "geometry": {...}}` dictionaries for each timezone.

`sqlite-utils` then creates a table with this schema and inserts those records as JSON strings:

```sql
CREATE TABLE [timezones] (
   [tzid] TEXT PRIMARY KEY,
   [geometry] TEXT
);
```
The resulting database file is 160MB. You can [download a copy from here](https://static.simonwillison.net/static/2023/timezones.db).

Here's a query that can be used to find the timezone for a latitude/longitude pair:

```sql
select
  tzid
from
  timezones
where
  tg_intersects(
    'POINT (' || :longitude || ' ' || :latitude || ')',
    geometry
  )
```
I started Datasette like this:

```bash
datasette timezones.db
```
And ran that query using the `http://localhost:8001/timezones` page.

And it worked! It returned the correct timezone for the different points I tried.

The query takes around 700ms on my M2 MacBook Pro. That's not a great number - usable, but pretty taxing - but it's also not a huge surprise since this is the most naive implementation of this possible - it's doing a brute force geometry check against 160MB of JSON strings in the table.

`sqlite-tg` doesn't yet include support for indexing. TG provides some [very interesting indexing mechanisms](https://github.com/tidwall/tg/blob/main/docs/POLYGON_INDEXING.md) as part of the library.

And for added fun... I installed the [datasette-geojson-map](https://datasette.io/plugins/datasette-geojson-map) plugin and added `select *` to the query and I got this!

![Screenshot of the timezone for New York rendered on a map below the SQL query](https://static.simonwillison.net/static/2023/timezone-new-york.jpg)

