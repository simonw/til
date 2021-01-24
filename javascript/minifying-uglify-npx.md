# Minifying JavaScript with npx uglify-js

While [upgrading CodeMirror](https://github.com/simonw/datasette/issues/948) in Datasette I figured out how to minify JavaScript using `uglify-js` on the command line without first installing any teels, using [npx](https://www.npmjs.com/package/npx) (which downloads and executes a CLI tool while skipping the install step):

    npx uglify-js codemirror-5.57.0.js -o codemirror-5.57.0.min.js

One problem: this stripped out the LICENSE comment at the top of the file.

Turns out you can tell `uglify-js` not to strip comments that match a specific regular expression.

So I edited the CodeMirror file to use a single `/* ... */` comment at the top of the file (instead of multiple `//` lines) and ran Uglify like this:

    npx uglify-js codemirror-5.57.0.js -o codemirror-5.57.0.min.js --comments '/LICENSE/'

For CSS I used `clean-css-cli`:

    npx clean-css-cli codemirror-5.57.0.css -o codemirror-5.57.0.min.css

## Using tercer instead

It turns out `uglify-js` doesn't support ES6 at all. You can use [tercer](https://github.com/terser/terser) instead:

    npx terser codemirror-5.57.0.js -o codemirror-5.57.0.min.js --comments '/LICENSE/'

Discovered in [datasette-edit-tables #16](https://github.com/simonw/datasette-edit-tables/issues/16).

## Trying out Uglify interactively

[UglifyJS 3: Online JavaScript minifier](https://skalman.github.io/UglifyJS-online/) is a useful way to try out Ugllify since it shows you the results as you type, which makes it easy to spot tiny changes you can make that result in a shorter minified output.
