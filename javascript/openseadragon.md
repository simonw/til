# Creating a tiled zoomable image with OpenSeadragon and vips

The San Francisco Microscopical Society has some extremely high resolution scanned images - one of them is a 1.67GB PNG file with a 25,088 × 17,283 pixel resolution.

I wanted to display these in a browser using a zoomed interface, without needing to load in that whole file.

[OpenSeadragon](https://openseadragon.github.io/) looked like a good fit for this:

> An open-source, web-based viewer for **high-resolution zoomable images**, implemented in pure JavaScript, for desktop and mobile.

## Creating the tiles with vips

The first step in using it is to split the source image up into a set of tiles.

OpenSeadragon offers a [range of options](http://openseadragon.github.io/examples/creating-zooming-images/) for doing this. After investigating a few the one that worked best for me was [vips](https://www.libvips.org/), with its [vips dzsave](https://www.libvips.org/API/current/Making-image-pyramids.html) command.

Installing this on macOS with Homebrew:

    brew install vips

Once installed you can split a source image into tiles like this:

    vips dzsave Miniature_Victorian_Slide_Collection.png \
      Miniature_Victorian_Slide_Collection

This command runs _really_ quickly: it took just a few seconds, and Activity Monitor showed it using more than 600% CPU, so it is clearly optimized to make full use of multiple cores.

This command creates an XML file called `Miniature_Victorian_Slide_Collection.dzi` defining the zoomed tile set, and a folder called `Miniature_Victorian_Slide_Collection_files` containing thousands of smaller tiles, arranged in a hierarchy.
```
% find . | grep Miniat | wc -l
    5233
```
That's a LOT of files. They were each around 256 × 256 in resolution - I deceded to see if I could make them bigger and reduce their number.

I used the `--tile-size` option to do this:

    vips dzsave Miniature_Victorian_Slide_Collection.png \
      Miniature_Victorian_Slide_Collection-tile-size-512 \
      --tile-size 512

This created a more manageable 1,343 files, totalling 25.2MB.

## Implementing the viewer

Here's the minimal HTML I figured out to create a zoomable viewer that takes up the full browser viewport:

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<style>
#openseadragon1 {
  width: 100vw;
  height: 100vh;
}
body {
  margin: 0;
  padding: 0;
}
</style>

<div id="openseadragon1"></div>
<script src="https://cdn.jsdelivr.net/npm/openseadragon@3.1/build/openseadragon/openseadragon.min.js"></script>
<script type="text/javascript">
var viewer = OpenSeadragon({
  id: "openseadragon1",
  prefixUrl: "https://cdn.jsdelivr.net/npm/openseadragon@3.1.0/build/openseadragon/images/",
  tileSources: "Miniature_Victorian_Slide_Collection-tile-size-512.dzi"
});
</script>
```
Saving this as `index.html` in the same folder as the `.dzi` file and then serving it like this let me start zooming and interacting with the tiled image:

    python3 -m http.server
