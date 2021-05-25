# Docker Compose for Django development

I had to get Docker Compose working for a Django project, primarily to make it easier for other developers to get a working development environment.

Some features of this project:

- Uses GeoDjango, so needs GDAL etc for the Django app plus a PostgreSQL server running PostGIS
- Already has a `Dockerfile` used for the production deployment, but needed a separate one for the development environment
- Makes extensive use of Django migrations (over 100 and counting)

I ended up with this `docker-compose.yml` file in the root of the project:

```yaml
version: "3.1"

services:
  database:
    image: postgis/postgis:13-3.1
    restart: always
    expose:
      - "5432"
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_DB: mydb
      POSTGRES_PASSWORD: postgres
  web:
    container_name: myapp
    build:
      context: .
      dockerfile: Dockerfile.dev
    command: python manage.py runserver 0.0.0.0:3000
    environment:
      DATABASE_URL: postgres://postgres:postgres@database:5432/mydb
      DEBUG: 1
    volumes:
      - .:/app
    ports:
      - "3000:3000"
    depends_on:
      - migrations
      - database
  migrations:
    build:
      context: .
      dockerfile: Dockerfile.dev
    command: python manage.py migrate --noinput
    environment:
      DATABASE_URL: postgres://postgres:postgres@database:5432/mydb
    volumes:
      - .:/app
    depends_on:
      - database
```
The `db` container runs PostGIS. The `web` container runs the Django development server, built using the custom `Dockerfile.dev` Dockerfile. The `migrations` container simply runs the apps migrations and then terminates - with `depends_on` used to ensure that migrations run after the hdatabase server starts and before the web server.

The `container_name: myapp` field on the `web` container is a convenience which means you can later run commands like this:

    docker exec -it myapp ./manage.py collectstatic

Here's `Dockerfile.dev`:

```dockerfile
FROM python:3.9-slim

ENV APP_HOME /app
WORKDIR $APP_HOME

ENV PYTHONUNBUFFERED 1

# gdal for GeoDjango
RUN apt-get update && apt-get install -y \
    binutils \
    gdal-bin \
    libproj-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR $APP_HOME/myapp

RUN ./manage.py collectstatic --no-input

CMD python manage.py runserver 0.0.0.0:3000
```
