# Natural Earth in SpatiaLite and Datasette

Natural Earth ([website](https://www.naturalearthdata.com/), [Wikipedia](https://en.wikipedia.org/wiki/Natural_Earth)) is a a public domain map dataset.

It's distributed in a bunch of different formats - one of them is a SQLite database file.

http://naciscdn.org/naturalearth/packages/natural_earth_vector.sqlite.zip - this is a 423MB file which decompresses to provide a 791MB `packages/natural_earth_vector.sqlite` file.

I opened it in Datasette like this:

    datasette --load-extension spatialite \
      ~/Downloads/natural_earth_vector.sqlite/packages/natural_earth_vector.sqlite

I had previously installed Datasette and SpatiaLite using Homebrew:

    brew install datasette spatialite-tools

## Database format

The database contains 181 tables, for different layers at different scales. Those tables are listed below.

Each table has a bunch of columns and a `GEOMETRY` column. That geometry column contains data stored in WKB - Well-Known Binary format.

If you have SpatiaLite you can convert that column to GeoJSON like so:

    AsGeoJSON(GeomFromWKB(GEOMETRY))

For example, here are the largest "urban areas" at 50m scale:

```sql
select
  AsGeoJSON(GeomFromWKB(GEOMETRY))
from
  ne_50m_urban_areas
order by area_sqkm desc
```
Every country at 50m scale (a good balance between detail and overall size):
```sql
select
  AsGeoJSON(GeomFromWKB(GEOMETRY)), *
from
  ne_50m_admin_0_countries
```

This query draws a coloured map of countries using the `datasette-geojson-map` and `sqlite-colorbrewer` plugins:

```sql
select
  ogc_fid,
  GeomFromWKB(GEOMETRY) as geometry,
  colorbrewer('Paired', 9, MAPCOLOR9 - 1) as fill
from
  ne_10m_admin_0_countries
```

<img width="1098" alt="Screenshot of a map showing different countries in random colours" src="https://user-images.githubusercontent.com/9599/156858327-08f99300-29fd-4ca8-a268-f8c2ec659349.png">

The `ne_10m_admin_1_states_provinces` table is useful: it has subdivisions for a bunch of different countries. Here's the UK divided into counties:

```sql
select
  ogc_fid,
  GeomFromWKB(GEOMETRY) as geometry,
  featurecla,
  scalerank,
  adm1_code,
  diss_me,
  iso_3166_2,
  wikipedia,
  iso_a2,
  adm0_sr,
  name,
  name_alt,
  type,
  type_en,
  area_sqkm,
  latitude,
  longitude,
  admin
from
  ne_10m_admin_1_states_provinces
where
  admin = 'United Kingdom'
```
I tried this with `select *, GeomFromWKB(GEOMETRY) as geometry` first but it didn't work with `datasette-geojson-map` because the `*` picked up the original `GEOMETRY` column in the wrong format.

The scales are:

- Large scale data, 1:10m - most detailed
- Medium scale data, 1:50m
- Small scale data, 1:110m - least detailed

## Exploring with Datasette plugins

With the `datasette-leaflet-geojson` plugin installed, any column that returns GeoJSON (from `AsGeoJSON(GeomFromWKB(GEOMETRY))`) will render as a little map, no matter what the column name.

If you install `datasette-geojson-map` you can seee a single map with all of the shapes on - you need to create a `geometry` column containing a SpatiaLite geometry, which you can do like this:
```sql
select
  ogc_fid, GeomFromWKB(GEOMETRY) as geometry, *
from
  ne_50m_coastline
```
## Full list of tables

- `ne_10m_admin_0_antarctic_claim_limit_lines`
- `ne_10m_admin_0_antarctic_claims`
- `ne_10m_admin_0_boundary_lines_disputed_areas`
- `ne_10m_admin_0_boundary_lines_land`
- `ne_10m_admin_0_boundary_lines_map_units`
- `ne_10m_admin_0_boundary_lines_maritime_indicator`
- `ne_10m_admin_0_boundary_lines_maritime_indicator_chn`
- `ne_10m_admin_0_countries`
- `ne_10m_admin_0_countries_arg`
- `ne_10m_admin_0_countries_bdg`
- `ne_10m_admin_0_countries_bra`
- `ne_10m_admin_0_countries_chn`
- `ne_10m_admin_0_countries_deu`
- `ne_10m_admin_0_countries_egy`
- `ne_10m_admin_0_countries_esp`
- `ne_10m_admin_0_countries_fra`
- `ne_10m_admin_0_countries_gbr`
- `ne_10m_admin_0_countries_grc`
- `ne_10m_admin_0_countries_idn`
- `ne_10m_admin_0_countries_ind`
- `ne_10m_admin_0_countries_isr`
- `ne_10m_admin_0_countries_ita`
- `ne_10m_admin_0_countries_jpn`
- `ne_10m_admin_0_countries_kor`
- `ne_10m_admin_0_countries_lakes`
- `ne_10m_admin_0_countries_mar`
- `ne_10m_admin_0_countries_nep`
- `ne_10m_admin_0_countries_nld`
- `ne_10m_admin_0_countries_pak`
- `ne_10m_admin_0_countries_pol`
- `ne_10m_admin_0_countries_prt`
- `ne_10m_admin_0_countries_pse`
- `ne_10m_admin_0_countries_rus`
- `ne_10m_admin_0_countries_sau`
- `ne_10m_admin_0_countries_swe`
- `ne_10m_admin_0_countries_tur`
- `ne_10m_admin_0_countries_twn`
- `ne_10m_admin_0_countries_ukr`
- `ne_10m_admin_0_countries_usa`
- `ne_10m_admin_0_countries_vnm`
- `ne_10m_admin_0_disputed_areas`
- `ne_10m_admin_0_disputed_areas_scale_rank_minor_islands`
- `ne_10m_admin_0_label_points`
- `ne_10m_admin_0_map_subunits`
- `ne_10m_admin_0_map_units`
- `ne_10m_admin_0_names`
- `ne_10m_admin_0_pacific_groupings`
- `ne_10m_admin_0_scale_rank`
- `ne_10m_admin_0_scale_rank_minor_islands`
- `ne_10m_admin_0_seams`
- `ne_10m_admin_0_sovereignty`
- `ne_10m_admin_1_label_points`
- `ne_10m_admin_1_label_points_details`
- `ne_10m_admin_1_seams`
- `ne_10m_admin_1_sel`
- `ne_10m_admin_1_states_provinces`
- `ne_10m_admin_1_states_provinces_lakes`
- `ne_10m_admin_1_states_provinces_lines`
- `ne_10m_admin_1_states_provinces_scale_rank`
- `ne_10m_admin_1_states_provinces_scale_rank_minor_islands`
- `ne_10m_admin_2_counties`
- `ne_10m_admin_2_counties_lakes`
- `ne_10m_admin_2_counties_lines`
- `ne_10m_admin_2_counties_scale_rank`
- `ne_10m_admin_2_counties_scale_rank_minor_islands`
- `ne_10m_admin_2_counties_to_match`
- `ne_10m_admin_2_label_points`
- `ne_10m_admin_2_label_points_details`
- `ne_10m_airports`
- `ne_10m_antarctic_ice_shelves_lines`
- `ne_10m_antarctic_ice_shelves_polys`
- `ne_10m_coastline`
- `ne_10m_geographic_lines`
- `ne_10m_geography_marine_polys`
- `ne_10m_geography_regions_elevation_points`
- `ne_10m_geography_regions_points`
- `ne_10m_geography_regions_polys`
- `ne_10m_glaciated_areas`
- `ne_10m_lakes`
- `ne_10m_lakes_australia`
- `ne_10m_lakes_europe`
- `ne_10m_lakes_historic`
- `ne_10m_lakes_north_america`
- `ne_10m_lakes_pluvial`
- `ne_10m_land`
- `ne_10m_land_ocean_label_points`
- `ne_10m_land_ocean_seams`
- `ne_10m_land_scale_rank`
- `ne_10m_minor_islands`
- `ne_10m_minor_islands_coastline`
- `ne_10m_minor_islands_label_points`
- `ne_10m_ocean`
- `ne_10m_ocean_scale_rank`
- `ne_10m_parks_and_protected_lands_area`
- `ne_10m_parks_and_protected_lands_line`
- `ne_10m_parks_and_protected_lands_point`
- `ne_10m_parks_and_protected_lands_scale_rank`
- `ne_10m_playas`
- `ne_10m_populated_places`
- `ne_10m_populated_places_simple`
- `ne_10m_ports`
- `ne_10m_railroads`
- `ne_10m_railroads_north_america`
- `ne_10m_reefs`
- `ne_10m_rivers_australia`
- `ne_10m_rivers_europe`
- `ne_10m_rivers_lake_centerlines`
- `ne_10m_rivers_lake_centerlines_scale_rank`
- `ne_10m_rivers_north_america`
- `ne_10m_roads`
- `ne_10m_roads_north_america`
- `ne_10m_time_zones`
- `ne_10m_urban_areas`
- `ne_10m_urban_areas_landscan`
- `ne_110m_admin_0_boundary_lines_land`
- `ne_110m_admin_0_countries`
- `ne_110m_admin_0_countries_lakes`
- `ne_110m_admin_0_map_units`
- `ne_110m_admin_0_pacific_groupings`
- `ne_110m_admin_0_scale_rank`
- `ne_110m_admin_0_sovereignty`
- `ne_110m_admin_0_tiny_countries`
- `ne_110m_admin_1_states_provinces`
- `ne_110m_admin_1_states_provinces_lakes`
- `ne_110m_admin_1_states_provinces_lines`
- `ne_110m_admin_1_states_provinces_scale_rank`
- `ne_110m_coastline`
- `ne_110m_geographic_lines`
- `ne_110m_geography_marine_polys`
- `ne_110m_geography_regions_elevation_points`
- `ne_110m_geography_regions_points`
- `ne_110m_geography_regions_polys`
- `ne_110m_glaciated_areas`
- `ne_110m_lakes`
- `ne_110m_land`
- `ne_110m_ocean`
- `ne_110m_populated_places`
- `ne_110m_populated_places_simple`
- `ne_110m_rivers_lake_centerlines`
- `ne_50m_admin_0_boundary_lines_disputed_areas`
- `ne_50m_admin_0_boundary_lines_land`
- `ne_50m_admin_0_boundary_lines_maritime_indicator`
- `ne_50m_admin_0_boundary_lines_maritime_indicator_chn`
- `ne_50m_admin_0_boundary_map_units`
- `ne_50m_admin_0_breakaway_disputed_areas`
- `ne_50m_admin_0_breakaway_disputed_areas_scale_rank`
- `ne_50m_admin_0_countries`
- `ne_50m_admin_0_countries_lakes`
- `ne_50m_admin_0_map_subunits`
- `ne_50m_admin_0_map_units`
- `ne_50m_admin_0_pacific_groupings`
- `ne_50m_admin_0_scale_rank`
- `ne_50m_admin_0_sovereignty`
- `ne_50m_admin_0_tiny_countries`
- `ne_50m_admin_0_tiny_countries_scale_rank`
- `ne_50m_admin_1_seams`
- `ne_50m_admin_1_states_provinces`
- `ne_50m_admin_1_states_provinces_lakes`
- `ne_50m_admin_1_states_provinces_lines`
- `ne_50m_admin_1_states_provinces_scale_rank`
- `ne_50m_airports`
- `ne_50m_antarctic_ice_shelves_lines`
- `ne_50m_antarctic_ice_shelves_polys`
- `ne_50m_coastline`
- `ne_50m_geographic_lines`
- `ne_50m_geography_marine_polys`
- `ne_50m_geography_regions_elevation_points`
- `ne_50m_geography_regions_points`
- `ne_50m_geography_regions_polys`
- `ne_50m_glaciated_areas`
- `ne_50m_lakes`
- `ne_50m_lakes_historic`
- `ne_50m_land`
- `ne_50m_ocean`
- `ne_50m_playas`
- `ne_50m_populated_places`
- `ne_50m_populated_places_simple`
- `ne_50m_ports`
- `ne_50m_rivers_lake_centerlines`
- `ne_50m_rivers_lake_centerlines_scale_rank`
- `ne_50m_urban_areas`



