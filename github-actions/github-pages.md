# Building and deploying a custom site using GitHub Actions and GitHub Pages

I figured out a minimal pattern for building a completely custom website using GitHub Actions and deploying the result to GitHub Pages.

First you need to enable GitHub Pages for the repository. Navigate to Settings -> Pages (or visit `$repo/settings/pages`) and set the build source to "GitHub Actions".

Here's my minimal YAML recipe - save this in a `.github/workflows/publish.yml` file:

```yaml
name: Publish site

on:
  push:
  workflow_dispatch:

permissions:
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Build the site
      run: |
        mkdir _site
        echo '<h1>Hello, world!</h1>' > _site/index.html
    - name: Upload artifact
      uses: actions/upload-pages-artifact@v3
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```
Anything that goes in that `_site/` directory will be published to the GitHub Pages site.

The `permissions` are required - the `pages: write` one enables writes to pages and for some reason the `id-token: write` one is needed by the [actions/deploy-pages](https://github.com/actions/deploy-pages) action.

The default URL for the site will be `https://$GITHUB_USERNAME.github.io/$REPO_NAME/`. You can set this to [custom domain](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site) if you want.

[github.com/simonw/minimal-github-pages-from-actions](https://github.com/simonw/minimal-github-pages-from-actions/) is an example repository that uses this exact YAML configuration. It publishes a site to [https://simonw.github.io/minimal-github-pages-from-actions/](https://simonw.github.io/minimal-github-pages-from-actions/).

## Next steps

You can combine this trick with scheduled workflows and [Git scraping](https://simonwillison.net/2020/Oct/9/git-scraping/) to create all sorts of interesting and useful things.

I'm using it to publish [an Atom feed](https://simonw.github.io/recent-california-brown-pelicans/atom.xml) of recent California Brown Pelicans sightings on [iNaturalist](https://www.inaturalist.org/) in my [simonw/recent-california-brown-pelicans](https://github.com/simonw/recent-california-brown-pelicans) repository.

I also use it to publish my [tools.simonwillison.net](https://tools.simonwillison.net/) site with a custom [colophon](https://tools.simonwillison.net/colophon) page - see [this post](https://simonwillison.net/2025/Mar/11/using-llms-for-code/#a-detailed-example) for details.
