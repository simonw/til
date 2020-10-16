# Explicit file encodings using click.File

I wanted to add a `--encoding` option to `sqlite-utils insert` which could be used to change the file encoding used to read the incoming CSV or TSV file.

Just one problem: the Click file argument was defined using `click.File()`, which has useful features like automatically handling `-` for standard input. The code looked like this:

```python
@click.argument("json_file", type=click.File(), required=True)
# ...
def command(json_file):
    # ...
```
`click.File()` takes an optional `encoding=` parameter, but that requires you to know the file encoding in advance. In my case I wanted to use the encoding optionally provided by an `--encoding=` option.

The workaround I came up with was to switch to using `click.File("rb")`, which opened the incoming file (or stdin stream) in binary mode. I could then wrap it in a `codecs.getreader()` object that could convert those bytes into a Python string using the user-supplied encoding.

```python
@click.argument("json_file", type=click.File("rb"), required=True)
@click.option("--encoding", help="Character encoding for input, defaults to utf-8")
def command(json_file, encoding):
    encoding = encoding or "utf-8"
    json_file = codecs.getreader(encoding)(json_file)
    reader = csv.reader(json_file)
    # ...
```
