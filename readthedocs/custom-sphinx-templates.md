# Using custom Sphinx templates on Read the Docs

I wanted to make a small customization to one of my documentation templates on Read the Docs.

It turns out you can over-ride the default templates by creating a `_templates` directory in your documentation folder and dropping new files into it - no additional configuration changes required.

I wanted to customize a small part of the `layout.html` template. The original template is here: https://github.com/simonw/sphinx_rtd_theme/blob/master/sphinx_rtd_theme/layout.html

It has named blocks in it, which means I can over-ride just the specific named block I'm interested in. I created my own `{% block sidebartitle %}` block, then saved it in a file in `_templates/layout.html`.

To inherit from the default layout template, I used `{% extends "!layout.html" %}` - note the `!` there which causes it to use the default template (without that character the build script throws an infinite recursion error).

Here's the `layout.html` template I used:
```html+jinja
{%- extends "!layout.html" %}

{% block sidebartitle %}

<a href="https://datasette.io/">
  <img src="{{ pathto('_static/' + logo, 1) }}" class="logo" alt="{{ _('Logo') }}"/>
</a>

{% if theme_display_version %}
  {%- set nav_version = version %}
  {% if READTHEDOCS and current_version %}
    {%- set nav_version = current_version %}
  {% endif %}
  {% if nav_version %}
    <div class="version">
      {{ nav_version }}
    </div>
  {% endif %}
{% endif %}

{% include "searchbox.html" %}

{% endblock %}
```
See https://github.com/simonw/datasette/tree/main/docs for the full documentation layout - the only thing I had to change to get this custom template was adding the new `_templates` folder and the `layout.html` file.
