# Writing a Datasette CLI plugin that mostly duplicates an existing command

My new [datasette-gunicorn](https://datasette.io/plugins/datasette-gunicorn) plugin adds a new command to Datasette - `datasette gunicorn` - which mostly replicates the existing `datasette serve` command but with a few differences.

I learned some useful tricks for modifying and extending existing [Click](https://click.palletsprojects.com/) commands building this plugin.

Here's the relevant section of code, with some extra comments (the [full code is here](https://github.com/simonw/datasette-gunicorn/blob/0.1/datasette_gunicorn/__init__.py)):

```python
import click
from datasette import hookimpl

# These options do not work with 'datasette gunicorn':
invalid_options = {
    "get",
    "root",
    "open_browser",
    "uds",
    "reload",
    "pdb",
    "ssl_keyfile",
    "ssl_certfile",
}


def serve_with_gunicorn(**kwargs):
    # Avoid a circular import error running the tests:
    from datasette import cli

    workers = kwargs.pop("workers")
    port = kwargs["port"]
    host = kwargs["host"]
    # Need to add back default kwargs for everything in invalid_options:
    kwargs.update({invalid_option: None for invalid_option in invalid_options})
    kwargs["return_instance"] = True
    ds = cli.serve.callback(**kwargs)
    # ds is now a configured Datasette instance
    asgi = StandaloneApplication(
        app=ds.app(),
        options={
            "bind": "{}:{}".format(host, port),
            "workers": workers,
        },
    )
    asgi.run()


@hookimpl
def register_commands(cli):
    # Get a reference to the existing "datasette serve" command
    serve_command = cli.commands["serve"]
    # Create a new list of params, excluding any in invalid_options
    params = [
        param for param in serve_command.params if param.name not in invalid_options
    ]
    # This is the longer way of constructing a new Click option, as an alternative
    # to using the @click.option() decorator
    params.append(
        click.Option(
            ["-w", "--workers"],
            type=int,
            default=1,
            help="Number of Gunicorn workers",
            # Causes [default: 1] to show in the option help
            show_default=True,
        )
    )
    gunicorn_command = click.Command(
        name="gunicorn",
        params=params,
        callback=serve_with_gunicorn,
        short_help="Serve Datasette using Gunicorn",
        help="Start a Gunicorn server running to serve Datasette",
    )
    # cli is the Click command group passed to this plugin hook by
    # Datasette - this is how we add the "datasette gunicorn" command:
    cli.add_command(gunicorn_command, name="gunicorn")
```
Here's the documentation for the [register_commands() plugin hook](https://docs.datasette.io/en/stable/plugin_hooks.html#register-commands-cli). It is passed `cli` which is a Click command group.

`cli.add_command(...)` can then be used to register additional commands - in this case the `datasette gunicorn` one.

I want that command to take _almost_ the same options as the existing `datasette serve` command - which is defined [here in the Datasette codebase](https://github.com/simonw/datasette/blob/0.62/datasette/cli.py#L468-L498).

So... I start by creating a copy of those options. But there are a few options which don't make sense for my new command (see [this issue](https://github.com/simonw/datasette-gunicorn/issues/2)). So I filtered those out with a list comprehension:

```python
params = [
    param for param in serve_command.params if param.name not in invalid_options
]
```
I did need one extra option: a `-w/--workers` integer specifying the number of workers that should be started by Gunicorn.

Here's the [relevant Click documentation](https://click.palletsprojects.com/en/8.1.x/api/#click.Option). I defined it like this:

```python
params.append(
    click.Option(
        ["-w", "--workers"],
        type=int,
        default=1,
        help="Number of Gunicorn workers",
        # Causes [default: 1] to show in the option help
        show_default=True,
    )
)
```
I defined the new `gunicorn` command like this:
```python
gunicorn_command = click.Command(
    name="gunicorn",
    params=params,
    callback=serve_with_gunicorn,
    short_help="Serve Datasette using Gunicorn",
    help="Start a Gunicorn server running to serve Datasette",
)
cli.add_command(gunicorn_command, name="gunicorn")
```
The `short_help` is shown in the list of commands displayed by `datasette --help`.

The `help` is shown at the top of the list of options when you run `datasette gunicorn --help`.

The most important argument here is `callback=` - this is the function which will be executed when the user types `datasette gunicorn ...`.

Here's a partial implementation of that function:
```python
def serve_with_gunicorn(**kwargs):
    # Avoid a circular import error running the tests:
    from datasette import cli

    workers = kwargs.pop("workers")
    port = kwargs["port"]
    host = kwargs["host"]
    # Need to add back default kwargs for everything in invalid_options:
    kwargs.update({invalid_option: None for invalid_option in invalid_options})
    kwargs["return_instance"] = True
    ds = cli.serve.callback(**kwargs)
    # ds is now a configured Datasette instance
    asgi = StandaloneApplication(
        app=ds.app(),
        options={
            "bind": "{}:{}".format(host, port),
            "workers": workers,
        },
    )
    asgi.run()
```
The `**kwargs` passed to that function are the options and argumenst that have been extracted from the command line by Click.

In this case, I know I'm going to be calling the existing `serve` function from Datasette. `cli.serve` is the Click decorated version, but `cli.serve.callback()` is the original function I defined in my own Datasette source code (linked above).

That function in Datasette takes a list of keyword arguments, which I need to pass through.

The `kwargs` passed to `serve_with_gunicorn()` are not quite right - remember, I removed some options earlier, and I also added a `workers` option that `serve()` doesn't know how to handle.

So I pop `workers` off the dictionary, and I add `"name": None` keys for the `invalid_options` that I previously filtered out.

One last trick: my `serve()` function [here in Datasette](https://github.com/simonw/datasette/blob/0.62/datasette/cli.py#L468-L498) has an extra `return_instance` keyword argument, which can be used to shortcut that function and return the configured Datasette instance instead of starting the server.

I originally built this to help with unit tests, but this is also exactly what I need for this particular plugin! I set that to true to get back a configured Datasette object instance, which I can then use to serve the application using Gunicorn.
