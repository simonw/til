# Upgrade Postgres.app on macOS

I've been using [Postgres.app](https://postgresapp.com/) to run PostgreSQL on my Mac for years. I like that it's easy to install, gives me a task tray icon to control it and means I don't have to run a full Docker environment just to hack on projects like [my blog](https://github.com/simonw/simonwillisonblog).

I want to try out the PostgreSQL vector extension, since it's now supported by Heroku PostgreSQL. Postgres.app [added support for that extension](https://github.com/PostgresApp/PostgresApp/issues/716) last year, but I need to upgrade my installation to get it.

This also meant migrating from PostgreSQL 15 to PostgreSQL 16. I didn't want to lose my existing data (even though it's just for development environments), so I dug around and [found their documentation](https://postgresapp.com/documentation/migrating-data.html) on migrating.

Here's what I did:

1. Dump _all_ of my development databases using `pg_dumpall`. This wasn't on my `$PATH` so I ran it like this:

    ```bash
    /Applications/Postgres.app/Contents/Versions/15/bin/pg_dumpall > ~/tmp/all-databases.sql
    ```

2. Stop the Postgres.app server. I quit it from the task tray icon but to my surprise this didn't seem to stop the server itself, so I ran `ps aux | grep postgres` and killed the main process manually using `kill PID`.

3. Delete the `/Applications/Postgres.app` directory.

4. Download and install the latest [Universal Postgres.app](https://postgresapp.com/downloads.html).

5. Start that app running, then click the "Initialize" button to initialize the filesystem for the new PostgreSQL 16 database.

6. Restore all of my databases using the `psql` command line tool like this:

    ```bash
    cat /tmpl/all.sql | /Applications/Postgres.app/Contents/Versions/16/bin/psql
    ```
