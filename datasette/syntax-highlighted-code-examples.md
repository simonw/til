# Syntax highlighted code examples in Datasette

I wanted to add syntax highlighting to the new tutorial [Data analysis with SQLite and Python](https://datasette.io/tutorials/data-analysis).

That page is using the new `{% markdown %}` tag from [datasette-render-markdown](https://datasette.io/plugins/datasette-render-markdown).

I figured out a recipe for adding GitHub-style syntax highlighting to Markdown rendered using that tag.

## Dependencies
```bash
datasette install datasette-render-markdown
datasette install Pygments
```
[Pygments](https://pygments.org/) is an optional dependency for the Python `markdown` library which enables syntax highlighting via an extension.

## The template markup

Here's the recipe that worked:

````html+jinja
{% markdown
  extensions="fenced_code codehilite"
  extra_tags="span div"
  extra_attrs="span:class div:class" %}
## Here comes some code
Python code here:
```python
def this_will_be(highlighted):
    "This works
    pass
```
Other languages work too:
```sql
select 1 + 1;
```
{% endmarkdown %}
````
The magic is all in that opening `{% markdown %}` tag.

We're loading two [markdown extensions](https://python-markdown.github.io/extensions/):

- [fenced_code](https://python-markdown.github.io/extensions/fenced_code_blocks/) adds support for those triple-backtick code blocks, and enables tagging them with the language name as well.
- [codehilite](https://python-markdown.github.io/extensions/code_hilite/) adds syntax highlighting. This will only work if [Pygments](https://pygments.org/) is installed - it will fail silently otherwise.

`datasette-render-markdown` defaults to stripping all but the safest HTML tags and attributes using [Bleach](https://bleach.readthedocs.io/).

In this case we want to keep `span` and `div` tags, since those are used by the syntax highlighter. We also want both of those tags to be allowed to have the `class` element on them.

The resulting HTML looks something like this (truncated):
```html
<div class="codehilite">
  <pre><span></span><code><span class="k">def</span> <span class="nf">parse_pep</span><span class="p">(</span>
```

## Adding the CSS

Pygments has [a neat collection](https://pygments.org/styles/) of default styles. I decided I liked "sas".

I couldn't see an obvious way to output the CSS, so I used ChatGPT to help figure out this Python one-liner to print out the CSS:

```bash
python -c 'from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name
formatter = HtmlFormatter(style="sas")
print(formatter.get_style_defs(".codehilite"))
'
```
I later found out that wasn't necessary - you can run this instead:
```bash
pygmentize -f html -S sas -a .codehilite
```
Both of those will output the CSS you need to add to your stylesheet to style the syntax highlighted text.

