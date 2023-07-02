# Custom Jinja template tags with attributes

I decided to implement a custom Jinja template block tag for my [datasette-render-markdown](https://datasette.io/plugins/datasette-render-markdown) plugin. I wanted the tag to work like this:

```html+jinja
{% markdown %}
# This will be rendered as markdown

- Bulleted
- List
{% endmarkdown %}
```

## A basic Jinja extension

After some fiddling around with GitHub Code Search and ChatGPT I settled on this as the simplest possible skeleton for a custom Jinja tag:

```python
from jinja2 import nodes
from jinja2.exceptions import TemplateSyntaxError
from jinja2.ext import Extension


class MarkdownExtension(Extension):
    tags = set(["markdown"])

    def __init__(self, environment):
        super(MarkdownExtension, self).__init__(environment)

    def parse(self, parser):
        # We need this for reporting errors
        lineno = next(parser.stream).lineno
        body = parser.parse_statements(
            ["name:endmarkdown"], drop_needle=True
        )
        return nodes.CallBlock(
            self.call_method("_render_markdown"),
            [],
            [],
            body,
        ).set_lineno(lineno)

    async def _render_markdown(self, caller):
        return render_markdown(await caller())
```
Then add it to the Jinja environment like this:
```python
env.add_extension(MarkdownExtension)
```
Note that my `_render_makdown()` method there is `async def`. This appeared to be necessary because I run Jinja for Datasette in [async mode](https://jinja.palletsprojects.com/en/3.0.x/api/#jinja2.Template.render_async). If I didn't I think this would work like this instead:

```python
    def _render_markdown(self, caller):
        return render_markdown(caller())
```
I'm not sure of the best way to build an extension that works in both async and regular modes.

## Adding support for attributes

My [render_markdown() function](https://github.com/simonw/datasette-render-markdown/blob/d437435161af8885ab206a85664f49d9dc0f368b/datasette_render_markdown/__init__.py#L46-L81) takes optional arguments for specifying if certain Markdown extensions should be enabled, or which additional tags and attributes should be allowed rather than being stripped by [Bleach](https://github.com/mozilla/bleach).

I decided to use the following syntax for that:

```html+jinja
{% markdown
  extensions="tables"
  extra_tags="table thead tr th td tbody" 
  extra_attrs="p:id,class a:name,href" %}
## Markdown table

First Header  | Second Header
------------- | -------------
Content Cell  | Content Cell
Content Cell  | Content Cell

<a href="https://www.example.com/" name="namehere">Example</a>
<p id="paragraph" class="klass">Paragraph</p>
{% endmarkdown %}
```
Adding `key="value"` attribute support to a custom Jinja tag was trickier than I expected!

You have to work directly with the parser.

After spending some time in the Python debugger, I figured out that the tokens in my test document looked something like this:

```python
[Token(lineno=6, type='name', value='markdown'),
 Token(lineno=6, type='name', value='foo'),
 Token(lineno=6, type='assign', value='='),
 Token(lineno=6, type='string', value='bar'),
 Token(lineno=6, type='name', value='baz'),
 Token(lineno=6, type='assign', value='='),
 Token(lineno=6, type='string', value='bar2'),
 Token(lineno=6, type='block_end', value='%}'),
 Token(lineno=6, type='data', value='\n# This is markdown'),
 Token(lineno=11, type='block_begin', value='{%'),
 Token(lineno=11, type='name', value='endmarkdown'),
 Token(lineno=11, type='block_end', value='%}'),
 Token(lineno=11, type='data', value='\n')]
```
To turn `key="value"` syntax into a dictionary of attributes, I would need to read every token up to the `block_end` (`"%}"`) token, then look for sequences of three tokens - a `name`, an `assign` (=) and a `string`.

I ended up writing this code to do that:

```python
    def parse(self, parser):
        # We need this for reporting errors
        lineno = next(parser.stream).lineno

        # Gather tokens up to the next block_end ('%}')
        gathered = []
        while parser.stream.current.type != "block_end":
            gathered.append(next(parser.stream))

        # If all has gone well, we will have a sequence of triples of tokens:
        #   (type='name, value='attribute name'),
        #   (type='assign', value='='),
        #   (type='string', value='attribute value')
        # Anything else is a parse error

        if len(gathered) % 3 != 0:
            raise TemplateSyntaxError("Invalid syntax for markdown tag", lineno)
        attrs = {}
        for i in range(0, len(gathered), 3):
            if (
                gathered[i].type != "name"
                or gathered[i + 1].type != "assign"
                or gathered[i + 2].type != "string"
            ):
                raise TemplateSyntaxError(
                    (
                        "Invalid syntax for markdown attribute - got "
                        "'{}', should be name=\"value\"".format(
                            "".join([str(t.value) for t in gathered[i : i + 3]]),
                        )
                    ),
                    lineno,
                )
            attrs[gathered[i].value] = gathered[i + 2].value
```
This did the trick! At the end of that block, `attrs` is a dictionary of all of the `key="value"` attributes that were included in that open tag.

## Validating the attributes

For my particular template tag, I only wanted three optional attributes to be supported. I added some code to validate them (and handle their slightly weird custom syntax):

```python
        # Validate the attributes
        kwargs = {}
        for attr, value in attrs.items():
            if attr in ("extensions", "extra_tags"):
                kwargs[attr] = value.split()
            elif attr == "extra_attrs":
                # Custom syntax: tag:attr1,attr2 tag2:attr3,attr4
                extra_attrs = {}
                for tag_attrs in value.split():
                    tag, attrs = tag_attrs.split(":")
                    extra_attrs[tag] = attrs.split(",")
                kwargs["extra_attrs"] = extra_attrs
            else:
                raise TemplateSyntaxError("Unknown attribute '{}'".format(attr), lineno)
```
Raising `TemplateSyntaxError` is a clean way to report errors in Jinja - and you pass the current template `lineno` to that exception to ensure it is reported back to the user.

## Passing attributes to the render method

At the end of this block I had `kwargs`, ready to be passed to my own `render_template(value, **kwargs)` function.

But there was one last problem: I needed to call this code:

```python
return nodes.CallBlock(
    self.call_method("_render_markdown"),
    [],
    [],
    body,
).set_lineno(lineno)
```
While passing through the `kwargs` I had collected to that `_render_markdown()` method.

I eventually found a pattern that worked, but it's kind of gross:

```python
        body = parser.parse_statements(["name:endmarkdown"], drop_needle=True)

        return nodes.CallBlock(
            # I couldn't figure out how to send attrs to the _render_markdown
            # method other than json.dumps and then passing as a nodes.Const
            self.call_method("_render_markdown", [nodes.Const(json.dumps(kwargs))]),
            [],
            [],
            body,
        ).set_lineno(lineno)

    async def _render_markdown(self, kwargs_json, caller):
        kwargs = json.loads(kwargs_json)
        return render_markdown(await caller(), **kwargs)
```

I'm serializing the `kwargs` dictionary to a JSON string, then wrapping that in `nodes.Const()`. I can then pass that as a list to the `.call_method()` method call.

Anything passed in that list becomes available to that `_render_markdown()` method as a positional argument - so I can take `kwargs` and `json.loads()` it to get the data back.

I don't know why I had to do it this way, and I'd be delighted to find a cleaner mechanism for this - but it does work.

## The finished code

You can see the finished code [here](https://github.com/simonw/datasette-render-markdown/blob/2.2/datasette_render_markdown/__init__.py#L101-L176C41) in the `datasette-render-markdown` GitHub repository.
