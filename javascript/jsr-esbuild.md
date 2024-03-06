# Using packages from JSR with esbuild

[JSR](https://jsr.io/) is a brand new package repository for "modern JavaScript and TypeScript", [launched on March 1st](https://deno.com/blog/jsr_open_beta) by the Deno team as a new alternative to [npm](https://www.npmjs.com/)

My JavaScript ecosystem fluency isn't great, so it took me a bit of work to figure out how to use packages from JSR in my browser.

## Installing yassify with npx jsr add

[@kwhinnery/yassify](https://jsr.io/@kwhinnery/yassify) is the demo package created as part of that [introductory blog post](https://deno.com/blog/jsr_open_beta#publishing-to-jsr). The code itself is a tiny snippet of TypeScript:

```typescript
/**
 * Yassify a string of text by appending emoji
 *
 * @param str The string of text to yassify.
 * @returns a string of text with emoji appended
 */
export function yassify(str: string): string {
  return `${str} 💅✨👑`;
}
```
It's published to JSR [here](https://jsr.io/@kwhinnery/yassify). That page includes `npm` instructions for using it that look like this:

> ```bash
> npx jsr add @kwhinnery/yassify
> ```
> ```javascript
> import * as mod from "@kwhinnery/yassify";
> ```
For someone with limited JavaScript ecosystem fluency like myself, that is **not enough information**! I want to run this code in a browser.

Part of the problem is that there are a bewildering array of build tool options. I wanted the thing with the least number of steps - eventually I found  this pattern using `esbuild` that seems to work.

I already had `npm` and `npx` installed.

First I created myself a directory for my experiment:

```bash
mkdir /tmp/site
cd /tmp/site
```
I used the `npx jsr add` command from the JSR documentation:
```bash
npx jsr add @kwhinnery/yassify
```
Output:
```
Setting up .npmrc...ok
Installing @kwhinnery/yassify...
$ npm install @kwhinnery/yassify@npm:@jsr/kwhinnery__yassify

added 1 package in 711ms

Completed in 824ms
```
This created a bunch of files. Running `find .` reveals the following:
```
./node_modules
./node_modules/@kwhinnery
./node_modules/@kwhinnery/yassify
./node_modules/@kwhinnery/yassify/mod.d.ts
./node_modules/@kwhinnery/yassify/package.json
./node_modules/@kwhinnery/yassify/mod.js
./node_modules/.package-lock.json
./.npmrc
./package-lock.json
./package.json
```
The `package.json` file contains:
```json
{
  "dependencies": {
    "@kwhinnery/yassify": "npm:@jsr/kwhinnery__yassify@^1.0.1"
  }
}
```
`.npmrc` has the following, which is described in the JSR documentation about [npm compatibility](https://jsr.io/docs/npm-compatibility#advanced-setup):
```
@jsr:registry=https://npm.jsr.io
```
The actual `yassify` code lives in that `./node_modules/@kwhinnery/yassify/mod.js` file.

OK - so we've run a command and got ourselves a `node_modules` directory with the `yassify` code in it. How do we use that in a browser?

## Building an index.js file with esbuild

Here's a tiny JavaScript file that uses `yassify`:

```javascript
import { yassify } from "@kwhinnery/yassify";
const h1 = document.querySelector("h1");
h1.innerText = yassify(h1.innerText);
```
And the incantation to have `esbuild` resolve that import and bundle all of the code together into a single file:
```bash
npx esbuild index.js --bundle
```
That outputs directly to standard out:
```javascript
(() => {
  // node_modules/@kwhinnery/yassify/mod.js
  function yassify(str) {
    return `${str} \u{1F485}\u2728\u{1F451}\u{1F984}`;
  }

  // index.js
  var h1 = document.querySelector("h1");
  h1.innerText = yassify(h1.innerText);
})();
```
Or you can add `--outfile=bundle.js` to write it to a file:
```bash
npx esbuild index.js --bundle --outfile=bundle.js
```
Now here's an `index.html` file that makes use of this bundle:
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Yassify</title>
</head>
<body>
<h1>Yassify</h1>
<script src="bundle.js"></script>
</body>
</html>
```
And that works! You can open `index.html` directly in a browser and it loads and executes the bundled code.

## Trying that with my own package - and failing to get it to work

I have just one package on NPM at the moment: [datasette-table](https://www.npmjs.com/package/datasette-table), an experimental Web Component for rendering tables from [Datasette](https://datasette.io/) on a page.

The source code for that is in [simonw/datasette-table](https://github.com/simonw/datasette-table) on GitHub.

I followed the [JSR intro post](https://deno.com/blog/jsr_open_beta#publishing-to-jsr) and published it to GitHub.

I signed into JSR using my GitHub account and created a scope called `@datasette` - all packages on JSR are published within a scope.

I added a `jsr.json` file te the root of the repository:
```json
{
  "name": "@datasette/table",
  "version": "0.1.0",
  "exports": "./datasette-table.js"
}
```
Then I ran this command:
```bash
npx jsr publish
```
This opened my browser to authenticate and pushed the package to JSR: [jsr.io/@datasette/table](https://jsr.io/@datasette/table). Pretty smooth!

Let's try using that package via the `esbuild` method described above:

```bash
mkdir /tmp/datasette-demo
cd /tmp/datasette-demo
npx jsr add @datasette/table
echo 'import * as mod from "jsr:@datasette/table";' > index.js
npx esbuild index.js --bundle --outfile=bundle.js
```
And I got this error:
```
✘ [ERROR] Could not resolve "npm:lit@^2.2.7"

    node_modules/@datasette/table/datasette-table.js:1:36:
      1 │ import {LitElement, html, css} from 'npm:lit@^2.2.7';
        ╵                                     ~~~~~~~~~~~~~~~~

  You can mark the path "npm:lit@^2.2.7" as external to exclude it from the bundle, which will
  remove this error and leave the unresolved path in the bundle.

1 error
```
`lit` is the only dependency of my component. I checked `node_modules` and it had all of the `lit` files in it, so they had been installed correctly - but something wasn't working.

I tried adding `--external:npm:lit` to the `esbuild` command, but that didn't help.

This failed too:
```bash
npx esbuild index.js --bundle --outfile=bundle.js --external:lit
```

So I started from scratch:
```bash
mkdir /tmp/datasette-demo2
cd /tmp/datasette-demo2
```
This time I used a mechanism I found in the [advanced setup](https://jsr.io/docs/npm-compatibility#advanced-setup) section of the npm compatibility documentation:
```bash
echo '@jsr:registry=https://npm.jsr.io' > .npmrc
npm install @jsr/datasette__table
```
`find .` showed me that it had installed the Lit packages, but I also noticed this:
```bash
find . | grep datasette
```
```
./node_modules/@jsr/datasette__table
./node_modules/@jsr/datasette__table/datasette-table.js
./node_modules/@jsr/datasette__table/package.json
```
So the JSR `@datasette/table` package is in a slightly different shape.

Now I tried the `esbuild` command again:
```bash
echo 'import * as mod from "@jsr/datasette__table";' > index.js
npx esbuild index.js --bundle --outfile=bundle.js
```
But I got the same error again:
```
✘ [ERROR] Could not resolve "npm:lit@^2.2.7"

    node_modules/@jsr/datasette__table/datasette-table.js:1:36:
      1 │ import {LitElement, html, css} from 'npm:lit@^2.2.7';
        ╵                                     ~~~~~~~~~~~~~~~~

  You can mark the path "npm:lit@^2.2.7" as external to exclude it from the bundle, which will
  remove this error and leave the unresolved path in the bundle.

1 error
```
And at this point... I gave up. I'm still seeking a solution - progress so far:

- I asked about this on the JSR Discord and they suggested it might be a bug, so I filed [Something rewrote my import to from 'npm:lit@^2.2.7'; and now I can't build with esbuild](https://github.com/jsr-io/jsr/issues/139)
- I started a [discussion on Mastodon](https://fedi.simonwillison.net/@simon/112027336520936261) and Bill Mill found [a workaround for the problem](https://notes.billmill.org/programming/javascript/build_tools/using_esbuild_to_package_a_deno_package_for_the_browser.html) using the [esbuild_deno_loader](https://github.com/lucacasonato/esbuild_deno_loader) plugin and Deno to build the bundle.

## And now it works!

Update 5th March 2024: the JSR team [shipped this fix](https://github.com/jsr-io/jsr/pull/172) and now the following recipe works exactly as I want it to:

```bash
mkdir /tmp/datasette-demo3
cd /tmp/datasette-demo3
echo '@jsr:registry=https://npm.jsr.io' > .npmrc
npm install @jsr/datasette__table
echo 'import * as mod from "@jsr/datasette__table";' > index.js
npx esbuild index.js --bundle --outfile=bundle.js
echo '<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Datasette News</title>
</head>
<body>
  <datasette-table
  url="https://datasette.io/content/news.json"
></datasette-table>
<script src="bundle.js"></script>
</body>
</html>' > index.html
```
Now open `index.html` in a browser and:

![Screenshot of a page with a table of recent news articles on it, rendered by my Web Component](https://github.com/simonw/til/assets/9599/fb916e87-a92f-4b55-99fc-63372669a74e)
