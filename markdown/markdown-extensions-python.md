# Useful Markdown extensions in Python

I wanted to render some markdown in Python but with the following extra features:

- URLize any bare URLs in the content, like GFM
- Handle `` ```python `` at the start of a block without showing the `python` bit (even if no syntax highlight is applied)
- Show a table of contents

For URLizing the best solution I've found is [r0wb0t/markdown-urlize](https://github.com/r0wb0t/markdown-urlize) - it's not available on PyPI so you have to download the [mdx_urlize.py](https://github.com/r0wb0t/markdown-urlize/blob/master/mdx_urlize.py) file and import from it.

The other two features can be handled by the [toc](https://python-markdown.github.io/extensions/toc/) and [fenced_code](https://python-markdown.github.io/extensions/fenced_code_blocks/) extensions, both of which are included with Python Markdown and can be activated by passing their names as strings to the `extensions=` list.

Here's what I ended up doing (in a Django view):

```python
from mdx_urlize import UrlizeExtension
import markdown
import pathlib

def docs(request):
    content = (pathlib.Path(__file__).parent / "docs.md").read_text()
    md = markdown.Markdown(
        extensions=["toc", "fenced_code", UrlizeExtension()], output_format="html5"
    )
    html = md.convert(content)
    return render(
        request,
        "docs.html",
        {
            "content": html,
            "toc": md.toc,
        },
    )
```
And in the `docs.html` template:

```html+django
{% extends "base.html" %}

{% block title %}Documentation{% endblock %}

{% block content %}
<h1>Documentation</h1>
{{ toc|safe }}
{{ content|safe }}
{% endblock %}
```
