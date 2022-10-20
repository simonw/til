# Adding a Datasette ASGI app to Django

[Datasette](https://datasette.io/) is implemented as an ASGI application.

Django can be [run and deployed using ASGI](https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/).

At the [DjangoCon Sprints](https://2022.djangocon.us/schedule/#Day-Sprints1) this morning I figured out how to run Datasette inside a Django application, talking to the same SQLite databases as Django itself.

## Installing Datasette

Run this in the same environment as your Django application (or add it to `requirements.txt` or similar):

    pip install datasette

## Adding it to asgi.py

Django projects have an `asgi.py` module automatically generated for them when the project is created.

Replace its content with the following (careful to replace `my_django_application.settings` with the correct value):

```python
from datasette.app import Datasette
from django.core.asgi import get_asgi_application
from django.db import connections
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_django_application.settings")


datasette_application = Datasette(
    [
        str(db["NAME"])
        for db in connections.databases.values()
        if db["ENGINE"] == "django.db.backends.sqlite3"
    ],
    settings={
        "base_url": "/datasette/",
    },
).app()
django_application = get_asgi_application()


async def application(scope, receive, send):
    if scope["type"] == "http" and scope.get("path").startswith("/datasette/"):
        await datasette_application(scope, receive, send)
    else:
        await django_application(scope, receive, send)
```

Prior to this change, the file contained `application = get_asgi_application()`. `application` is the ASGI application that will be served.

This code replaces that with a tiny ASGI app that looks at the incoming `scope["path"]` and, if it starts with `/datasette/`, sends it to the Djatasette ASGI application. All other requests are sent to Django.

The `Datasette()` constructor at the start finds all SQLite databases that have been configured for Django, extracts their file path (`db["NAME"]` is a path object for SQLite databases) and passes that to the Datasette constructor.

It also sets `base_url` to `/datasette/` so that Datasette will know how to generate correct URLs when it is mounted at that path, as opposed to the root `/` path of the server.

## Running it with Uvicorn

Since this is an ASGI app, running `./manage.py runserver` will no longer do the right thing.

Instead, you need to install and use an ASGI server to run Django.

I like [Uvicorn](https://www.uvicorn.org/) for this.

Install it with `pip install uvicorn`, then start a local Django server running with:

    uvicorn my_django_application.asgi:application

Add `--reload` to cause it to automatically reload any time a file on disk is changed:

    uvicorn my_django_application.asgi:application --reload

## Using Datasette

With this in place, browsing to `http://127.0.0.1:8000/datasette/` will provide a Datasette interface for running read-only queries against your Django SQLite databases.
