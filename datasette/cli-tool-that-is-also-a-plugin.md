# Writing a CLI utility that is also a Datasette plugin

I'm working on [dclient](https://github.com/simonw/dclient), a CLI tool for interacting with Datasette instances via the Datasette API.

The tool is used like this:
```
dclient query https://latest.datasette.io/fixtures "select * from facetable limit 1"
```
I decided to see if I could have it optionally work as a Datasette plugin too, so you could run the command like this as well:
```
datasette client query https://latest.datasette.io/fixtures "select * from facetable limit 1"
```
This would need to use the [register_commands() plugin hook](https://docs.datasette.io/en/stable/plugin_hooks.html#register-commands-cli).

Here's the pattern I used for that which works.

## In setup.py

I generated the initial tool using my [click-app](https://github.com/simonw/click-app) cookiecutter template.

To get it to work as both a CLI tool and a Datasette plugin I needed to modify `setup.py` to include this:

```python
    entry_points={
        "datasette": ["client = dclient.plugin"],
        "console_scripts": ["dclient = dclient.cli:cli"],
    }
```
The `dclient/cli.py` module contains the Click application definition itself.

`dclient/plugin.py` is an entirely new module which I created to get this to work.

## dclient/plugin.py

The `plugin.py` module contains the following:

```python
from datasette import hookimpl


@hookimpl
def register_commands(cli):
    from .cli import cli as dclient_cli

    cli.add_command(dclient_cli, name="client")
```

Note that it imports from `datasette` even though Datasette is not one of the dependencies included in `setup.py`. This works OK - the `plugin.py` module is only loaded by Datasette's plugin mechanism if Datasette is itself installed.

The `register_commands()` hook implementation is passed the `cli` object used by Datasette itself. I can use `cli.add_command(...)` to add a new command to it - in this case a command group, but either works fine.

Without the `name="client" parameter here the command registered as `datasette cli --help`, which wasn't what I wanted.

## dclient/cli.py

You can [see that module here](https://github.com/simonw/dclient/blob/0.1a2/dclient/cli.py) - it's the bulk of the implementation of the tool. It's a standard Click application.
