# Dynamically loading multiple assets with a callback

For [datasette-leaflet-geojson](https://github.com/simonw/datasette-leaflet-geojson) I wanted to dynamically load some external CSS and JavaScript and then execute some code once they had loaded ([issue 14](https://github.com/simonw/datasette-leaflet-geojson/issues/14)).

I'm not using any frameworks for this so I wanted to do it with vanilla JavaScript.

I wanted to load the CSS and JavaScript in parallel and fire a callback function when both of them had finished loading.

Here's the pattern I came up with:
```javascript
const loadDependencies = (callback) => {
    let loaded = [];
    function hasLoaded() {
        loaded.push(this);
        if (loaded.length == 2) {
            callback();
        }
    }
    let stylesheet = document.createElement('link');
    stylesheet.setAttribute('type', 'text/css');
    stylesheet.setAttribute('rel', 'stylesheet');
    stylesheet.setAttribute('href', 'https://unpkg.com/leaflet@1.5.1/dist/leaflet.css');
    stylesheet.setAttribute('integrity', 'sha512-xwE/Az9zrjBIphAcBb3F6JVqxf46+CDLwfLMHloNu6KEQCAWi6HcDUbeOfBIptF7tcCzusKFjFw2yuvEpDL9wQ==');
    stylesheet.setAttribute('crossorigin', 'anonymous');
    stylesheet.onload = hasLoaded;
    document.head.appendChild(stylesheet);
    let script = document.createElement('script');
    script.src = 'https://unpkg.com/leaflet@1.5.1/dist/leaflet.js';
    script.setAttribute('integrity', 'sha512-GffPMF3RvMeYyc1LWMHtK8EbPv0iNZ8/oTtHPx9/cc2ILxQ+u905qIwdpULaqDkyBKgOaB57QTMg7ztg8Jm2Og==');
    script.setAttribute('crossorigin', 'anonymous');
    script.onload = stylesheet.onload = hasLoaded;
    document.head.appendChild(script);
};
```
Then called like this:
```javascript
loadDependencies(() => {
    /* Code here can use Leaflet */
});
```
