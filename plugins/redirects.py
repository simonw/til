from datasette import hookimpl
from datasette.utils.asgi import Response


@hookimpl
def register_routes():
    return (
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
