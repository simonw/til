# Turning on Jinja autoescaping when using Template() directly

Jinja autoescaping is turned off by default. Coming from Django this frequently catches me out.

You can turn on autoescaping for your Jinja environment using:

```python
from jinja2 import Environment, FileSystemLoader

env = Environment(
    loader=FileSystemLoader("/path/to/templates"),
    autoescape=True
)
```

But what about if you are using `Template` directly? TIL that the `Template` class takes all of the same options as `Environment` does, so you can do this:

```python
from jinja2 import Template

template = Template("""
<p>Hello {{ name }}</p>
""", autoescape=True)

print(template.render({"name": "Simon & Cleo"}))
# Output: <p>Hello Simon &amp; Cleo</p>
```
Here's the [Template class constructor](https://github.com/pallets/jinja/blob/2.11.2/src/jinja2/environment.py#L984-L1005).
