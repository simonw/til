# Serving a JavaScript project built using Vite from GitHub Pages

I figured out how to serve a JavaScript project built using [Vite](https://vitejs.dev/) using GitHub Pages and a custom build script that runs using GitHub Actions.

## Creating a Vite project

I started with a "vanilla" JavaScript Vite project. I used the following command to create it:

```bash
npx create-vite@latest hmb-map --template vanilla
```
My project is called `hmb-map`.

This creates a `hmb-map/` directory containing the following files:

```
.gitignore
counter.js
index.html
javascript.svg
main.js
package.json
public/vite.svg
style.css
```

Now `cd hmb-map` and run this:

```bash
npm install
```
That installs Vite and a few other dependencies into `node_modules/`.

Start the Vite development server like so:
```bash
npm run dev
```
This spits out a URL like `http://localhost:5173/` - that page uses Vite's live reloading mechanism, so any changes you make to the code should be instantly reflected in your browser, without having to reload the page.

You can `npm install x` packages there, then use `import x from 'x'` in your `main.js` code and Vite will automatically bundle them into your project.

## Deploying that project to GitHub Pages

The directory structure created by `npx create-vite` has almost everything you need to push it to GitHub. But we want the build process to run on every push and deploy a built version of the code to GitHub Pages.

To do that, add a `.github/workflows/deploy.yml` file containing the following:

```yaml
name: Deploy

on:
  push:
    branches:
      - main

jobs:
  build:
    name: Build
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v3
      - name: Setup Node
        uses: actions/setup-node@v3
      - name: Install dependencies
        run: npm install
      - name: Configure vite
        run: |
          echo 'export default {
            base: "/${{ github.event.repository.name }}/"
          }' > vite.config.js
      - name: Build project
        run: npm run build
      - name: Upload Pages artifact
        uses: actions/upload-pages-artifact@v2
        with:
          path: dist
  deploy:
    needs: build
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v2
```
There are a few things going on here.

The `build` job mainly runs `npm run build`, which creates a `dist/` folder suitable for deployment.

I had to make one change here. GitHub Pages defaults to deploying to `username.github.io/repo-name/` - but Vite expects the application to be running at the root of a site, not inside a folder.

The fix for that is to configure Vite to use a base path. My Actions workflow does that like so:

```bash
echo 'export default {
  base: "/${{ github.event.repository.name }}/"
}' > vite.config.js
```
This uses GitHub Actions expression syntax to get the name of the repository, then writes a `vite.config.js` file containing the following:

```js
export default {
  base: "/hmb-map/"
}
```
This causes the `npm run build` step to bundle for code hosted at `/hmb-map/` instead of `/`.

At the end of the build job the [actions/upload-pages-artifact](https://github.com/actions/upload-artifact) action is used to upload the `dist/` folder produced by Vite as an artifact.

This artifact is then deployed by the [actions/deploy-pages](https://github.com/actions/deploy-pages) action at the end of the deploy job.

## Enabling GitHub Pages via GitHub Actions

There was one remaining configuration step: I had to visit https://github.com/simonw/hmb-map/settings/pages and set GitHub Actions as the source for my Pages builds:

![Screenshot of the Pages settings showing the GitHub Actions source selection menu](https://github.com/simonw/til/assets/9599/0bd1e59f-5571-4be3-b843-ce80704e9c01)

## Adding additional files to public/

For my application I needed a file called `hmb.pmtiles` to be hosted in the root directory of the site.

Vite has a [public directory](https://vitejs.dev/guide/assets.html#the-public-directory) concept for this. Any files you add to the `public/` directory will be served from the root by `npm run dev` and will be bundled into the root of the built asset as well.

## The final result

You can see the resulting repo at https://github.com/simonw/hmb-map/ - the GitHub Pages site it deploys is at https://simonw.github.io/hmb-map/
