# Upgrading a Heroku PostgreSQL database with pg:copy

Figured this out in https://github.com/simonw/simonwillisonblog/issues/132 - I was running PostgreSQL 9.x and I wanted 11.x in order to use the new `search_type="websearch"` option in Django 3.1.

I followed the steps in [Upgrading with pg:copy](https://devcenter.heroku.com/articles/upgrading-heroku-postgres-databases#upgrading-with-pg-copy) (I don't have any database followers so the `pg:upgrade` route wasn't open to me).

Because I'm the only user who writes to my database I skipped the maintenance mode bit.

## Step one: provision a new DB

    $ heroku addons:create heroku-postgresql:hobby-basic -a simonwillisonblog
    Creating heroku-postgresql:hobby-basic on ⬢ simonwillisonblog... $9/month
    ▸    Release command executing: config vars set by this add-on will not be
    ▸    available until the command succeeds. Use `heroku releases:output` to view
    ▸    the log.
    Database has been created and is available
    ! This database is empty. If upgrading, you can transfer
    ! data from another database with pg:copy
    Created postgresql-animate-15868 as HEROKU_POSTGRESQL_JADE_URL
    Use heroku addons:docs heroku-postgresql to view documentation

## Step 2 skipped - I didn't bother with maintenance mode

## Step 3: copy the data to the new database

I had to wait for it to finish provisioning first:

```
heroku pg:wait -a simonwillisonblog
```
Then I used this command to figure out which `_URL` it had:
```
heroku config -a simonwillisonblog | grep URL
```
Which meant I could run the copy:
```
$ heroku pg:copy DATABASE_URL HEROKU_POSTGRESQL_JADE_URL --app simonwillisonblog
▸    WARNING: Destructive action
▸    This command will remove all data from JADE
▸    Data from DATABASE will then be transferred to JADE
▸    To proceed, type simonwillisonblog or re-run this command with --confirm simonwillisonblog

> simonwillisonblog
Starting copy of DATABASE to JADE... done
Copying... done
```

## Step 4: promote the new database
```
$ heroku pg:promote HEROKU_POSTGRESQL_JADE -a simonwillisonblog
Ensuring an alternate alias for existing DATABASE_URL... HEROKU_POSTGRESQL_OLIVE_URL
Promoting postgresql-animate-15868 to DATABASE_URL on ⬢ simonwillisonblog... done
Checking release phase... pg:promote succeeded. It is safe to ignore the failed Detach DATABASE (@ref:postgresql-contoured-66343) release.
```

## Step 5: deprovision the old database
```
% heroku addons:destroy HEROKU_POSTGRESQL_OLIVE -a simonwillisonblog
 ▸    WARNING: Destructive Action
 ▸    This command will affect the app simonwillisonblog
 ▸    To proceed, type simonwillisonblog or re-run this command with --confirm simonwillisonblog

> simonwillisonblog
Destroying postgresql-contoured-66343 on ⬢ simonwillisonblog... done
```
