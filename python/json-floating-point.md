# Outputting JSON with reduced floating point precision

[datasette-leaflet-geojson](github.com/simonw/datasette-leaflet-geojson) outputs GeoJSON geometries in HTML pages in a way that can be picked up by JavaScript and used to plot a Leaflet map.

These geometries often look something like this:

```
{
  "type":"MultiPolygon",
  "coordinates":[[[[-122.4457678900319,37.77292891669105],[-122.441075063058,37.77352490695095]...
```
[Decimal_degrees: Precision on Wikipedia](https://en.wikipedia.org/wiki/Decimal_degrees#Precision) says that `0.00001` should be accurate to within around a meter.

Shortening these floating point representations can shave 100KB+ off an HTML page with a lot of GeoJSON shapes on it!

There's [a lengthy Stack Overflow](https://stackoverflow.com/questions/1447287/format-floats-with-standard-json-module) about this but it's difficult to follow because ways of doing this changed between Python 2 and Python 3. Here's what worked for me:
```python

def round_floats(o):
    if isinstance(o, float):
        return round(o, 5)
    if isinstance(o, dict):
        return {k: round_floats(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [round_floats(x) for x in o]
    return o

data = json.dumps(round_floats(data))
```
See [issue 11](https://github.com/simonw/datasette-leaflet-geojson/issues/11) for details.
