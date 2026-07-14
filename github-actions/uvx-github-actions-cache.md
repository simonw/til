# Using uvx in GitHub Actions in a cache-friendly way

I often find myself wanting to run a quick Python tool inside of GitHub Actions using `uvx name-of-tool` - but I don't want that to result in a network request to PyPI every time the workflow runs. I want the tool to be fetched the first time and then reused from the GitHub Actions cache for subsequent runs.

I've tried unsuccessfully to find patterns I like for this in the past, especially given the standard pattern in GitHub Actions of using the hashed contents of a file - often `pyproject.toml` or `requirements.txt` - as a key for the cache.

This is usually a good pattern, but for simple scripts I don't want to have to maintain an additional file just to get the cache to work correctly.

Today (with the [help of GPT-5.6 Sol](https://chatgpt.com/share/6a5586a8-68d0-83e8-a78a-f01ec2472c58)) I finally found a pattern I like. 

My goal was to be able to drop `uvx name-of-tool` into a GitHub Actions workflow anywhere I like, while still trusting that the tool would be cached between builds - and could be cache-invalidated if I needed to.

The key turned out to be the [UV_EXCLUDE_NEWER](https://docs.astral.sh/uv/reference/environment/#uv_exclude_newer) environment variable. This works the same as `uvx --exclude-newer DATE`, allowing you to tell `uv` to install the most recent package as-of a specific date.

That date can then also be used as part of the cache key for GitHub Actions! This means you can set the date in the script once and get a repeatable set of installed versions for all of the tools. Then any time you want to bust the cache you can increment the date in that one palce:

```yaml
name: Run tools

on:
  workflow_dispatch:

env:
  # Bump this date to allow newer package releases and a fresh cache:
  UV_EXCLUDE_NEWER: "2026-07-12"

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Install uv and restore cache
        id: setup-uv
        uses: astral-sh/setup-uv@11f9893b081a58869d3b5fccaea48c9e9e46f990 # v8.3.2
        with:
          enable-cache: true
          cache-dependency-glob: ""
          cache-suffix: "tools-${{ env.UV_EXCLUDE_NEWER }}"
          prune-cache: false
    
      - name: Require cache-only uv on cache hits
        if: steps.setup-uv.outputs.cache-hit == 'true'
        run: echo "UV_OFFLINE=1" >> "$GITHUB_ENV"
    
      - name: Run sqlite-utils
        run: uvx sqlite-utils --version
    
      - name: Run datasette
        run: uvx --pre datasette --version
    
      - name: Run LLM
        run: uvx llm --version
```

[astral-sh/setup-uv](https://github.com/astral-sh/setup-uv) is Astral's official Action for getting `uv`. I'm annoyed that it appears to hit Astral's own `releases.astral.sh` site every time it runs but if that's how they want it to work I guess that's on them.

Those settings:

- `enable-cache: true` turns on GitHub Actions caching
- `cache-dependency-glob: ""` disables the feature where it looks for `pyproject.toml` or similar to use as a cache key
- `cache-suffix: "tools-${{ env.UV_EXCLUDE_NEWER }}"` is the bit that uses our single `UV_EXCLUDE_NEWER` value for the cache key
- `prune-cache: false` is necessary because Astral default to deliberately pruning your cache of any downloaded wheels, the exact opposite of what I want!

I should note that my preferences here go directly against [what uv advises](https://docs.astral.sh/uv/concepts/cache/#caching-in-continuous-integration):

> However, in continuous integration environments, persisting pre-built wheels may be undesirable. With uv, it turns out that it's often faster to _omit_ pre-built wheels from the cache (and instead re-download them from the registry on each run).

Personally I'd rather suffer from very slightly slower CI builds (presumably because GitHub's cache restore operations are slower than fresh installations from PyPI?) than optimize my builds by hitting the PyPI CDN for every tool execution.

This block here enforces that the cache is used correctly:
```
      - name: Require cache-only uv on cache hits
        if: steps.setup-uv.outputs.cache-hit == 'true'
        run: echo "UV_OFFLINE=1" >> "$GITHUB_ENV"
```
Setting that `UV_OFFLINE=1` environment variable causes `uvx tool-name` to fail if the tool has not been previously installed. We only run that if we got a cache hit from the GitHub Actions cache.

This means that if you add a new tool to the workflow without also bumping the `UV_EXCLUDE_NEWER` date you'll get an error.
