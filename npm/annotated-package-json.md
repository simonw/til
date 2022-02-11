# Annotated package.json for idb-keyval

Jake Archibald [pointed to](https://twitter.com/jaffathecake/status/1491771402294370306) his `package.json` for `idb-keyval` as a "modernish example" of NPM packaging on Twitter this morning.

I've been frustrated at my lack of understanding of `package.json` for too long, so I decided to do some research and put together an annotated copy of [that full package.json file](https://github.com/jakearchibald/idb-keyval/blob/fdf795b9b55b417eb6ed22db9721c53877a19569/package.json).

## Relevant links

- The [idb-keyval README](https://github.com/jakearchibald/idb-keyval/blob/main/README.md) has a bunch of extra details about the packaging
- The [NPM package.json docs](https://docs.npmjs.com/cli/v7/configuring-npm/package-json) are a great starting point
- [idb-keyval npm listing](https://www.npmjs.com/package/idb-keyval) (which displays the metadata) 
- [Node.js Packages](https://nodejs.org/api/packages.html) explains the Node.js extensions to `package.json`
- [UNPGK CDN docs](https://unpkg.com/) explaning the `"unpgk"` extension
- [webpack Tree Shaking docs](https://webpack.js.org/guides/tree-shaking/) explaining `"sideEffects"`
- Documentation for [Husky](https://typicode.github.io/husky/) and [lint-staged](https://github.com/okonet/lint-staged)

## Annotated package.json

```javascript
{
  // Name and version are required if you want to publish to npm
  "name": "idb-keyval",
  "version": "6.1.0",

  // Description is listed by npm search and used on websites
  "description": "A super-simple-small keyval store built on top of IndexedDB",

  // The “primary entry point” to your program - if the user installs the package and
  // runs require("package-name") the exports object from this module will be returned
  "main": "./dist/compat.cjs",
```
This is complicated, [see StackOverflow](https://stackoverflow.com/questions/42708484/what-is-the-module-package-json-field-for) - it’s a not-fully-accepted proposal which
is something of a de facto standard. It indicates the version of the package that
can be used as an ES Module. I don’t yet understand the full implications of this.
```javascript
  "module": "./dist/compat.js",

  // The unpkg CDN says “If you omit the file path (i.e. use a “bare” URL), unpkg will
  // serve the file specified by the unpkg field in package.json, or fall back to main.”
  // - this should be what happens when you hit https://unpkg.com/idb-keyval - but I
  // tried that just now and got an error saying “Cannot find "/dist/iife-compat.js"
  // in idb-keyval@6.1.0” so something isn’t quite working right here.
  //
  // The iife-compat.js filename here suggests that this file will use the Immediately
  // invoked function expression pattern, which looks like this:
  //
  // ​​(function () { /* ... */ })();
  //
  // It’s a pattern to avoid polluting the global namespace with variables and functions.
  "unpkg": "./dist/iife-compat.js",

  // This is a Node.js extension. The Node docs say: “The "exports" field provides an
  // alternative to "main" where the package main entry point can be defined while also
  // encapsulating the package, preventing any other entry points besides those defined
  // in "exports". This encapsulation allows module authors to define a public interface
  // for their package.”
  "exports": {
    // I don’t yet understand why this is a nested object
    ".": {
      "module": "./dist/index.js",
      "import": "./dist/index.js",
      "default": "./dist/index.cjs"
    },
    "./dist/*": "./dist/*",
    "./package.json": "./package.json"
  },

  // These files are included when the package is installed as a dependency
  "files": [
    "dist/**"
  ],

  // Another node.js extension: https://nodejs.org/api/packages.html#type says: Files
  // ending with .js are loaded as ES modules when the nearest parent package.json file
  // contains a top-level field "type" with a value of "module".
  "type": "module",

  // TypeScript extension indicating the location of type information for this module
  "types": "./dist/index.d.ts",

  // The webpack Tree Shaking docs say “The new webpack 4 release expands on this capability
  // with a way to provide hints to the compiler via the "sideEffects" package.json property
  // to denote which files in your project are "pure" and therefore safe to prune if unused”
  "sideEffects": false,

  // Running “npm run build” or “npm run dev” or “npm run prepack” runs these:
  "scripts": {
    "build": "rollup -c && node lib/size-report.js",
    "dev": "rollup -cw & serve",
    "prepack": "npm run build"
  },

  // A bunch more metadata used when the package is shown on npm
  "repository": {
    "type": "git",
    "url": "git+https://github.com/jakearchibald/idb-keyval.git"
  },
  "keywords": [
    "idb",
    "indexeddb",
    "store",
    "keyval",
    "localstorage",
    "storage",
    "promise"
  ],
  "author": "Jake Archibald",
  "license": "Apache-2.0",
  "bugs": {
    "url": "https://github.com/jakearchibald/idb-keyval/issues"
  },
  "homepage": "https://github.com/jakearchibald/idb-keyval#readme",

  // These are the dependencies that get installed when you run “npm install” from the
  // root of the package - but they are not installed when an end-user uses
  // “npm install name-of-package”
  "devDependencies": {
    "@babel/core": "^7.16.0",
    "@babel/plugin-external-helpers": "^7.16.0",
    "@babel/plugin-transform-runtime": "^7.16.4",
    "@babel/preset-env": "^7.16.4",
    "@babel/runtime": "^7.16.3",
    "@rollup/plugin-babel": "^5.3.0",
    "@rollup/plugin-commonjs": "^21.0.1",
    "@rollup/plugin-node-resolve": "^13.0.6",
    "@types/chai": "^4.2.22",
    "@types/mocha": "^9.0.0",
    "chai": "^4.3.4",
    "conditional-type-checks": "^1.0.5",
    "del": "^6.0.0",
    "filesize": "^8.0.6",
    "glob": "^7.2.0",
    "husky": "^7.0.4",
    "lint-staged": "^12.1.2",
    "mocha": "^9.1.3",
    "prettier": "^2.5.0",
    "rollup": "^2.60.2",
    "rollup-plugin-terser": "^7.0.2",
    "serve": "^13.0.2",
    "typescript": "^4.3.5"
  },

  // Husky is a tool for managing git pre-commit hooks
  "husky": {
    "hooks": {
      "pre-commit": "lint-staged"
    }
  },

  // lint-staged runs linters against staged files - here it is called by Husky
  "lint-staged": {
    "*.{js,css,md,ts,html}": "prettier --write"
  },

  // This package has only one non-dev dependency
  "dependencies": {
    // safari-14-idb-fix provides a idbReady().then(() => … function for waiting
    // until IDB is ready to be accessed in Safari, as a workaround for a bug that
    // existed prior to Safari 14.7 
    "safari-14-idb-fix": "^3.0.0"
  }
}
```
