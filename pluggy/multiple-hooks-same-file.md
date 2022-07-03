# Registering the same Pluggy hook multiple times in a single file

I found myself wanting to register more than one instance of a [Pluggy](https://pluggy.readthedocs.io/) plugin hook inside a single module.

Hooks are usually registered like this:

```python
@hookimpl
def filters_from_request(request, database, datasette):
    # ...
```
Where `filters_from_request` matches the name of a registered plugin hook.

It turns out you can do this instead:

```python
@hookimpl(specname="filters_from_request")
def filters_from_request_1(request, database, datasette):
    # ...

    
@hookimpl(specname="filters_from_request")
def filters_from_request_2(request, database, datasette):
    # ...
```
Which allows you to write more than one plugin implementation function in the same Python module file.

Note that the `specname` feature requires [Pluggy 1.0.0](https://github.com/pytest-dev/pluggy/blob/main/CHANGELOG.rst#pluggy-100-2021-08-25) or higher.

These can be combined with `tryfirst=` and `trylast=`. This example adds one link at the start of the Datasette application menu and one at the end, using the [menu_links hook](https://docs.datasette.io/en/stable/plugin_hooks.html#menu-links-datasette-actor-request).

```python
from datasette import hookimpl


@hookimpl(specname="menu_links", tryfirst=True)
def menu_links_1(datasette):
    return [
        {"href": datasette.urls.path("/"), "label": "Home"},
    ]


@hookimpl(specname="menu_links", trylast=True)
def menu_links_2():
    return [
        {
            "href": "http://www.example.com/",
            "label": "Link at the end",
        },
    ]
```
