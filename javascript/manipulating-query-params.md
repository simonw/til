# Manipulating query strings with URLSearchParams

The `URLSearchParams` class, in [every modern browser](https://caniuse.com/?search=URLSearchParams) since IE 11, provides a sensible API for manipulating query string parameters in JavaScript. I first used it to build Datasette's column action menu, see [table.js](https://github.com/simonw/datasette/blob/0.50a0/datasette/static/table.js) and [issue 981](https://github.com/simonw/datasette/issues/981).

Here's how it handles multiple parameters with the same name, e.g. `?foo=bar&foo=baz`:

```javascript
var params = new URLSearchParams('?foo=bar&foo=baz')
console.log(params.get("foo"))
// Outputs "bar"
console.log(params.getAll("foo"))
// Outputs ["bar", "baz"]
console.log(params.get("foo2"))
// Outputs null
console.log(params.getAll("foo2"))
// Outputs []
```

It can also be used to add, remove and append values - then turned back into a query string using `params.toString()`:

```javascript
var params = new URLSearchParams('?foo=bar&foo=baz')
params.append("foo", "another");
params.toString()
// "foo=bar&foo=baz&foo=another"
params.set("foo", "over-written")
// "foo=over-written"
params.delete("foo")
params.toString()
// ""
```
To construct a parameters object from the query string used on the current page, do this:
```javascript
var params = new URLSearchParams(location.search);
```
It doesn't matter if the string passed to `new URLSearchParams()` has a leading question mark or not - the result is the same.
