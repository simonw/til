# Allowing a container in Docker Desktop for Mac to talk to a PostgreSQL server on the host machine

I like using [Postgres.app](https://postgresapp.com/) to run PostgreSQL on my macOS laptop. I use it for a bunch of different projects.

When I deploy applications to Fly.io I build them as Docker containers and inject the Fly PostgreSQL database details as a `DATABASE_URL` environment variable.

In order to test those containers on my laptop, I needed to figure out a way to set a `DATABASE_URL` that would point to the PostgreSQL I have running on my own laptop - so that I didn't need to spin up another PostgreSQL Docker container just for testing purposes.

## host.docker.internal

The first thing to know is that Docker for Desktop sets `host.docker.internal` as a magic hostname inside the container that refers back to the IP address of the host machine.

So ideally something like this should work:

    docker run --env DATABASE_URL="postgres://docker:docker-password@host.docker.internal:5432/pillarpointstewards" \
       -p 8080:8000 pillarpointstewards

I'm using `-p 8080:8000` here to set port 8080 on my laptop to forward to the Django application server running on port 8000 inside the container.

## Creating the account and granting permissions

To create that PostgreSQL account with username `docker` and password `docker-password` (but pick a better password than that) I used Postico to open a connection to my `postgres` database and ran the following:

    create role docker login password 'docker-password';

Then I connected to my application database (in this case `pillarpointstewards`) and ran the following to grant permissions to that user:
```sql
GRANT ALL ON ALL TABLES IN SCHEMA "public" TO docker;
```
Having done this, the container run with the above `DATABASE_URL` environment variable was able to both connect to the server and run Django migrations too.
