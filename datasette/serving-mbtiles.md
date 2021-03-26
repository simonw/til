# Serving MBTiles with datasette-media

The [MBTiles](https://github.com/mapbox/mbtiles-spec) format uses SQLite to bundle map tiles for use with libraries such as Leaflet.

I figured out how to use the [datasette-media](https://datasette.io/plugins/datasette-media) to serve tiles from this MBTiles file containing two zoom levels of tiles for San Francisco: https://static.simonwillison.net/static/2021/San_Francisco.mbtiles

This TIL is now entirely obsolete: I used this prototype to build the new [datasette-tiles](https://datasette.io/plugins/datasette-tiles) plugin.

```yaml
plugins:
  datasette-cluster-map:
    tile_layer: "/-/media/tiles/{z},{x},{y}"
    tile_layer_options:
      attribution: "© OpenStreetMap contributors"
      tms: 1
      bounds: [[37.61746256103807, -122.57290320721465],[37.85395101481279, -122.27695899334748]]
      minZoom: 15
      maxZoom: 16
  datasette-media:
    tiles:
      database: San_Francisco
      sql:
        with comma_locations as (
          select instr(:key, ',') as first_comma,
          instr(:key, ',') + instr(substr(:key, instr(:key, ',') + 1), ',') as second_comma
        ),
        variables as (
          select
            substr(:key, 0, first_comma) as z,
            substr(:key, first_comma + 1, second_comma - first_comma - 1) as x,
            substr(:key, second_comma + 1) as y
          from comma_locations
        )
        select
          tile_data as content,
          'image/png' as content_type
        from
          tiles, variables
        where
          zoom_level = variables.z
          and tile_column = variables.x
          and tile_row = variables.y
```
