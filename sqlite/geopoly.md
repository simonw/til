# Geopoly in SQLite

I noticed this morning that one of my Datasette installations had the [Geopoly](https://www.sqlite.org/geopoly.html) SQLite extension enabled. I don't know how it got there - it has to be compiled specifically - but since it was there I decided to try it out.

The clue that it was enabled was seeing `ENABLE_GEOPOLY` listed in compile options on the `/-/versions` page.

## Importing some raw GeoJSON data

Geopoly supports "a small subset of GeoJSON". It can only handle polygons, and they have to be "simple" polygons for which the boundary does not intersect itself.

It took me a bit of work to populate a database table. I started by exporting GeoJSON for North and South America from this page:

https://geojson-maps.ash.ms/

Here's [the data I exported as a Gist](https://gist.github.com/simonw/683bf1ff7403796ae49b70be8e202e7e).

To load that into SQLite I started by installing the [datasette-write](https://datasette.io/plugins/datasette-write) plugin and starting Datasette as root:

```
datasette install datasette-write
datasette --create data.db --root -o
```
Then I visited `http://localhost:8001/-/write` and created a `raw_data` table and inserted the GeoJSON:
```
create table raw_data (text);
```
I had to replace any single `'` characters with `''` in the JSON to escape them, then I pasted in the following:
```
insert into raw_data (text) values ('{
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",...');
```
This gave me a populated `raw_data` table with a blob of JSON I could start playing with.

## Converting that to Geopoly shapes

This next bit was really tricky.

I started by creating a new table for my countries:

```sql
create virtual table countries using geopoly(name, properties);
```

My GeoJSON data contained two types of object: polygons and multipolygons.

Neither of these can be inserted directly into a Geopoly table.

GeoJSON Polygons exist as a list, where the first item in the list is the shape and subsequent items are "holes" within that shape (lakes and suchlike).

Multipolygons are a list of polygons, for example the USA has separate polygons for Alaska and Hawaii and more.

Geopoly can only handle a simple polygon - so I needed to pick a single polygon for each of my countries.

After some experimenting, I came up with the following write query to populate the table with valid polygons:

```sql
insert into countries (name, properties, _shape)
select
  json_extract(value, '$.properties.name') as name,
  json_extract(value, '$.properties') as properties,
  json_extract(value, '$.geometry.coordinates[0]') as _shape
from json_each(text, '$.features'), raw_data
where geopoly_blob(_shape) is not null
```
There are a few tricks going on here.

- `from json_each(text, '$.features'), raw_data` loops through every feature in the `$.features` list inside the `text` field in that `raw_data` table I created earlier. The join there is a little unintuitive but it works for processing JSON in a table with a single row. Each item in that array is available as `value` in the rest of the query.
- `json_extract(value, '$.properties.name')` extracts the `name` property from the `properties` object inside the GeoJSON feature - this is the name of the country.
- `json_extract(value, '$.properties')` extracts the full `properties` object as a JSON string.
- `json_extract(value, '$.geometry.coordinates[0]')` extracts the first item from the `coordinates` array inside the GeoJSON geometry object. As discussed earlier, I decided to ignore the "holes" in each polygon and just store the outer-most shape.
- `where geopoly_blob(_shape) is not null` is a trick I found to filter out invalid polygons - without this the entire query failed with an unhelpful SQL logic error.

This query turned out to do the right thing for all of the countries with a single polygon - but it skipped countries like the USA and Canada which used a multipolygon.

I eventually figured out I could import those countries as well with a second query:

```sql
insert into countries (name, properties, _shape)
select
  json_extract(value, '$.properties.name') as name,
  json_extract(value, '$.properties') as properties,
  json_extract(value, '$.geometry.coordinates[0][0]') as _shape
from json_each(text, '$.features'), raw_data
  where json_extract(value, '$.geometry.type') = 'MultiPolygon';
```
Here I'm using `$.geometry.coordinates[0][0]` to extract that outer shape from the first polygon in the multipolygon.

This worked! Having run the above two queries I had a fully populated `countries` table with 31 rows.

## What country is this point in?

I can now use the `geopoly_contains_point()` function to find which country a point is in:

```sql
select
  name, properties
from
  countries
where
  geopoly_contains_point(_shape, -84.1067362, 9.9314029)
```
The latitude and longitude of San José, Costa Rica is 9.9314029, -84.1067362. This query returns Costa Rica.

## Plotting everything on a map

I installed the [datasette-geojson-map](https://datasette.io/plugins/datasette-geojson-map) plugin by Chris Amico and used it to plot my countries on a map:

```
datasette install datasette-geojson-map
```
Then in the SQL interface:
```sql
select
  name,
  '{"coordinates": ['
  || geopoly_json(_shape) || 
  '], "type": "Polygon"}' as geometry
from
  countries
```
Here I'm using the `geopoly_json(_shape)` function to turn the binary representation of the shape in the database back into a GeoJSON polygon. Then I'm concatenating that with a little bit of wrapping JSON to create a full GeoJSON feature that looks like this (coordinates truncated):

```json
{"coordinates": [[[-82.5462,9.56613],[-82.9329,9.47681]]], "type": "Polygon"}
```

The plugin renders any GeoJSON in a column called `geometry`. The output looked like this:

<img width="765" alt="Screenshot showing that SQL query, with a map displayed below it with the outlines of all 31 countries. Argentina is notably missing." src="https://user-images.githubusercontent.com/9599/210618239-4c14bf8a-6c83-4220-b86a-047b5ea01c1d.png">

I just spotted that Argentina is missing from that map, presumably because it's a multipolygon and the first polygon in that sequence isn't the largest polygon covering that country.

## Could this handle more complex polygons?

The obvious problem with this approach is that I've over-simplified the polygons: the USA is missing two whole states and a bunch of territories, and other countries have been simplified in similar ways.

I think there's a reasonable way to handle this, with a bit more work. The trick would be to represent each country as multiple rows in the database, each row corresponding to one of the polygons in the multipolygon.

This could even be extended to handle holes in regular polygons, by running queries that can consider multiple rows and identify if a point falls within a hole and hence should not be considered as part of a country.
