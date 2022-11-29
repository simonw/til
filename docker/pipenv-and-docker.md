# Using pipenv and Docker

I had [a Django project](https://github.com/natbat/cbwg) that used `pipenv` (in particular a `Pipfile.lock`) to manage dependencies and I wanted to build a Docker container for it.

With the help of [this article](https://sourcery.ai/blog/python-docker/) (for the `PIPENV_VENV_IN_PROJECT` tip) I came up with the following:

```dockerfile
FROM python:3.6.15-slim-buster

RUN mkdir -p /app
WORKDIR /app

COPY . .

ENV PIPENV_VENV_IN_PROJECT=1

RUN pip install pipenv
RUN pipenv sync

RUN pipenv run ./manage.py collectstatic --noinput

EXPOSE 8000

CMD pipenv run gunicorn --bind 0.0.0.0:8000 --timeout 120 --workers 2 cbwg.wsgi
```

Ignore the base image - the project was an emergency port from Heroku and I didn't have time to upgrade it from the ancient version of Python it was using (if you're using a `Pipfile.lock` file you need to keep your Python version stable unless you want to lock new versions).

The key lines here are these ones:

```dockerfile
RUN mkdir -p /app
WORKDIR /app

COPY . .

ENV PIPENV_VENV_IN_PROJECT=1

RUN pip install pipenv
RUN pipenv sync
```
First we create a `/app` directory and set that as the working directory.

`COPY . .` copies ALL files and directories from the `Dockerfile` directory into the new image, inside `/app`.

`ENV PIPENV_VENV_IN_PROJECT=1` is important: it causes the resuling virtual environment to be created as `/app/.venv`. Without this the environment gets created somewhere surprising, such as `/root/.local/share/virtualenvs/app-4PlAip0Q` - which makes it much harder to write automation scripts later on.

Then we install `pipenv` and use `RUN pipenv sync` to install all of the package versions from our `Pipfile.lock` file (which was added by `COPY . .`).

## Alternative using pipenv sync --system

You can avoid creating a virtual environment in your Docker image entirely using `pipenv sync --system`, which instead installs the packages in the Docker container's system Python:

```dockerfile
FROM python:3.6.15-slim-buster

RUN mkdir -p /app
WORKDIR /app

COPY . .

RUN pip install pipenv
RUN pipenv sync --system

RUN ./manage.py collectstatic --noinput

EXPOSE 8000

CMD pipenv run gunicorn --bind 0.0.0.0:8000 --timeout 120 --workers 2 cbwg.wsgi
```

But this carries its own risks, as [described here by Hynek Schlawack](https://hynek.me/articles/virtualenv-lives/).

The key problem is that the operating system itself may have already installed specific package versions in `site-packages`, and there's a risk that these might conflict with the versions of those packages used by your own application.

So Hynek advises:

> Do isolate your application server’s OS from its host using Docker [...]
> But inside of them also do isolate your Python environment using virtualenv from unexpected surprises in the system site-packages.


