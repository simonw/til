# Running self-hosted QuickJS in a browser

I want to try using [QuickJS](https://bellard.org/quickjs/) compiled to WebAssembly in a browser as a way of executing untrusted user-provided JavaScript in a sandbox.

My plan is to host it locally, not load it from a CDN. I also want to be able to write most of my regular JavaScript without using build tooling - so I want a QuickJS bundle that I can load using a good old-fashioned `<script>` tag.

This is always harder than I think it will be. In this case the [quickjs-emscripten README](https://github.com/justjake/quickjs-emscripten/blob/main/README.md) starts with the following:

> ```javascript
> import { getQuickJS } from "quickjs-emscripten"
> ...

That's not enough information for someone like me to get started!

Here's the recipe I figured out that got me to where I wanted to be.

## Install and build quickjs-emscripten using npm and webpack

I do not want to have to run `npm` and `webpack` as part of my day-to-day project work, but I'm happy to run them once to get me a bundle that I can use.

I started by installing `quickjs-emscripten` and `webpack` in a temporary directory:

```bash
cd /tmp
mkdir qjs
cd qjs
npm install quickjs-emscripten webpack webpack-cli
```
Tools like `webpack` like to run against an "entry point" - a script that depends on other libraries that it can bundle and minify and tree shake and suchlike.

I just want something I can load into a web page as a script, so I created the simplest entry point I could that appeared to work. I saved this in `src/quickjs.js`:

```javascript
import { getQuickJS } from "quickjs-emscripten";
window.getQuickJS = getQuickJS;
```
Then I configured webpack (with the help of Claude 3 Opus) by creating this `webpack.config.js` file:

```javascript
const path = require('path');

module.exports = {
    entry: './src/quickjs.js',
    output: {
        filename: 'quickjs.js',
        path: path.resolve(__dirname, 'dist'),
    },
    mode: 'production'
};
```
I started with `development` as the mode, but `production` produces a smaller set of files.

Then I ran webpack:

```bash
npx webpack
```
Heres the partial output from that command:
```
asset 7cf7ced34f0a1ece31b4.wasm 505 KiB [emitted] [immutable] [from: ../node_modules/@jitl/quickjs-wasmfile-release-sync/dist/emscripten-module.wasm] [big]
asset 915.quickjs.js 24.9 KiB [emitted] [minimized] (id hint: vendors)
asset 338.quickjs.js 11.9 KiB [emitted] [minimized]
asset 878.quickjs.js 5.49 KiB [emitted] [minimized]
asset quickjs.js 3.65 KiB [emitted] [minimized] (name: main)
asset 864.quickjs.js 2.01 KiB [emitted] [minimized]
asset 966.quickjs.js 242 bytes [emitted] [minimized]
orphan modules 329 KiB (javascript) 8.88 MiB (asset) [orphan] 17 modules
runtime modules 6.67 KiB 9 modules
cacheable modules 51.6 KiB (javascript) 505 KiB (asset)
...
webpack 5.91.0 compiled with 1 warning in 403 ms
```
My `dist/` directory now contains the following:
```
338.quickjs.js - 12K
7cf7ced34f0a1ece31b4.wasm - 505K
864.quickjs.js - 2.0K
878.quickjs.js - 5.5K
915.quickjs.js - 25K
966.quickjs.js - 242B
quickjs.js - 3.7K
```
## Using the bundle in a web page

I created a simple HTML file to test the bundle. I saved this in `index.html`:

```html
<script src="dist/quickjs.js"></script>
```
This needs to be served by a real web server - opening the file directly in a browser won't work because of CORS restrictions.

So I ran a server using Python like this:
```bash
python -m http.server 8052
```
And loaded up http://localhost:8052/ in a browser.

The network panel showed me that this loaded just `quickjs.js`, a 3.74KB file.

This showed a blank page, as expected. I opened up the developer console and ran the following:
```javascript
QuickJS = await getQuickJS()
```
This triggered a short flurry of network requests, for the following files:

- 338.quickjs.js
- 878.quickjs.js
- 915.quickjs.js
- 966.quickjs.js
- 7cf7ced34f0a1ece31b4.wasm

Most of the weight was that last WASM file. The page had now loaded 564KB total.

And... I can now use QuickJS! The following worked:

```javascript
vm = QuickJS.newContext()
result = vm.evalCode(`"Hello " + 333 ** 2`);
if (result.error) {
  console.log("Execution failed:", vm.dump(result.error))
  result.error.dispose()
} else {
  console.log("Success:", vm.dump(result.value))
  result.value.dispose()
}
```
It logged out `Success: Hello 110889` to the console.

## The dist/ directory survives relocation

I was worried that webpack might have built me a bundle that requires hosting in `/dist/` - but thankfully that wasn't the case.

I tried renaming `dist/` to different things and making it part of a nested folder structure. Provided I loaded that initial `/path/to/quickjs.js` file, the rest of the files were loaded relative to that.

## Grab it from a gist

For anyone who wants a usable copy of `quickjs-emscripten` without having to run `npm` and `webpack` themselves, I created a Gist containing the files described above:

https://gist.github.com/simonw/36506994222a56d1556b3452ca663dbe

You can download the files from there, or grab them with this command:
```bash
git clone https://gist.github.com/simonw/36506994222a56d1556b3452ca663dbe
```
