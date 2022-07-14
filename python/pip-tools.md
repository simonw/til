# Freezing requirements with pip-tools

I tried [pip-tools](https://github.com/jazzband/pip-tools) for the first time today to pin the requirements for the [natbat/pillarpointstewards](https://github.com/natbat/pillarpointstewards) Django app.

The [pip-tools README](https://github.com/jazzband/pip-tools/blob/master/README.rst) is really good. Here's how I'm using it.

## Create a requirements.in

The `requirements.in` file contains your un-pinned requirements. Mine ended up looking like this:
```
Django~=4.0
gunicorn
whitenoise
psycopg2-binary
dj-database-url
pytest-django
django-extensions
django-htmx
pytz
bs4
httpx
sentry-sdk
pytest-httpx
ics==0.7
```
`Django~=4.0` means version Django 4.0 or higher, but less than 4.1. I pinned it like this because I saw a warning from `django-extensions`:

> `django.utils.deprecation.RemovedInDjango41Warning: 'django_extensions' defines default_app_config = 'django_extensions.apps.DjangoExtensionsConfig'.`

I'm pinning `ics` to the exact version 0.7 due to a broken test I experienced with more recent versions.

## Compiling requirements.txt from requirements.in

The `pip-compile` command runs against a `requirements.in` file and writes `requirements.txt` in the current directory with pinned versions of the packages.

You have to `pip install pip-tools` first to get that command.

I ran it like this:

    pip-compile --upgrade --generate-hashes requirements.in

The `--upgrade` option here causes it to check PyPI for the maximum version of each package that matches the lines in `requirements.in` - without this it may settle for packages that are currently in your local cache.

`--generate-hashes` adds hashes to the generated file, as a security measure.

I then committed both `requirements.in` and `requirements.txt` to the repo.

Here's the generated [requirements.txt](https://github.com/natbat/pillarpointstewards/blob/ff2a8aa14a41e548f37d61312dc3c6f0036aa73c/requirements.txt).

## Updating requirements locally with pip-sync

The other tool installed by `pip-tools` is `pip-sync`. It's useful for keeping your local development environment updated with the exact packages from `requirements.txt`.

Run it like this:

    pip-sync

It will uninstall and reinstall packages in your virtual environment until they exactly match `requirements.txt`.
