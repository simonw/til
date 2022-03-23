# Using the GitHub Actions cache with npx and no package.json

Some of my repositories have GitHub Actions workflows that execute commands using `npx`, for example my [graphql-scraper](https://github.com/simonw/graphql-scraper) repo using `npx` to [install and run](https://github.com/simonw/help-scraper/blob/54ef9b1fa579dc2d3f68055ffdac9996fd6dae9c/.github/workflows/scrape.yml#L76-L80) the `get-graphql-schema` tool:

    npx get-graphql-schema https://api.fly.io/graphql > flyctl/fly.graphql

This was downloading the package from npm every time the action ran. This feels rude! I wanted to use the [actions/cache](https://github.com/actions/cache) mechanism to cache the download in between runs.

One problem: the documentation for that action assumes that projects are using a `package.json` file which can be used as part of the cache key. But my projects don't have one of those files, they just want to use `npx` utilities as part of their workflows.

Here's the pattern I came up with to configure the cache:

```yaml
    - uses: actions/setup-node@v2
      with:
        node-version: '14'
        cache: 'npm'
        cache-dependency-path: '**/.github/workflows/*.yml'
```
This is using [actions/setup-node](https://github.com/actions/setup-node) which itself can setup the cache. I'm telling it that I want to cache `npm` assets - which usually requires a `package.json` file. But it turns out you can set a custom `cache-dependency-path` - and in this case I'm bundling together ALL of my GitHub Actions wokflow YAML files as that cache key.

I could be more specific and indicate the exact filename of the workflow in question, but I wanted something I could copy-and-paste between projects easily.

With this in place, `npx ...` lines now get to reuse the previously downloaded version of the tool. The entire cache is invalidated any time any content of any of the workflow YAML files changes, which I think is fine.
