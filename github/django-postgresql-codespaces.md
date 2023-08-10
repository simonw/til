# Running a Django and PostgreSQL development environment in GitHub Codespaces

Helping people setup development environments (and fix them when they break) can be incredibly frustrating. I'm really excited about cloud-based development environments such as [GitHub Codespaces](https://github.com/features/codespaces) for exactly this reason - I love the idea that you can get a working environment by clicking a green button, and if it breaks you can throw it away and click the button again to get a brand new one.

Today I figured out how to run a full Django + PostgreSQL development environment in GitHub Codespaces, configured so anyone else who creates a Codespace from that repository will get a working environment.

## The .devcontainer directory

The key to this is three files in the `.devcontainer` directory of the repository:

- `devcontainer.json` provides the overall configuration
- `Dockerfile` defines the Docker image that will be used to create the main container for the Codespace
- `docker-compose.yml` defines the Docker Compose services that will be run - this is necessary to get a separate PostgreSQL database container going

You can see them in [my project's .devcontainer directory here](https://github.com/natbat/pillarpointstewards/tree/6c26cfd4c9a21539dbddf70a780e652b51d44ab7/.devcontainer).

Here's what those files look like:

## devcontainer.json

This is the most complex file. Here's what I ended up with for a classic Django app:

```json
{
  "dockerComposeFile": "docker-compose.yml",
  "service": "app",
  "waitFor": "onCreateCommand",
  "updateContentCommand": "",
  "postCreateCommand": "pip install --user -r requirements.txt && python manage.py collectstatic && python manage.py migrate",
  "postAttachCommand": {
    "server": "python manage.py runserver"
  },
  "containerEnv": {
    "DATABASE_URL": "postgres://postgres:postgres@db/pillarpointstewards"
  },
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python"
      ]
    }
  },
  "portsAttributes": {
    "8000": {
      "label": "Application",
      "onAutoForward": "openPreview"
    }
  },
  "forwardPorts": [8000]
}
```
This references the `docker-compose.yml` file that we will define next, and specifies that the main service is the thing in that file that's defined in the `app` block.

I haven't completely figured out the different commands, but the above recipe worked for me - where the `postCreateCommand` installs dependencies and runs migrations, and the `postAttachCommand` starts a development server.

Here's that `postCreateCommand` in full:

```bash
pip install --user -r requirements.txt \
  && python manage.py collectstatic \
  && python manage.py migrate
```
I'm installing requirements, running `collectstatic` (needed for my project that uses whitenoise) and then running migrations.

The `containerEnv` key holds environment variables. I'm telling it where to find PostgreSQL - my `settings.py` file then uses [dj_database_url](https://pypi.org/project/dj-database-url/) like this:

```python
import dj_database_url

DATABASES = {}
DATABASES["default"] = dj_database_url.config()
```
The `customizations` key says that I want the VS Code Python extension.

The `portsAttributes` and `forwardPorts` pieces ensure port 8000 will be forwarded and made available for a browser tab inside the Codespaces environment.

## docker-compose.yml

This file exists to ensure the PostgreSQL server is running:

```yaml
version: '3.8'

services:
  app:
    build:
      context: ..
      dockerfile: .devcontainer/Dockerfile

    volumes:
      - ../..:/workspaces:cached

    command: sleep infinity
    network_mode: service:db

  db:
    image: postgres:latest
    restart: unless-stopped
    volumes:
      - postgres-data:/var/lib/postgresql/data
    environment:
      POSTGRES_USER: postgres
      POSTGRES_DB: pillarpointstewards
      POSTGRES_PASSWORD: postgres

volumes:
  postgres-data:
```
I figured this out by copying examples from various GitHub searches. It seems to work OK.

Note that setting `POSTGRES_DB` to `pillarpointstewards` caused a database of that name to be created when the server started.

## Dockerfile

This one is really simple:

```dockerfile
FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

ENV PYTHONUNBUFFERED 1
```
I can't remember where I found this example. It also included this comment:

```dockerfile
# [Optional] If your requirements rarely change, uncomment this section to add them to the image.
# COPY requirements.txt /tmp/pip-tmp/
# RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
#    && rm -rf /tmp/pip-tmp

# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>
```
## Running Codespaces

With this `.devcontainer/` directory setup for a repository, starting a Codespace for it can be done from the green Code button menu:

<img width="458" alt="That menu opens an area with a big green Create codespace on main button" src="https://github.com/simonw/til/assets/9599/bb227223-33b5-4abb-83f0-63679017bb5e">

Clicking that button will churn away for about a minute building and launching the container, then drop into a VS Code like environment running in your browser where it will churn away for a few more minutes running the various setup commands.

<img width="704" alt="Setting up your codespace window, showing the output of build logs" src="https://github.com/simonw/til/assets/9599/c01d0559-4a2f-44fe-88e9-b5619eda31f0">

Once it's finished starting up, there should be a Django development server running. To view that in your browser, click on the "Ports" tab and then hover over the development server and click the little globe icon:

![The ports tab shows available ports, with their local addresses](https://user-images.githubusercontent.com/9599/259881100-eb9fac27-ab36-458a-a87c-09857aac4b50.png)

This should open a new browser window that exposes the port-forwarded development server.
