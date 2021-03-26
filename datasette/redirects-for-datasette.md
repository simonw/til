# Redirects for Datasette

I made some changes to my https://til.simonwillison.net/ site that resulted in cleaner URL designs, so I needed to setup some redirects. I configured the redirects using a one-off Datasette plugin called `redirects.py` which I dropped into the `plugins/` directory for the Datasette instance:

```python
from datasette import hookimpl
from datasette.utils.asgi import Response


@hookimpl
def register_routes():
    return (
        (r"^/til/til/(?P<topic>[^_]+)_(?P<slug>[^\.]+)\.md$", lambda request: Response.redirect(
            "/{topic}/{slug}".format(**request.url_vars), status=301
        )),
        ("^/til/feed.atom$", lambda: Response.redirect("/tils/feed.atom", status=301)),
        (
            "^/til/search$",
            lambda request: Response.redirect(
                "/tils/search"
                + (("?" + request.query_string) if request.query_string else ""),
                status=301,
            ),
        ),
    )
```
