# Granting a PostgreSQL user read-only access to some tables

I wanted to grant a PostgreSQL user (or role) read-only access to a specific list of tables.

I created the role using the Heroku PostgreSQL web console. Having done that, it had the name `read-only-core-tables`.

I attached it to my Heroku application using the web console, then I ran the following to get myself a default-permission terminal session:

    % heroku pg:psql postgresql-metric-59331 --app myapp

As the default user I ran the following:

```sql
GRANT USAGE ON SCHEMA PUBLIC TO "read-only-core-tables";
```

This grants that user the ability to see what tables exist - after running this the `\dt` command for that user started showing a full list of tables.

But... `select * from table` returned permission denied for every table. To allow select access I ran this:

```sql
GRANT SELECT ON TABLE
    public.availability_tag,
    public.county,
    public.django_content_type,
    public.django_migrations
TO "read-only-core-tables";
```
That's all it took - my read-only user was then able to run `select * from county` and see the results - but attempts to select against tables not in that allow-list were denied.
