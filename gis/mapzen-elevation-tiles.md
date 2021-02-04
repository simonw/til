# Downloading MapZen elevation tiles

[Via Tony Hirst](https://twitter.com/psychemedia/status/1357280624319553537) I found out about [MapZen's elevation tiles](https://www.mapzen.com/blog/terrain-tile-service/), which encode elevation data in PNG and other formats.

These days they live at https://registry.opendata.aws/terrain-tiles/

I managed to download a subset of them using [download-tiles](https://datasette.io/tools/download-tiles) like so:

```
download-tiles elevation.mbtiles -z 0-4 \
  --tiles-url='https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png'
```
I'm worried I may have got the x and y the wrong way round though, see comments on https://github.com/simonw/datasette-tiles/issues/15
