# Using heroku pg:pull to restore a backup to a macOS laptop

Today I worked out how to use the Heroku `pg:pull` command and [Postgres.app](https://postgresapp.com/) to pull a Heroku backup to my laptop.

## Postgres.app

Postgres.app is the easiest way I know to run a PostgreSQL server on macOS: just install using the installer, then click the "Initialize" button in the UI.

## pg:pull

Assuming you have the Heroku CLI installed, the `heroku pg:pull` command can pull a Heroku database backup and load it into a local database.

https://devcenter.heroku.com/articles/heroku-postgresql#pg-push-and-pg-pull tells you that you need the following:

    heroku pg:pull HEROKU_POSTGRESQL_MAGENTA mylocaldb --app sushi

The app name is your app name (whatever comes before `.herokuapp.com`). 

I found my all-caps environment variable by running the following:

    heroku run env -a simonwillisonblog | grep POSTGRESQL
    Running env on simonwillisonblog... up, run.2963 (Hobby)
    HEROKU_POSTGRESQL_JADE_URL=postgres://....

Then I ran this command:

    heroku pg:pull HEROKU_POSTGRESQL_JADE_URL simonwillisonblog -a simonwillisonblog

This created a local PostgreSQL database called `simonwillisonblog` and imported my latest backup.

When I ran it a second time I had to use `dropdb simonwillisonblog` first to drop the existing local database.
