# Talking to a PostgreSQL service container from inside a Docker container

I have a Django application which uses PostgreSQL. I build the Django application into its own Docker container, push that built container to the GitHub package registery and then deploy that container to production.

I wanted to run the tests inside the container as part of the deployment process, to make sure the container that I build is ready to be deployed (via continuous deployment).

In production I'm using Digital Ocean PostgreSQL rather than running PostgreSQL in a container. For running the tests I decided to use GitHub's [PostgreSQL service containers](https://docs.github.com/en/actions/guides/creating-postgresql-service-containers) to run the tests.

But how do you set it up so tests running inside a Docker container can talk to the PostgreSQL service container provided by the GitHub Actions environment?

This took a while to figure out. The key insight was that Docker containers (at least on Linux) have a magic IP address, `172.17.0.1`, which can be used to access their host environment - and GitHub's PostgreSQL container is available to that host environment on localhost port 5432.

So here's the recipe I ended up using:

```yaml
name: Build, test and deploy

on:
  push:

jobs:
  build_test_deploy:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres
        env:
          POSTGRES_USER: postgres
          POSTGRES_DB: postgres
          POSTGRES_PASSWORD: postgres
        ports:
          - 5432:5432
        # Health checks to wait until postgres has started
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
    - uses: actions/checkout@v2
    - name: Build the tagged Docker image
      run: |-
        docker build -t my-tag .
    - name: Run tests
      run: |-
        docker run \
          -e DATABASE_URL="postgres://postgres:postgres@172.17.0.1:5432/postgres" \
          --entrypoint=/app/github-actions-runtests.sh \
          my-tag
```
My `github-actions-runtests.sh` file uses [django-pytest](https://pytest-django.readthedocs.io/) and looks like this:
```bash
#!/bin/bash
cd /app
pytest --ds=config.test_settings
```
