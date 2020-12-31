# Using Prettier to check JavaScript code style in GitHub Actions

I [decided](https://github.com/simonw/datasette/issues/1166) to adopt [Prettier](https://prettier.io/) as the JavaScript code style for Datasette, based on my success with [Black](https://github.com/psf/black) for Python code.

I added `.prettierrc` to the root of the repo with the following settings:

```json
{
  "tabWidth": 2,
  "useTabs": false
}
```

Then I created the following `.github/workflows/prettier.yml` file:

```yaml
name: Check JavaScript for conformance with Prettier

on:
  push:
  pull_request:

jobs:
  prettier:
    runs-on: ubuntu-latest
    steps:
    - name: Check out repo
      uses: actions/checkout@v2
    - uses: actions/cache@v2
      name: Configure npm caching
      with:
        path: ~/.npm
        key: ${{ runner.os }}-npm-${{ hashFiles('**/workflows/prettier.yml') }}
        restore-keys: |
          ${{ runner.os }}-npm-
    - name: Run prettier
      run: |-
        npx prettier --check 'datasette/static/*[!.min].js'
```

The `npx prettier --check 'datasette/static/*[!.min].js'` line ensures that prettier is run in "check" mode (which fails the tests if a matching file does not conform to the formatting rules) - it checks any `.js` file in the `datasette/static` folder but excludes any `.min.js` minified files.

I'm using `npx` to run Prettier which installs it if it is missing - as far as I can tell `npx` respects the `.npm` cache so I'm using that to avoid downloading a new copy of Prettier every time.

I decided to use the hash of the `prettier.yml` file itself as the key for the cached data, so any time I change the workflow it should invalidate the cache.
