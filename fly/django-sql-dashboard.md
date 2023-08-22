# Configuring Django SQL Dashboard for Fly PostgreSQL

I have a Fly application that uses their PostgreSQL service. I wanted to run [Django SQL Dashboard]() with a read-only user against that database.

Here's how I did it.

## Connect to psql on the Fly PostgreSQL service

The application running my Fly PostgreSQL database is called `my-app-postgresql`.

```bash
flyctl ssh console -a my-app-postgresql
```
This gives me a shell on the machine running PostgreSQL. I can then connect to the database with `psql`.

```bash
psql postgres://postgres@localhost
```
Then paste in the password (if you don't have your `postgres` password to hand, I spotted it in `ps aux`).

## Create a role with read-only permissions

I decided to create a role called `dashboardrole`. In PostgreSQL roles and users are technically the same thing - a user is really just a role that can be signed into with a password.

My PostgreSQL database schema here is called `appdatabase`.

I created a random password for my role first, which I used as `RANDOM_PASSWORD` in this script:

```sql
-- Create the role - will be read-only and have access to most tables
CREATE ROLE dashboardrole;
GRANT CONNECT ON DATABASE appdatabase TO dashboardrole;
```
I connected to the database, so the references to `public` coming up would refer to the right place:
```sql
\c appdatabase
```
Now to grant access to current and future tables in that schema:
```sql
-- Grant access to the schema and all tables
GRANT USAGE ON SCHEMA public TO dashboardrole;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO dashboardrole;
-- Grant access to future tables as well
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO dashboardrole;
```
Since I'm running a Django application I wanted to lock things down a little here. I revoked access entirely to the `django_session` table:
```sql
-- Revoke access to django_session
REVOKE SELECT ON TABLE django_session FROM dashboardrole;
```
I want to be able to join against the `auth_user` table, but I didn't want to make the password hashes visible to dashboard users. In PostgreSQL you can't subtract permissions, but you can revoke the entire table and then selectively add them back for the other columns:
```sql
-- Grant access to the auth_user table to just the columns we need
REVOKE SELECT ON auth_user FROM dashboardrole;
GRANT SELECT(
  id, last_login, is_superuser, username, first_name,
  last_name, email, is_staff, is_active, date_joined
) ON auth_user TO dashboardrole;
```
Finally I set a password so my `dashboardrole` could connect from Django with one:
```sql
-- Set a password for the role
ALTER ROLE dashboardrole WITH LOGIN PASSWORD 'RANDOM_PASSWORD';
```
I then exited `psql` and ran this to test the new role:
```sql
psql postgres://dashboardrole@localhost/datasettecloud -W
< PASTE RANDOM_PASSWORD >
```
I tried `select * from auth_user` and got an error, but `select id, username from auth_user` worked fine - as I had intended.

The last step was to construct a connection URL for Django. I used this:

## Set up the Django connection string

```
postgres://dashboardrole:RANDOM_PASSWORD@my-app-postgresql.internal/appdatabase
```
The rest of the configuration is described [in the Django SQL Dashboard documentation](https://django-sql-dashboard.datasette.io/en/stable/setup.html#configuring-the-dashboard-database-alias).

[More on Django SQL Dashboard](https://simonwillison.net/2021/Jul/6/django-sql-dashboard/).
