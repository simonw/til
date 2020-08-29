# Converting Airtable JSON for use with sqlite-utils using jq

The Airtable API outputs JSON that looks like this:

```json
{
  "records": [
    {
      "id": "rec0kmRncBsXrJBSe",
      "fields": {
        "area": "Morro bay",
        "Name": "North Point Beach",
        "body": "North Point Natural Area has some great tide pools at low tide. They are located north of Morro Strand State Beach between the towns of Morro Bay and Cayucos.",
        "website_url": "http://www.californiabeaches.com/beach/north-point-beach/"
      },
      "createdTime": "2017-11-26T01:54:47.000Z"
    },
    {
      "id": "rec0sW0dbM6X1bVRr",
      "fields": {
        "area": "Pismo beach",
        "Name": "Spyglass beach",
        "body": "The Shell Beach area has many tidepool areas along its rugged shoreline. Head to just about any of the beaches here at low tide and you’ll find excellent tide pools. Our favorite access point for tide pools is the one at Spyglass Park.",
        "website_url": "http://www.californiabeaches.com/beach/spyglass-park/"
      },
      "createdTime": "2017-11-26T01:57:33.000Z"
    }
  ]
}
```
The items in the `records` array each have an `id`, a nested `fields` dictionary and a `createdTime`.

I want to pipe these into `sqlite-utils insert` - but that requires a flat JSON list of dictionaries like this:

```json
[
  {
    "id": "rec0kmRncBsXrJBSe",
    "area": "Morro bay",
    "Name": "North Point Beach",
    "body": "North Point Natural Area has some great tide pools at low tide. They are located north of Morro Strand State Beach between the towns of Morro Bay and Cayucos.",
    "website_url": "http://www.californiabeaches.com/beach/north-point-beach/",
    "createdTime": "2017-11-26T01:54:47.000Z"
  },
  {
    "id": "rec0sW0dbM6X1bVRr",
    "area": "Pismo beach",
    "Name": "Spyglass beach",
    "body": "The Shell Beach area has many tidepool areas along its rugged shoreline. Head to just about any of the beaches here at low tide and you’ll find excellent tide pools. Our favorite access point for tide pools is the one at Spyglass Park.",
    "website_url": "http://www.californiabeaches.com/beach/spyglass-park/",
    "createdTime": "2017-11-26T01:57:33.000Z"
  }
]
```
Can I use https://stedolan.github.io/jq/ to convert between the two? it turns out I can:

    cat airtable.json | jq '[.records[] | {id: .id} + .fields + {createdTime: .createdTime}]'

This loops through each item in the `.records` list and for each one creates a new JSON object that concatenates the `id`, all of the `.fields` and the `createdTime`.

I can then pipe that into `sqlite-utils` to create a SQLite table from it. Here's the full recipe:

    curl "https://api.airtable.com/v0/appZOGvNJPXCQ205F/Tidepool%20areas" \
      -H "Authorization: Bearer xxx" | \
      jq '[.records[] | {id: .id} + .fields + {createdTime: .createdTime}]' | \
      sqlite-utils insert tidepools.db tidepools - --pk=id
