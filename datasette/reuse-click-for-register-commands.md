# Reusing an existing Click tool with register_commands

The [register_commands](https://docs.datasette.io/en/stable/plugin_hooks.html#register-commands-cli) plugin hook lets you add extra sub-commands to the `datasette` CLI tool.

I have a lot of existing tools that I'd like to also make available as plugins. I figured out this pattern for my [git-history](https://datasette.io/tools/git-history) tool today:

```python
from datasette import hookimpl
from git_history.cli import cli as git_history_cli

@hookimpl
def register_commands(cli):
    cli.add_command(git_history_cli, name="git-history")
```
Now I can run the following:

```
% datasette git-history --help
Usage: datasette git-history [OPTIONS] COMMAND [ARGS]...

  Tools for analyzing Git history using SQLite

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  file  Analyze the history of a specific file and write it to SQLite
```

I initially tried doing this:

```python
@hookimpl
def register_commands(cli):
    cli.command(name="git-history")(git_history_file)
```
But got the following error:

    TypeError: Attempted to convert a callback into a command twice.

Using [cli.add_command()](https://click.palletsprojects.com/en/8.0.x/api/?highlight=add_command#click.Group.add_command) turns out to be the right way to do this.

Research issue for this: [datasette#1538](https://github.com/simonw/datasette/issues/1538).
