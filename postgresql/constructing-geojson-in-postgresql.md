# Constructing GeoJSON in PostgreSQL

In order to efficiently generate a GeoJSON representation of a vast number of locations, I'm currently experimenting with generating the GeoJSON directly inside a PostgreSQL SQL query using `json_build_object()` and friends.

Here's my query so far, which illustrates various new patterns I've been learning - including a join against a CTE that extracts a many-to-many table into a format that can be represented in the final output as a JSON array.

```sql
with location_concordances as (
  select location.id, coalesce(
    jsonb_agg(ci.authority || ':' || ci.identifier) filter (
      where ci.authority IS NOT NULL
    ),
    '[]'
  ) as concordances
  from location
  left join concordance_location cl on location.id = cl.location_id
  left join concordance_identifier ci on ci.id = cl.concordanceidentifier_id
  group by location.id
)
SELECT
  json_build_object(
    'type', 'Feature',
    'properties', json_build_object(
      'id',
      location.public_id,
      'name',
      location.name,
      'state', state.abbreviation,
      'latitude', location.latitude,
      'longitude', location.longitude,
      'location_type', location_type.name,
      'import_ref', location.import_ref,
      'phone_number', location.phone_number,
      'full_address', location.full_address,
      'city', location.city,
      'county', county.name,
      'google_places_id', location.google_places_id,
      'vaccinefinder_location_id', location.vaccinefinder_location_id,
      'vaccinespotter_location_id', location.vaccinespotter_location_id,
      'zip_code', location.zip_code,
      'hours', location.hours,
      'website', location.website,
      'preferred_contact_method', location.preferred_contact_method,
      'provider', case 
        when provider.name is null then null
        else jsonb_build_object('name', provider.name, 'type', provider_type.name) 
      end,
      'concordances', location_concordances.concordances
    ),
    'geometry', json_build_object(
      'type', 'Point',
      'coordinates', json_build_array(location.longitude, location.latitude)
    )
  )
  from location
    join state on location.state_id = state.id
    join county on location.county_id = county.id
    join location_type on location.location_type_id = location_type.id
    join location_concordances on location.id = location_concordances.id
    left join provider on location.provider_id = provider.id
    left join provider_type on provider.provider_type_id = provider_type.id
limit 1
```
Example output from this query:
```json
{
    "type": "Feature",
    "properties": {
        "id": "rec00NpJzUnVDpLaQ",
        "name": "Kaiser Permanente Pharmacy #568",
        "state": "CA",
        "latitude": 34.081292,
        "longitude": -117.996576,
        "location_type": "Pharmacy",
        "import_ref": "vca-airtable:rec00NpJzUnVDpLaQ",
        "phone_number": "833-480-4700",
        "full_address": "12761 Schabarum Ave Plaza Level RM 1100, Irwindale, CA 91706",
        "city": null,
        "county": "Los Angeles",
        "google_places_id": "ChIJizKuijvXwoAR4VAXM2Ek4Nc",
        "vaccinefinder_location_id": null,
        "vaccinespotter_location_id": null,
        "zip_code": null,
        "hours": "Monday - Friday: 8:00 AM – 5:00 PM\nSaturday - Sunday: Closed",
        "website": null,
        "preferred_contact_method": null,
        "provider": {
            "name": "Kaiser Permanente",
            "type": "Health Plan"
        },
        "concordances": [
            "google_places:ChIJizKuijvXwoAR4VAXM2Ek4Nc"
        ]
    },
    "geometry": {
        "type": "Point",
        "coordinates": [
            -117.996576,
            34.081292
        ]
    }
}
```
## Using ST_AsGeoJSON

After writing this TIL I found a much quicker option: the `ST_AsGeoJSON()` function. This works if your table has a geometry column on it - in my case I [enhanced my location table](https://simonwillison.net/2021/May/3/adding-geodjango-to-an-existing-django-project/) to include a point column.

The following SQL generates a full GeoJSON feature row for each location in the database:

```sql
select ST_AsGeoJSON(location.*) from location
```
The `location.*` is required - if you try to use `ST_AsGeoJSON(*)` you get an error claiming that "No function matches the given name and argument types".

The output looks something like this:
```json
{
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [
      -117.65499,
      34.10835
    ]
  },
  "properties": {
    "id": 4285,
    "name": "Vons Pharmacy #2681",
    "public_id": "recbECvQlveAyBorV",
    "import_json": {
      "Name": "Vons Pharmacy #2681",
      "Hours": "Monday - Friday: 8:00 AM \u2013 8:00 PM\nSaturday - Sunday: 9:00 AM \u2013 5:00 PM",
      "County": "San Bernardino County",
      "county_id": [
        "reclZ8DWOEuoluStG"
      ]
    }
  }
}
```
That `import_json` section is a PostgreSQL JSON column in the database - note that it gets output as nested data inside the `"properties"` object.
