# TOML in Python

I finally got around to fully learning [TOML](https://toml.io/). Some notes, including how to read and write it from Python.

## The data structure

A TOML file is a document that contains a dictionary of key value pairs. TOML calls this a "table" - but any time you see the term "table" you can think of it as a hash table or dictionary.

(I found this unintuitive because I think of tables as SQL-style tables with a set of rows containing the same columns - but that's not what a "table" means in TOML.)

The keys are always strings. The values can be:

- Strings e.g. `"hello"`
- Integers e.g. `42`
- Floats e.g. `3.14`
- Booleans e.g. `true` or `false`
- Various  RFC 3339 date and time values e.g. `1979-05-27` or `1979-05-27T07:32:00`
- An array of items of the same type of value, e.g. `[1, 2, 3]` or `["a", "b", "c"]`
- Another table (a nested key-value document)

TOML supports multi-line strings using Python-style triple quotes:

```toml
multi_line_string = """
This is a
multi-line
string.
"""
```

## More than one way to represent things

This confused me at first. You can represent the same data structure using different syntax in TOML, particularly for arrays and nested tables.

These two examples are exactly equivalent (from [the spec](https://toml.io/en/v1.0.0#inline-table)):

```toml
[name]
first = "Tom"
last = "Preston-Werner"

[point]
x = 1
y = 2

[animal]
type.name = "pug"
```
And (using inline syntax):
```toml
name = { first = "Tom", last = "Preston-Werner" }
point = { x = 1, y = 2 }
animal = { type = { name = "pug" } }
```
That last line can also be:
```toml
animal = { type.name = "pug" }
```
The same is true of arrays. This example uses `[[...]]` syntax:
```toml
[[products]]
name = "Hammer"
sku = 738594937

[[products]]
name = "Nail"
sku = 284758393
```
It is equivalent to the following:
```toml
products = [
  { name = "Hammer", sku = 738594937 },
  { name = "Nail",   sku = 284758393 }
]
```
## TOML in Python

Python 3.11 added TOML parsing support in the standard library, in the [tomllib](https://docs.python.org/3/library/tomllib.html) package in the standard library:

```python
import tomllib

with open("pyproject.toml", "rb") as f:
    data = tomllib.load(f)

toml_str = """
python-version = "3.11.0"
python-implementation = "CPython"
"""

data2 = tomllib.loads(toml_str)
```
This is effectively a vendored version of [tomli](https://github.com/hukkin/tomli), which is available for previous Python versions via `pip install tomli`:
```pycon
>>> import tomli
>>> tomli.loads("foo = 1\nbar = 2")
{'foo': 1, 'bar': 2}
```

## Serializing to TOML

Notably, neither of these provides the ability to *serialize TOML back out again*. That's because there are multiple ways to serialize TOML and the libraries decided not to take an opinion on the best way to do so.

The [tomli-w](https://github.com/hukkin/tomli-w) package provides a basic serialization mechanism:

```python
import tomli_w

doc = {
    "table": {
        "nested": {}, "val3": 3
    },
    "val2": 2,
    "val1": 1
}
toml_string = tomli_w.dumps(doc)
```
A more advanced option is [tomlkit](https://github.com/sdispater/tomlkit), which describes itself as a " Style-preserving TOML library for Python".

`tomlkit` is capable of updating an existing TOML document while keeping things like style decisions and inline comments intact. It can also be used to construct a fresh TOML document from scratch with those extra syntax decisions, as demonstrated [in the documentation](https://github.com/sdispater/tomlkit/blob/master/docs/quickstart.rst):

```python
from tomlkit import comment, document, dumps, nl, table
from datetime import datetime, timezone

doc = document()
doc.add(comment("This is a TOML document."))
doc.add(nl())
doc.add("title", "TOML Example")
# Using doc["title"] = "TOML Example" is also possible

owner = table()
owner.add("name", "Tom Preston-Werner")
owner.add("organization", "GitHub")
owner.add("bio", "GitHub Cofounder & CEO\nLikes tater tots and beer.")
owner.add("dob", datetime(1979, 5, 27, 7, 32, tzinfo=timezone.utc))
owner["dob"].comment("First class dates? Why not?")

# Adding the table to the document
doc.add("owner", owner)
print(dumps(doc))
```
This will output:
```toml
# This is a TOML document.

title = "TOML Example"

[owner]
name = "Tom Preston-Werner"
organization = "GitHub"
bio = "GitHub Cofounder & CEO\nLikes tater tots and beer."
dob = 1979-05-27T07:32:00Z # First class dates? Why not?
```
