# Publishing a Web Component to npm

I tried this for the first time today with my highly experimental [datasette-table](https://www.npmjs.com/package/datasette-table) Web Component. Here's [the source code](https://github.com/simonw/datasette-table/tree/0.1.0) for version 0.1.0.

I mainly followed the guidelines in Justin Fagnani's guide [How to Publish Web Components to NPM](https://justinfagnani.com/2019/11/01/how-to-publish-web-components-to-npm/).

## Creating the Web Component

See [the source code](https://github.com/simonw/datasette-table/blob/0.1.0/datasette-table.js) to see the full code. It's a single file, `datasette-table.js`, which is structured like this:

```javascript
import {LitElement, html, css} from 'lit';
export class DatasetteTable extends LitElement {
    ...
}
customElements.define("datasette-table", DatasetteTable);
```

## The initial `package.json`

I created my `package.json` using the `npm init` command, which asks questions and generates the file - then I manually edited it to fit Justin's suggestions. It ended up looking like this:

```json
{
  "author": "Simon Willison (https://simonwillison.net/)",
  "name": "datasette-table",
  "version": "0.1.0",
  "type": "module",
  "description": "A Web Component for embedding Datasette tables on a page",
  "main": "datasette-table.js",
  "module": "datasette-table.js",
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1",
  },
  "dependencies": {
    "lit": "^2.0.0"
  },
  "repository": {
    "type": "git",
    "url": "git+https://github.com/simonw/datasette-table.git"
  },
  "license": "Apache-2.0",
  "bugs": {
    "url": "https://github.com/simonw/datasette-table/issues"
  },
  "homepage": "https://github.com/simonw/datasette-table#readme"
}
```
## Using Vite to load the `lit` dependency

My first version of this ran directly in my browser because I imported `lit` directly like so:

```javascript
import {LitElement, html, css} from 'https://cdn.skypack.dev/lit@2.0.2?min';
```
When I switched to `from 'lit'` I had to add a build tool. I decided to try [Vite](https://vitejs.dev/guide/).

I added the following section to `package.json`:

```
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1",
    "dev": "vite",
    "build": "vite build",
    "serve": "vite preview"
  },
  ...
  "devDependencies": {
    "vite": "^2.6.4"
  },
```
Then I ran `npm install` to install Vite and Lit.

Vite needs an `index.html` file, so I created one like so:
```html
<script type="module" src="/datasette-table.js"></script>

<h1>Covid in Greene county, Mississippi</h1>

<datasette-table
  url="https://covid-19.datasettes.com/covid/ny_times_us_counties.json?_size=1000&county=Greene&state=Mississippi"
></datasette-table>

<h1>Power plants</h1>

<datasette-table
  url="https://global-power-plants.datasettes.com/global-power-plants/global-power-plants.json"
></datasette-table>
```

Then I ran `npm run dev` to start the Vite server, then navigated to `http://localhost:3000/` to try out the app.

Vite works by scanning the `index.html` for any JavaScript references, then doing magic on the files that it finds. View source on the running dev server showed that it adds this line to the top of `index.html` when it serves it:

```html
<script type="module" src="/@vite/client"></script>
```
And when it serves the `datasette-table.js` file it rewrites the first import line to look like this:
```script
import {LitElement, html, css} from '/node_modules/.vite/lit.js?v=bf29c8a9';
```

## Publishing to npm

Publishing to npm was almost as easy as running `npm login` - entering my username and password - and then running `npm publish` in that directory. Except this happened:

```
datasette-table % npm publish
...
npm ERR! code E403
npm ERR! 403 403 Forbidden - PUT https://registry.npmjs.org/datasette-table - Forbidden
npm ERR! 403 In most cases, you or one of your dependencies are requesting
npm ERR! 403 a package version that is forbidden by your security policy, or
npm ERR! 403 on a server you do not have access to.
```
That error message was enitrely misleading: the issue was that I hadn't yet clicked the "Verify" link in the email they sent me when I created my account! Once I did that re-running `npm publish` worked... and my package showed up live here:

https://www.npmjs.com/package/datasette-table

## Now that it's on npm unpkg and Skypack work

Now that it's live, the following works as a quick way of trying out the Web Component loaded from [unpkg](https://unpkg.com):
```html
<script type="module" src="https://unpkg.com/datasette-table?module"></script>

<datasette-table
    url="https://global-power-plants.datasettes.com/global-power-plants/global-power-plants.json"
></datasette-table>
```
[Skypack](https://www.skypack.dev/) works the same way:
```html
<script type="module" src="https://cdn.skypack.dev/datasette-table"></script>

<datasette-table
    url="https://global-power-plants.datasettes.com/global-power-plants/global-power-plants.json"
></datasette-table>
```
