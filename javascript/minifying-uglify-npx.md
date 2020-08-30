# Minifying JavaScript with npx uglify-js

While [upgrading CodeMirror](https://github.com/simonw/datasette/issues/948) in Datasette I figured out how to minify JavaScript using `uglify-js` on the command line without first installing any teels, using [npx](https://www.npmjs.com/package/npx) (which downloads and executes a CLI tool while skipping the install step):

    npx uglify-js codemirror-5.57.0.js -o codemirror-5.57.0.min.js

One problem: this stripped out the LICENSE comment at the top of the file.

Turns out you can tell `uglify-js` not to strip comments that match a specific regular expression.

So I edited the CodeMirror file to use a single `/* ... */` comment at the top of the file (instead of multiple `//` lines) and ran Uglify like this:

    npx uglify-js codemirror-5.57.0.js -o codemirror-5.57.0.min.js --comments '/LICENSE/'

For CSS I used `clean-css-cli`:

    npx clean-css-cli codemirror-5.57.0.css -o codemirror-5.57.0.min.css
