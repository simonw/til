# Loading radio.garden into SQLite using jq

http://radio.garden/ is an amazing website which displays a 3D globe covered in radio stations and lets you listen to any of them.

I wanted to have a play around with their data. I fired up the Firefox Developer Tools, switched to the Network tab and sorted by largest first, which revealed this URL to a 1.4MB JSON file:

    http://radio.garden/api/ara/content/places

I ran that through `jq` to pretty print it and see what it looked like:

    % cat places | jq | head -n 20 
    {
      "apiVersion": 1,
      "version": "e56d3ed3",
      "data": {
        "list": [
          {
            "id": "GBy0N9TE",
            "title": "Sukhumi",
            "country": "Abkhazia, Georgia",
            "url": "/visit/sukhumi/GBy0N9TE",
            "size": 1,
            "boost": true,
            "geo": [
              41.023,
              43.001
            ]
          },
          {
            "id": "PbqG2Mmi",
            "title": "Ghazni",

I need a flat JSON list to load this into `sqlite-utils`. I used `jq` to reshape the data like so:

    % cat places | jq '[.data.list[] | {id: .id, title: .title, country: .country, url: .url, size: .size, latitude: .geo[1], longitude: .geo[0]}]' | head -n 20
    [
      {
        "id": "GBy0N9TE",
        "title": "Sukhumi",
        "country": "Abkhazia, Georgia",
        "url": "/visit/sukhumi/GBy0N9TE",
        "size": 1,
        "latitude": 43.001,
        "longitude": 41.023
      },
      {
        "id": "PbqG2Mmi",
        "title": "Ghazni",
        "country": "Afghanistan",
        "url": "/visit/ghazni/PbqG2Mmi",
        "size": 1,
        "latitude": 33.545,
        "longitude": 68.417
      },
      {

Then I piped that result to `sqlite-utils`:

    % cat places | jq '[.data.list[] | {id: .id, title: .title, country: .country, url: .url, size: .size, latitude: .geo[1], longitude: .geo[0]}]' | \
      sqlite-utils insert radio.db stations - --pk=id

Here's the whole process as a one-liner:

    curl http://radio.garden/api/ara/content/places | \
      jq '[.data.list[] | {id: .id, title: .title, country: .country, url: .url, size: .size, latitude: .geo[1], longitude: .geo[0]}]' | \
      sqlite-utils insert radio.db stations - --pk=id

I then opened it in Datasette so I could do things like see it on a map and facet by country:

    datasette install datasette-cluster-map
    datasette radio.db -o
