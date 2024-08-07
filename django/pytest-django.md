# Using pytest-django with a reusable Django application

I published a reusable Django application today: **[django-http-debug](https://github.com/simonw/django-http-debug)**, which lets you define mock HTTP endpoints using the Django admin - like `/webhook-debug/` for example, configure what they should return and view detailed logs of every request they receive.

Since it's a resuable app, you can add it to any Django project like so:

```bash
pip install django-http-debug
```
Then add the following to `INSTALLED_APPS` in your Django settings:
```python
INSTALLED_APPS = [
    # ...
    'django_http_debug',
    # ...
]
```
Add this to `MIDDLEWARE`:
```python
MIDDLEWARE = [
    # ...
    "django_http_debug.middleware.DebugMiddleware",
    # ...
]
```
And run `./manage.py migrate` to create the necessary database tables.

I used Claude 3.5 Sonnet to build most of this project ([prompts in this issue](https://github.com/simonw/django-http-debug/issues/1)) and then did that again via [LLM](https://llm.datasette.io/) to have it help me write the tests ([full dialog](https://gist.github.com/simonw/a1c51e3a4f30d91eac4664ba84266ca1)). I then poked around with the tests until I got them to work. Here's what I learned about using [pytest-django](https://pytest-django.readthedocs.io/) in the context of a reusable Django application.

## Basic test project structure

My reusable app had the following directory structure inside `django-http-debug` - initially created using my [python-lib](https://github.com/simonw/python-lib) cookiecutter template, then I added the Django `models.py` and `views.py` and suchlike:

```
pyproject.toml
README.md
LICENSE
django_http_debug/__init__.py
django_http_debug/models.py
django_http_debug/views.py
django_http_debug/middleware.py
django_http_debug/admin.py
django_http_debug/migrations/__init__.py
django_http_debug/migrations/0001_initial.py
```
I like `pytest`, which encourages adding tests in a dedicated `tests/` directory.

My `pyproject.toml` file ended up looking like this, after I added both `pytest` and `pytest-django` as test dependencies:

```toml
[project]
name = "django-http-debug"
version = "0.2"
description = "Django app for creating database-backed HTTP debug endpoints"
readme = "README.md"
requires-python = ">=3.8"
authors = [{name = "Simon Willison"}]
license = {text = "Apache-2.0"}
classifiers = [
    "License :: OSI Approved :: Apache Software License"
]
dependencies = [
    "filetype",
    "django"
]

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project.urls]
Homepage = "https://github.com/simonw/django-http-debug"
Changelog = "https://github.com/simonw/django-http-debug/releases"
Issues = "https://github.com/simonw/django-http-debug/issues"
CI = "https://github.com/simonw/django-http-debug/actions"

[project.optional-dependencies]
test = ["pytest", "pytest-django"]
```
I could then install everything into a virtual environment for my project folder like so:
```bash
pip install -e '.[test]'
```
The big challenge here is that Django apps need a fully configured Django project in which to execute! With more help from Claude I created the following structure:

```
tests/test_django_http_debug.py
tests/test_project/__init__.py
tests/test_project/settings.py
tests/test_project/urls.py
```
That `settings.py` file ended up looking like this, after I removed as much stuff from it as possible (the main goal is to test my new middleware):
```python
SECRET_KEY = "django-insecure-test-key"
DEBUG = True
ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    # "django.contrib.sessions",
    # "django.contrib.messages",
    # "django.contrib.staticfiles",
    "django_http_debug",
]

MIDDLEWARE = [
    "django_http_debug.middleware.DebugMiddleware",
]

ROOT_URLCONF = "tests.test_project.urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

USE_TZ = True
```
And `urls.py` contained this:
```python
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
```

## Implementing the tests

Here's the first of the tests in `tests/test_django_http_debug.py` - the rest [are here](https://github.com/simonw/django-http-debug/blob/a0103538d486cca04449a357f8dae0dc3da0573e/tests/test_django_http_debug.py):

```python
import pytest
from django_http_debug.models import DebugEndpoint, RequestLog
from django.test.client import Client


@pytest.mark.django_db
def test_debug_view():
    assert Client().get("/test/endpoint").status_code == 404
    DebugEndpoint.objects.create(
        path="test/endpoint",
        status_code=200,
        content="Test content",
        content_type="text/plain",
    )
    response = Client().get("/test/endpoint")
    assert response.status_code == 200
    assert response.content == b"Test content"
    assert response["Content-Type"] == "text/plain"
```
This uses `@pytest.mark.django_db` to ensure the Django databsae is configured (and then cleared) for that test. It uses the Django test client to exercise an endpoint, and the Django ORM to populate the database.

## Configuring django-pytest

The part that took the longest was figuring out how to make it so that when `pytest` ran it could find my `test_project` Django project.

I saw this error a lot:

`django.core.exceptions.ImproperlyConfigured: Requested setting INSTALLED_APPS, but settings are not configured. You must either define the environment variable DJANGO_SETTINGS_MODULE or call settings.configure() before accessing settings.`

Eventually I figured out the recipe to fix that. I added the following to my `pyproject.toml` file:

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "tests.test_project.settings"
pythonpath = ["."]
```
The `pythonpath` line tells `pytest` to add the current directory to the Python path before running. Then the `DJANGO_SETTINGS_MODULE` variable tells it where to find the test project.

Here's the [relevant pytest-django documentation](https://pytest-django.readthedocs.io/en/latest/managing_python_path.html).

## Running the tests

This all worked! Now when I run `pytest` in my root folder I see the following:

```
======================== test session starts =========================
platform darwin -- Python 3.10.10, pytest-8.3.2, pluggy-1.5.0
django: version: 5.1, settings: tests.test_project.settings (from ini)
rootdir: /Users/simon/Dropbox/Development/django-http-debug
configfile: pyproject.toml
plugins: django-4.8.0
collected 5 items                                                    

tests/test_django_http_debug.py .....                          [100%]

========================= 5 passed in 0.10s ==========================
```
