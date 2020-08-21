# Working around the size limit for nodeValue in the DOM

TIL that `nodeValue` in the DOM has a size limit!

I had a table cell element containing HTML-escaped JSON and I was doing this:

```javascript
data = JSON.parse(td.firstChild.nodeValue); 
```

This was breaking on larger JSON strings. It turns out that beyond a certain length limit browsers break up large chunks of text into multiple DOM text nodes.

The solution, [via Stackoverflow](https://stackoverflow.com/questions/4411229/size-limit-to-javascript-node-nodevalue-field), was this:

```javascript
const getFullNodeText = (el) => {
    // https://stackoverflow.com/a/4412151
    if (!el) {
        return '';
    }
    if (typeof(el.textContent) != "undefined") {
        return el.textContent;
    }
    return el.firstChild.nodeValue;
};
```
More details in [this issue](https://github.com/simonw/datasette-leaflet-geojson/issues/12).
