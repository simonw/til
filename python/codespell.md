# Check spelling using codespell

Today I discovered [codespell](https://github.com/codespell-project/codespell/) via [this Rich commit](https://github.com/willmcgugan/rich/commit/9c12a4537499797c43725fff5276ef0da62423ef#diff-ce84a1b2c9eb4ab3ea22f610cad7111cb9a2f66365c3b24679901376a2a73ab2). `codespell` is a really simple spell checker that can be run locally or incorporated into a CI flow.

Basic usage:

    pip install codespell
    codespell docs/*.rst

This outputs any spelling errors it finds in those files. I got this the first time I ran it against the Datasette documentation:

```
docs/authentication.rst:63: perfom ==> perform
docs/authentication.rst:76: perfom ==> perform
docs/changelog.rst:429: repsonse ==> response
docs/changelog.rst:503: permissons ==> permissions
docs/changelog.rst:717: compatibilty ==> compatibility
docs/changelog.rst:1172: browseable ==> browsable
docs/deploying.rst:191: similiar ==> similar
docs/internals.rst:434: Respons ==> Response, respond
docs/internals.rst:440: Respons ==> Response, respond
docs/internals.rst:717: tha ==> than, that, the
docs/performance.rst:42: databse ==> database
docs/plugin_hooks.rst:667: utilites ==> utilities
docs/publish.rst:168: countainer ==> container
docs/settings.rst:352: inalid ==> invalid
docs/sql_queries.rst:406: preceeded ==> preceded, proceeded
```
You can create a file of additional words that it should ignore and pass that using the `--ignore-words` option:

    codespell docs/*.rst --ignore-words docs/codespell-ignore-words.txt

Since I don't have any words in that file yet I added one fake word, so my file looks like this:

```
AddWordsToIgnoreHere
```
Each ignored word should be on a separate line.

I added it to my GitHub Actions CI like this:
```yaml

name: Check spelling in documentation

on: [push, pull_request]

jobs:
  spellcheck:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - uses: actions/cache@v2
      name: Configure pip caching
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-spellcheck
        restore-keys: |
          ${{ runner.os }}-pip-spellcheck
    - name: Install dependencies
      run: |
        pip install codespell
    - name: Check spelling
      run: codespell docs/*.rst --ignore-words docs/codespell-ignore-words.txt
```
Now any push or pull request will have the spell checker applied to it, and will fail if any new incorrectly spelled words are detected.

Here's [the full PR](https://github.com/simonw/datasette/pull/1418) where I added this to Datasette, and [the commit](https://github.com/simonw/sqlite-utils/commit/991cf56ae2840aaefda2af828a5c40396d2506ca) where I added this to `sqlite-utils`.
