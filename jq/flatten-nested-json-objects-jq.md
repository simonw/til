# Flattening nested JSON objects with jq

I wanted to take a nested set of JSON objects and import them into a SQLite database using `sqlite-utils insert` - but I wanted to "flatten" some of the nested rows.

Example data:
```json
{
  "status": "success",
  "data": {
    "generated": "2021-02-18T20:14:02.288Z",
    "sites": [
      {
        "id": "full_data",
        "name": "Moscone Center South (full data)",
        "active": true,
        "location": {
          "address": "747 Howard St, San Francisco, CA 94103",
          "url": "https://www.google.com/maps/place/Moscone+Center+South,+747+Howard+St,+San+Francisco,+CA+94103",
          "lng": -122.401253,
          "lat": 37.78392
        },
        "info": {
          "url": "https://sf.gov/location/moscone-center-south-covid-19-vaccine-site"
        },
        "booking": {
          "url": "https://myturn.ca.gov",
          "dropins": false,
          "info": null
        },
        "access": {
          "wheelchair": true,
          "languages": {
            "en": true,
            "es": true,
            "zh": true,
            "fil": false,
            "vi": false,
            "ru": false
          },
          "remote_translation": {
            "available": false,
            "info": null
          }
        },
        "access_mode": {
          "walk": true,
          "drive": false
        },
        "open_to": {
          "everyone": true,
          "text": "Open to the public"
        },
        "appointments": {
          "available": true,
          "last_updated": "2021-02-18T20:14:02.288Z"
        },
        "eligibility": {
          "65_and_over": true,
          "healthcare_workers": true,
          "education_and_childcare": false,
          "agriculture_and_food": false,
          "emergency_services": false
        }
      }
    ]
  }
}
```
I wanted to turn this into an array of non-nested objects, like this:
```json
[
  {
    "id": "full_data",
    "name": "Moscone Center South (full data)",
    "active": true,
    "location_address": "747 Howard St, San Francisco, CA 94103",
    "location_url": "https://www.google.com/maps/place/Moscone+Center+South,+747+Howard+St,+San+Francisco,+CA+94103",
    "location_lng": -122.401253,
    "location_lat": 37.78392
  }
]
```
Thanks to [this StackOverflow answer](https://stackoverflow.com/a/37555908) I found the following `jq` fragment:
```jq
[leaf_paths as $path | {
    "key": $path | join("_"), "value": getpath($path)
}] | from_entries
```
This fragment transforms a nested JSON object into a flat one with `"location_address"` style keys instead.

I like trying these things out in interactive tools - https://www.jqkungfu.com/ is my current favourite, which runs the original `jq` in your browser compiled to WebAssembly.

I pasted in the example from above and then used this `jq` query to confirm that it works - the `.data.sites[] | [ ... ]` pattern here pulls out the `["data"]["sites"]` array and applies the flatten transformation to every item within it: 

    .data.sites[] | [ [leaf_paths as $path | {"key": $path | join("_"), "value": getpath($path)}] | from_entries ]

It worked!

The final, full recipe I used to pull down the JSON, transform and flatten it and insert it into a SQLite database was this:

```bash
curl 'https://vaccination-site-microservice.vercel.app/api/v1/sites' | \
  jq .data.sites | jq '
    [.[] | 
    [leaf_paths as $path | {"key": $path | join("_"), "value": getpath($path)}]
    | from_entries]
  ' | \
  sqlite-utils insert /tmp/sf.db sites -
```
