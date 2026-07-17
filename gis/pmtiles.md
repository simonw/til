# Serving a custom vector web map using PMTiles and maplibre-gl

[Protomaps](https://protomaps.com/) is "an open source map of the world, deployable as a single static file on cloud storage". It involves some _very_ clever technology, rooted in the [PMTiles](https://github.com/protomaps/PMTiles) file format which lets you create a single static file containing vector tile data which is designed to be hosted on static hosting but can then serve vector tiles to clients using HTTP range requests.

I figured out how to use it to create a custom map of just my local area, then serve that map using [MapLibre GL](https://maplibre.org/) from static hosting on GitHub Pages.

See [Serving a JavaScript project built using Vite from GitHub Pages](https://til.simonwillison.net/github-actions/vite-github-pages) for details of the other half of this project, where I figured out how to use Vite and how to serve Vite-built projects using GitHub Pages.

## Creating the pmtiles file

Protomaps offers [daily builds](https://maps.protomaps.com/builds/) of a single `.pmtiles` file that covers the entire world, down to a building-shape level of detail. That file is currently 107 GB!

I want to build a map of just the town I live in, Half Moon Bay.

That's where the `pmtiles` tool come in. It's a little Go binary which can download just the tiles for a specified area and build those into a new `.pmtiles` file.

It's [really easy to use](https://docs.protomaps.com/guide/getting-started).

I used [bboxfinder.com](http://bboxfinder.com/#37.373977,-122.593346,37.570977,-122.400055) to draw a rough bounding box around the area I wanted. It gave me the following coordinates:

    -122.593346,37.373977,-122.400055,37.570977 

I downloaded the latest `pmtiles` binary for Apple Silicon (the `go-pmtiles-1.10.5_Darwin_arm64.zip` file) from the [releases page](https://github.com/protomaps/go-pmtiles/releases).

Then I ran it against the URL to the latest build listed [on this page](https://maps.protomaps.com/builds/) like so:

    pmtiles extract \
      https://build.protomaps.com/20231023.pmtiles \
      hmb.pmtiles \
      --bbox=-122.593346,37.373977,-122.400055,37.570977

This only took a few seconds to run, and it produced a `hmb.pmtiles` file that was just 2 MB in size! Here's the output of the command:
```
fetching 8 dirs, 8 chunks, 8 requests
Region tiles 607, result tile entries 381
fetching 381 tiles, 30 chunks, 21 requests
fetching chunks 100% |█████████████████████████| (2.0/2.0 MB, 1.5 MB/s)        
Completed in 4.24978175s with 4 download threads (89.65166006314148 tiles/s).
Extract required 32 total requests.
Extract transferred 2.1 MB (overfetch 0.05) for an archive size of 2.0 MB
```
Amazingly, that 2 MB file includes building-shape level detail for the entire area. It also includes much less detailed tiles for the rest of the world, so you can zoom in from globe level to street level within my specified area.

You can also run the command without a `bbox` but with a `--maxzoom` to download a map of the whole world that works up to a specific zoom level, where 1 is the lowest (view the whole map at once). Zoom level 5 is only a 17 MB file:
```bash
pmtiles extract https://build.protomaps.com/20231023.pmtiles 5.pmtiles --maxzoom=5
```
Output:
```
fetching 1 dirs, 1 chunks, 1 requests
Region tiles 1365, result tile entries 1101
fetching 1101 tiles, 1 chunks, 1 requests
fetching chunks 100% |█████████████████████████| (16/16 MB, 26 MB/s)        
Completed in 1.519326s with 4 download threads (724.6634162544027 tiles/s).
Extract required 5 total requests.
Extract transferred 17 MB (overfetch 0.05) for an archive size of 17 MB
```
Add `--dry-run` to see the size without downloading the files - for example:
```
pmtiles extract https://build.protomaps.com/20231023.pmtiles OUTPUT.pmtiles --maxzoom=6 --dry-run
```
Which shows that zoom level 6 would be 46 MB:
```
fetching 1 dirs, 1 chunks, 1 requests
Region tiles 5461, result tile entries 4832
fetching 4832 tiles, 1 chunks, 1 requests
Completed in 631.8625ms with 4 download threads (7647.232372992088 tiles/s).
Extract required 5 total requests.
Extract transferred 46 MB (overfetch 0.05) for an archive size of 46 MB
```
If you just need a very high level world map, zoom level 1 is only 495 KB.

## Exploring the pmtiles file

The https://protomaps.github.io/PMTiles/ tool can be used to explore a `.pmtiles` file.

You can drop the file directly onto the page, which gave me this:

![PMTiles Viewer showing a vector map centered on the Pillar Point Harbor near Half Moon Bay](https://github.com/simonw/til/assets/9599/8c1c867f-8802-43aa-a13b-dc68e79af87c)

The Metadata tab confirms that the file covers roughly the expected bounding box area:

![Metadata tab includes this: num addressed tiles: 607, num tile entries: 381, num tile contents: 336, min zoom: 0, max zoom: 15, min lon, min lat, max lon, max lat: -122.593346, 37.3739769, -122.400055, 37.570977](https://github.com/simonw/til/assets/9599/f028f997-083c-4fa4-93a2-ecfe0dca9356)

## Serving the map using Vite and maplibre-gl

I decided to build a web page that would serve an interactive version of the map.

I ended up putting this together with Vite (see [other TIL](https://til.simonwillison.net/github-actions/vite-github-pages)) and `maplibre-gl`.

I ran these commands:

```bash
npx create-vite@latest hmb-map --template vanilla
cd hmb-map
npm install
npm install maplibre-gl
npm install pmtiles
npm install protomaps-themes-base
```
After _much_ iteration I got to a version that worked.

My `index.html` ended up looking like this:

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Map</title>
    <style>
      body,
      html {
        margin: 0;
        padding: 0;
      }
      #map {
        width: 100vw;
        height: 100vh;
      }
    </style>
  </head>
  <body>
    <div id="map"></div>
    <script type="module" src="/main.js"></script>
  </body>
</html>
```
And `main.js` like this:

```javascript
import * as pmtiles from "pmtiles";
import * as maplibregl from "maplibre-gl";
import layers from "protomaps-themes-base";

const protocol = new pmtiles.Protocol();
maplibregl.addProtocol("pmtiles", protocol.tile);

const myMap = new maplibregl.Map({
  container: "map",
  style: {
    version: 8,
    glyphs: "https://cdn.protomaps.com/fonts/pbf/{fontstack}/{range}.pbf",
    sources: {
      protomaps: {
        type: "vector",
        url: `pmtiles://${location.protocol}//${location.host}${location.pathname}hmb.pmtiles`,
        attribution:
          '<a href="https://protomaps.com">Protomaps</a> © <a href="https://openstreetmap.org">OpenStreetMap</a>',
      },
    },
    layers: layers("protomaps", "light"),
  },
});
myMap.on("load", () => {
  const myBounds = myMap.getSource("protomaps").bounds;
  myMap.setMaxBounds(myBounds);
});
```
I copied my `hmb.pmtiles` file into the `public/` directory.

To run the dev server:

```bash
npm run dev
```

This served a live-reloading version of the map at `http://localhost:5174/`.

Breaking down the code a little. My `index.html` mainly exists to provide a `<div id="map"></div>` element for the map to render in.

It's set to `width: 100vw; height: 100vh` which means it will fill the entire browser window (since body and html both have no padding or margin).

Vite uses `index.html` as the main entrypoint - so it knows that `main.js` should have magic bundling applied to it.

I ended up needing three dependencies: `pmtiles`, `maplibre-gl` and `protomaps-themes-base`. Those are all loaded at the top of `main.js`:

```javascript
import * as pmtiles from "pmtiles";
import * as maplibregl from "maplibre-gl";
import layers from "protomaps-themes-base";
```
- `pmtiles` upgrades `maplibre-gl` to be able to load the special PMTiles vector format.
- `maplibre-gl` is the core WebGL library that renders the map.
- `protomaps-themes-base` provides a set of default styles for the layers of the map - green for land, blue for sea etc.

This code sets up the `pmtiles://` protocol handler:

```javascript
const protocol = new pmtiles.Protocol();
maplibregl.addProtocol("pmtiles", protocol.tile);
```

Most of the rest of the work is done in the `Map()` constructor:
```javascript
const myMap = new maplibregl.Map({
  container: "map",
  style: {
    version: 8,
    glyphs: "https://cdn.protomaps.com/fonts/pbf/{fontstack}/{range}.pbf",
    sources: {
      protomaps: {
        type: "vector",
        url: `pmtiles://${location.protocol}//${location.host}${location.pathname}hmb.pmtiles`,
        attribution:
          '<a href="https://protomaps.com">Protomaps</a> © <a href="https://openstreetmap.org">OpenStreetMap</a>',
      },
    },
    layers: layers("protomaps", "light"),
  },
});
```
You can also self host the glyphs, by downloading them from here: [https://github.com/protomaps/basemaps-assets](https://github.com/protomaps/basemaps-assets)

I needed to specify a full URL to my `hmb.pmtiles` file. In my development environment that's `http://localhost:5174/hmb.pmtiles` - but in production it's `https://simonw.github.io/hmb-map/hmb.pmtiles` - so I had to dynamically assemble that URL using the `location.protocol` and `location.host` and `location.pathname` properties.

The `layers()` function is provided by `protomaps-themes-base` and returns an array of layer definitions that can be used to render the map.

There was one last step: my map was loading showing the entire globe, but I wanted to restrict it to only allowing the user to zoom within the area defined by my `hmb.pmtiles` file.

I ended up doing that using an onload handler:

```javascript
myMap.on("load", () => {
  const myBounds = myMap.getSource("protomaps").bounds;
  myMap.setMaxBounds(myBounds);
});
```
This code needs to run on load because otherwise the `myMap.getSource()` method fails.

Here we read the `bounds` property for our `protomaps` source and then use that to set the max bounds for the overall map.

## The finished map

I [deployed this with GitHub Pages](https://til.simonwillison.net/github-actions/vite-github-pages) and it can now be seen at https://simonw.github.io/hmb-map/

<img width="1022" alt="Screenshot of a map centered on El Granada" src="https://github.com/simonw/til/assets/9599/a9d090c2-1015-4942-99e2-554599b2f98a">

## Adding markers

In a previous TIL I [extracted 900 point locations in Half Moon Bay](https://til.simonwillison.net/overture-maps/overture-maps-parquet#user-content-filtering-for-places-in-half-moon-bay) from the Overture Maps places dataset.

I decided to add those to my new map the simplest way possible, by dropping in [a static JSON file](https://github.com/simonw/hmb-map/blob/main/public/places.json) (1.24MB).

Then I added this to the JavaScript to load that JSON file and use it to populate markers for every point:

```javascript
myMap.on("load", () => {
  const myBounds = myMap.getSource("protomaps").bounds;
  myMap.setMaxBounds(myBounds);
  // Now load the places.json
  fetch("places.json").then((response) => {
    response.json().then((data) => {
      data.rows.forEach((row) => {
        const categories = JSON.parse(row.categories);
        const catlist = [categories.main, ...(categories.alternate || [])].join(
          ", ",
        );
        let color = '#000080';
        if (/store|shop/.test(catlist)) {
          color = '#006400';
        }
        if (/restaurant|cafe/.test(catlist)) {
          color = '#FFA500';
        };
        const name = JSON.parse(row.names).value[0][0].value[0];
        const marker = new maplibregl.Marker({ scale: 0.5, color: color });
        marker
          .setLngLat([row.longitude, row.latitude])
          .setPopup(
            new maplibregl.Popup().setHTML(
              `<strong>${name}</strong><br>${catlist}`,
            ),
          );
        marker.addTo(myMap);
      });
    });
  });
});
```
The JSON format is a bit untidy, hence the `JSON.parse()` calls. But this works!

I'm using a very simple set of regular expressions to show shops and restaurants with different marker colors.

At first the markers were displaying in the wrong places, and the popup windows corrupted the display of the map. It turns out this is because I hadn't loaded the `maplibre-gl.css` file.

I added this to `index.html`:

```html
<link rel="stylesheet" href="maplibre-gl.css">
```
And dropped a copy of the [maplibre-gl.css](https://github.com/simonw/hmb-map/blob/main/public/maplibre-gl.css) file into my `public/` directory.

This fixed it, and now my map looks like this:

![The map is now scattered with dark blue markers. One of them has a popup open, reading La Costanera: latin_american_restaurant, peruvian_restaurant, seafood_restaurant](https://github.com/simonw/til/assets/9599/82e5739b-13d8-4289-80d2-72716016d2b5)
