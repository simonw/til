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
## Suggestions from Carl Johnson

[@carlmjohnson commented](https://github.com/simonw/til/commit/f40b5a6483f2979f4973d8af50ff9e9855f2b388#comments):

> Two suggestions. 
> 
> First, the Javascript is overly complicated with pushing `this` (?) to an array. I think the reason you're doing this is because you are subconsciously influenced by Python which has broken nonlocals by default. Even ES5 Javascript, however, respects `var` declarations, and you're using `let`, which is ES6. So, you can radically simplify this:
> 
> ```JavaScript
> const loadDependencies = (callback) => {
>     let loaded = 0;
>     function hasLoaded() {
>         loaded++;
>         if (loaded == 2) {
>             callback();
>         }
>     }
> ```
> 
> Two, you can radically complicate this. :-) The idiomatic way in JavaScript to deal with callbacks is to _convert them to promises as soon as possible_. Again, you're writing ES6 (arrow funcs, `const`, `let`) anyway, plus this is a hobby project, so don't let IE11 hold you back. Just use a promise. Again, I think you're influenced by Python, in which async is a big deal architecturally and you can't just drop it in anywhere. In JS, because it's single threaded by the spec, you can just drop in async any time you like and converting callbacks to Promises is trivial. There are two options for converting to promises, first you can keep your existing API:
> 
> ```JavaScript
> const resolveOnLoad = (el) =>
>   new Promise((resolve) => {
>     el.onload = resolve;
>   });
> 
> const loadDependencies = (callback) => {
>     let stylesheet = document.createElement('link');
>     stylesheet.setAttribute('type', 'text/css');
>     stylesheet.setAttribute('rel', 'stylesheet');
>     stylesheet.setAttribute('href', 'https://unpkg.com/leaflet@1.5.1/dist/leaflet.css');
>     stylesheet.setAttribute('integrity', 'sha512-xwE/Az9zrjBIphAcBb3F6JVqxf46+CDLwfLMHloNu6KEQCAWi6HcDUbeOfBIptF7tcCzusKFjFw2yuvEpDL9wQ==');
>     stylesheet.setAttribute('crossorigin', 'anonymous');
> 
>     let script = document.createElement('script');
>     script.src = 'https://unpkg.com/leaflet@1.5.1/dist/leaflet.js';
>     script.setAttribute('integrity', 'sha512-GffPMF3RvMeYyc1LWMHtK8EbPv0iNZ8/oTtHPx9/cc2ILxQ+u905qIwdpULaqDkyBKgOaB57QTMg7ztg8Jm2Og==');
>     script.setAttribute('crossorigin', 'anonymous');
>     Promise.all([
>         resolveOnLoad(stylesheet),
>         resolveOnLoad(script),
>     ]).then(cb)
>     document.head.appendChild(stylesheet);
>     document.head.appendChild(script);
> };
> ```
> 
> Or second, you just move to all promises/async:
> 
> ```JavaScript
> const resolveOnLoad = (el) =>
>   new Promise((resolve) => {
>     el.onload = resolve;
>   });
> 
> const loadDependencies = async () => {
>   let stylesheet = document.createElement("link");
>   stylesheet.setAttribute("type", "text/css");
>   stylesheet.setAttribute("rel", "stylesheet");
>   stylesheet.setAttribute(
>     "href",
>     "https://unpkg.com/leaflet@1.5.1/dist/leaflet.css"
>   );
>   stylesheet.setAttribute(
>     "integrity",
>     "sha512-xwE/Az9zrjBIphAcBb3F6JVqxf46+CDLwfLMHloNu6KEQCAWi6HcDUbeOfBIptF7tcCzusKFjFw2yuvEpDL9wQ=="
>   );
>   stylesheet.setAttribute("crossorigin", "anonymous");
> 
>   let script = document.createElement("script");
>   script.src = "https://unpkg.com/leaflet@1.5.1/dist/leaflet.js";
>   script.setAttribute(
>     "integrity",
>     "sha512-GffPMF3RvMeYyc1LWMHtK8EbPv0iNZ8/oTtHPx9/cc2ILxQ+u905qIwdpULaqDkyBKgOaB57QTMg7ztg8Jm2Og=="
>   );
>   script.setAttribute("crossorigin", "anonymous");
>   let loaded = Promise.all([resolveOnLoad(stylesheet), resolveOnLoad(script)]);
>   document.head.appendChild(stylesheet);
>   document.head.appendChild(script);
>   await loaded;
> };
> ```
> 
> In the second case, you'd use it as `loadDependencies().then(()=> console.log("loaded"))`.
> 
> In either case, the principle is the same: if you have a callback based API, write a short wrapper to turn it into a promises API, then use that instead, either with .then or async/await, whichever is more convenient at the time.
