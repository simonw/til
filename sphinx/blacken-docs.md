# Format code examples in documentation with blacken-docs

I decided to enforce that all code examples in the [Datasette documentation](https://docs.datasette.io/) be formatted using [Black](https://github.com/psf/black). Here's [issue 1718](https://github.com/simonw/datasette/issues/1718) where I researched the options for doing this.

I found  the [blacken-docs](https://pypi.org/project/blacken-docs/) tool. Here's how to run it against a folder full of reStructuredText files:

    pip install blacken-docs
    blacken-docs docs/*.rst

This modifies the files in place.

## Setting a different line length

I read most documentation on my phone, so when I'm writing code examples I tend to try to keep the line lengths a little bit shorter to avoid having to scroll sideways when reading.

`blacken-docs` has a `-l` option for changing the length (Black defaults to 88 characters) which can be used like this:

    blacken-docs -l 60 docs/*.rst

## Running this in CI

The `blacken-docs` command outputs errors if it finds any Python examples it cannot parse. I actually found a couple of bugs in my examples using this, so it's a handy feature.

This also causes the tool to exit with a status code of 1:
```
% blacken-docs -l 60 docs/*.rst                        
docs/authentication.rst: Rewriting...
docs/internals.rst:196: code block parse error Cannot parse: 14:0: <line number missing in source>
docs/json_api.rst:449: code block parse error Cannot parse: 1:0: <link rel="alternate"
docs/plugin_hooks.rst:250: code block parse error Cannot parse: 6:4:     ]
docs/plugin_hooks.rst:311: code block parse error Cannot parse: 38:0: <line number missing in source>
% echo $?
1
```
I also wanted my CI to fail if the author had forgotten to run `blacken-docs` against the repository before pushing the commit.

I filed [a feature request](https://github.com/asottile/blacken-docs/issues/161) asking for an equivalent of the `black . --check` option, but it turns out that feature isn't necessary - `blacken-docs` returns a non-zero exit code if it makes any changes. So just running the following in CI works for checking if it should have been applied:

```yaml
    - name: Check if blacken-docs needs to be run
      run: |
        blacken-docs -l 60 docs/*.rst
```
