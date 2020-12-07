# Controlling the style of dumped YAML using PyYAML

I had a list of Python dictionaries I wanted to output as YAML, but I wanted to control the style of the output.

Here's the data:
```python
items = [
    {
        "date": "2020-11-28",
        "body": "[Datasette 0.52](https://docs.datasette.io/en/stable/changelog.html#v0-52) - `--config` is now `--setting`, new `database_actions` plugin hook, `datasette publish cloudrun --apt-get-install` option and several bug fixes.",
    },
    {
        "date": "2020-10-31",
        "body": "[Datasette 0.51](https://docs.datasette.io/en/stable/changelog.html#v0-51) - A new visual design, plugin hooks for adding navigation options, better handling of binary data, URL building utility methods and better support for running Datasette behind a proxy. [Annotated release notes](https://simonwillison.net/2020/Nov/1/datasette-0-51/).",
    },
]
```
By default, the YAML output by `import yaml; print(yaml.dump(items))` looks like this:
```yaml
- body: '[Datasette 0.52](https://docs.datasette.io/en/stable/changelog.html#v0-52)
    - `--config` is now `--setting`, new `database_actions` plugin hook, `datasette
    publish cloudrun --apt-get-install` option and several bug fixes.'
  date: '2020-11-28'
- body: '[Datasette 0.51](https://docs.datasette.io/en/stable/changelog.html#v0-51)
    - A new visual design, plugin hooks for adding navigation options, better handling
    of binary data, URL building utility methods and better support for running Datasette
    behind a proxy. [Annotated release notes](https://simonwillison.net/2020/Nov/1/datasette-0-51/).'
  date: '2020-10-31'
```
I wanted to list the `date` key first, and I wanted the `body` key to use `|-` YAML multi-line syntax rather than a single quoted string.

I ended up combining [these](https://stackoverflow.com/a/8641732) [two](https://stackoverflow.com/a/16782282) recipes from Stack Overflow. First I registered new representers with PyYaml:

```python
import yaml
from collections import OrderedDict

class literal(str):
    pass

def literal_presenter(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


yaml.add_representer(literal, literal_presenter)

def represent_ordereddict(dumper, data):
    value = []

    for item_key, item_value in data.items():
        node_key = dumper.represent_data(item_key)
        node_value = dumper.represent_data(item_value)

        value.append((node_key, node_value))

    return yaml.nodes.MappingNode(u"tag:yaml.org,2002:map", value)

yaml.add_representer(OrderedDict, represent_ordereddict)
```
Then I used the following Python code to output my YAML in the desired key order:
```python
print(yaml.dump([OrderedDict([
    ("date", item["date"]),
    ("body", literal(item["body"]))
]) for item in items]))
```
The result was:
```yaml
- date: '2020-11-28'
  body: |-
    [Datasette 0.52](https://docs.datasette.io/en/stable/changelog.html#v0-52) - `--config` is now `--setting`, new `database_actions` plugin hook, `datasette publish cloudrun --apt-get-install` option and several bug fixes.
- date: '2020-10-31'
  body: |-
    [Datasette 0.51](https://docs.datasette.io/en/stable/changelog.html#v0-51) - A new visual design, plugin hooks for adding navigation options, better handling of binary data, URL building utility methods and better support for running Datasette behind a proxy. [Annotated release notes](https://simonwillison.net/2020/Nov/1/datasette-0-51/).
```
Ideally I'd like to wrap that text within those `|-` blocks but I haven't figured out a way to do that yet.
