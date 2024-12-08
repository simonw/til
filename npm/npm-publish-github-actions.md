# Publishing a simple client-side JavaScript package to npm with GitHub Actions

Here's what I learned about publishing a single file JavaScript package to NPM for my [Prompts.js](https://simonwillison.net/2024/Dec/7/prompts-js/) project.

The code is in [simonw/prompts-js](https://github.com/simonw/prompts-js) on GitHub. The NPM package is [prompts-js](https://www.npmjs.com/package/prompts-js).

## A simple single file client-side package

For this project, I wanted to create an old-fashioned JavaScript file that you could include in a web page using a `<script>` tag. No TypeScript, no React JSK, no additional dependencies, no build step.

I also wanted to ship it to NPM, mainly so it would be magically available from various CDNs.

I think I've boiled that down to about as simple as I can get. Here's the `package.json` file:

```json
{
  "name": "prompts-js",
  "version": "0.0.4",
  "description": "async alternatives to browser alert() and prompt() and confirm()",
  "main": "index.js",
  "homepage": "https://github.com/simonw/prompts-js",
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "author": "Simon Willison",
  "license": "Apache-2.0",
  "repository": {
    "type": "git",
    "url": "git+https://github.com/simonw/prompts-js.git"
  },
  "keywords": [
    "alert",
    "prompt",
    "confirm",
    "async",
    "promise",
    "dialog"
  ],
  "files": [
    "index.js",
    "README.md",
    "LICENSE"
  ]
}
```
That "scripts.test" block probably isn't necessary. The `keywords` are used when you deploy to NPM, and the `files` block tells NPM which files to include in the package.

The `"repository"` block is used by NPM's [provenance statements](https://docs.npmjs.com/generating-provenance-statements). Don't worry too much about these - they're only needed if you use the `npm publish --provenance` option later on.

Really the three most important keys here are `"name"`, which needs to be a unique name on NPM, `"version"` and that `"main"` key. I set `"main"` to `index.js`.

All that's needed now is that `index.js` file - and optionally the `README.md` and `LICENSE` files if we want to include them in the package. The `README.md` ends up displayed on the NPM listing page so it's worth including.

Here's my [index.js](https://github.com/simonw/prompts-js/blob/main/index.js) file. It starts and ends like this (an [IFFE](https://developer.mozilla.org/en-US/docs/Glossary/IIFE)):

```javascript
const Prompts = (function () {
  // ...
  return { alert, confirm, prompt };
})();
```

## Publishing to NPM

With these pieces in place, running `npm publish` in the root of the project will publish the package to NPM - after first asking you to sign into your NPM account.

## Automating this with GitHub Actions

I use GitHub Actions that trigger on any release to publish all of my Python projects to PyPI. I wanted to do the same for this JavaScript project.

I found [this example](https://docs.github.com/en/actions/use-cases-and-examples/publishing-packages/publishing-nodejs-packages#publishing-packages-to-the-npm-registry) in the GitHub documentation which gave me most of what I needed. This is in [.github/workflows/publish.yml](https://github.com/simonw/prompts-js/blob/main/.github/workflows/publish.yml):

```yaml
name: Publish Package to npmjs
on:
  release:
    types: [published]
jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20.x'
          registry-url: 'https://registry.npmjs.org'
      - run: npm publish --provenance --access public
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```
There's that `--provenance` option which only works if you have the `repository` block set up in your `package.json`.

This needs a secret called `NPM_TOKEN` to be set up in the GitHub repository settings.

It took me a few tries to get this right. It needs to be a token created on the NPM website using the Access Tokens menu item, then Generate New Token -> Classic Token. As far as I can tell the new "Granular Access Token" format doesn't work for this as it won't allow you to create a token that never expires, and I never want to have to remember to update the secret in the future.

An "Automation" token should do the trick here - it bypasses 2-factor authentication when publishing.

Set that in GitHub Actions as a secret called `NPM_TOKEN` and now you can publish a new version of your package to NPM by doing the following:

1. Update the version number in `package.json`
2. Create a new release on GitHub with a tag that matches the version number
