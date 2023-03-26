# Using jq in an Observable notebook

I use the `jq` language quite a lot these days, mainly because I can get ChatGPT to write little JSON transformation programs for me very quickly.

I just figured out how to run `jq` in an Observable notebook.

The key is the [jq-web](https://www.npmjs.com/package/jq-web) npm package, which provides an Emscripten-compiled version of `jq` itself.

You can load that in an Observable notebook with this cell:

```javascript
jq = require("jq-web")
```

Now you can use the `jq.json(data, jqScript)` function to run a conversion against some data.

Here's a simple example from the `jq-web` documentation:

```javascript
jq.json({
  a: {
    big: {
      json: [
        'full',
        'of',
        'important',
        'things'
      ]
    }
  }
}, '.a.big.json | ["empty", .[1], "useless", .[3]] | join(" ")')
```

I tend to want to run recipes against data from an Observable textarea - so I add a cell like this:

```javascript
viewof input = Inputs.textarea({
  placeholder: "Paste JSON here"
})
```
Then I can run a `jq` recipe like it and assign the result to a variable:
```javascript
output = jq.json(JSON.parse(input), '.my.jq.program.here');
```
I can display that output like so:
```javascript
html`<h2>Output:</h2>
<textarea style="width: 80%; height: 20em">${JSON.stringify(
  output,
  null,
  2
)}</textarea>
```
Here's [an example of a notebook I created](https://observablehq.com/@simonw/chatgpt-json-transcript-to-markdown) using `jq-web`.
