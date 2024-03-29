# Using cog to update --help in a Markdown README file

My [csvs-to-sqlite README](https://github.com/simonw/csvs-to-sqlite/blob/main/README.md) includes a section that shows the output of the `csvs-to-sqlite --help` command ([relevant issue](https://github.com/simonw/csvs-to-sqlite/issues/82)).

I had been manually copying this in, but I decided to try using [cog](https://nedbatchelder.com/code/cog) to automate the process.

Here's what I came up with:

````markdown
<!-- [[[cog
import cog
from csvs_to_sqlite import cli
from click.testing import CliRunner
runner = CliRunner()
result = runner.invoke(cli.cli, ["--help"])
help = result.output.replace("Usage: cli", "Usage: csvs-to-sqlite")
cog.out(
    "```\n{}\n```".format(help)
)
]]] -->
```
Usage: csvs-to-sqlite [OPTIONS] PATHS... DBNAME
...
```
<!-- [[[end]]] -->
````
Then to update the README file, run this:

    cog -r README.md

The `-r` option causes it to modify that file in place.

Cog works by scanning for a `[[[cog ... ]]]` section, executing the code there, capturing the `cog.out()` output and using that to replace everything from the end of the code block up to the line containing the `[[[end]]]` marker.

It's designed to interact well with comments - in this case HTML comments - such that the `cog` generation code can be hidden.

## Testing with cog --check

A version of Cog released after I first wrote this TIL added a new `--check` option, so you can run a test in CI to check if the file needs to be updated using:

    cog --check README.md

## Writing a test (before cog --check)

Any time I generate content like this in a repo I like to include a test that will fail if I forget to update the content.

`cog` clearly isn't designed to be used as an independent library, but I came up with the following pattern `pytest` test which works well, in my `tests/test_csvs_to_sqlite.py` module:

```python
from cogapp import Cog
import sys
from io import StringIO
import pathlib


def test_if_cog_needs_to_be_run():
    _stdout = sys.stdout
    sys.stdout = StringIO()
    readme = pathlib.Path(__file__).parent.parent / "README.md"
    result = Cog().main(["cog", str(readme)])
    output = sys.stdout.getvalue()
    sys.stdout = _stdout
    assert (
        output == readme.read_text()
    ), "Run 'cog -r README.md' to update help in README"
```
The key line here is this one:
```python
result = Cog().main(["cog", str(readme)])
```
In cog's implementation, that code is called like this:
```python
Cog().main(sys.argv)
```
Here I'm faking the command-line arguments to pass in just the path to my `README.md` file.

Cog then writes the generated output to `stdout` - which I capture with that `sys.stdout` trick.

Finally, I compare the generated output to the current file content and fail the test with a reminder to run `cog -r` if they do not match.

## Cog for reStructuredText

Here's an example of `cog` in a `.rst` file:

```rst
.. [[[cog
    import tabulate
    cog.out("\n" + "\n".join('- ``{}``'.format(t) for t in tabulate.tabulate_formats) + "\n\n")
.. ]]]

- ``fancy_grid``
- ``fancy_outline``
- ``github``

.. [[[end]]]
```
The trailing and leading newlines are important to avoid a warning about "Explicit markup ends without a blank line; unexpected unindent".

## CLI reference pages

I added these to both Datasette and `sqlite-utils`: full pages that list the help for every command provided by those tools.

- [Datasette CLI reference](https://docs.datasette.io/en/stable/cli-reference.html) - underlying [source code](https://raw.githubusercontent.com/simonw/datasette/main/docs/cli-reference.rst)
- [sqlite-utils CLI reference](https://sqlite-utils.datasette.io/en/stable/cli-reference.html) - underlying [source code](https://raw.githubusercontent.com/simonw/sqlite-utils/main/docs/cli-reference.rst)
