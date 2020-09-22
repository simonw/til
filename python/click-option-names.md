# Understanding option names in Click

I hit [a bug today](https://github.com/simonw/datasette/issues/973) where I had defined a Click option called `open` but in doing so I replaced the Python bulit-in `open()` function:

```python
@click.command()
# ...
@click.option("-o", "--open", is_flag=True, help="Open Datasette in your web browser")
def my_command(open):
    # Now open() is no longer available
```
This inspired me to finally figure out how Click function argument names work. It's documented here: https://click.palletsprojects.com/en/7.x/options/#name-your-options

Short version: you can do this:

```python
@click.command()
# ...
@click.option("-o", "--open", "open_browser", is_flag=True, help="Open Datasette in your web browser")
def my_command(open_browser):
    # Now open() is no longer available
```
Click will use the positional argument without any hyphen prefixes as the name of the argument. If none is provided it will use the first `--` one. If that's not defined it will use the `-o` one - all with the hypens stripped.
