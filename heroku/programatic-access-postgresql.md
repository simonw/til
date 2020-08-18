# Programatically accessing Heroku PostgreSQL from GitHub Actions

My [db-to-sqlite](https://github.com/simonw/db-to-sqlite) tool can connect to a PostgreSQL database, export all of the content and write it to a SQLite database file on disk.

I wanted to use it in a GitHub Action - but that meant I needed code running in the action workflow to be able to access my Heroku PostgreSQL database directly.

It turns out the `DATABASE_URL` environment variable in Heroku has everything you need to connect to that database from elsewhere.

If you have the `heroku` CLU tool installed and authenticated the following one-liner does the job:

    db-to-sqlite $(heroku config:get DATABASE_URL -a simonwillisonblog) simonwillisonblog.db

To configure `heroku` in a GitHub Action you need to set a `HEROKU_API_KEY` environment variable.

You can create an OAuth token on your laptop like this:

    % heroku authorizations:create --scope=read-protected 
    Creating OAuth Authorization... done
    Client:      <none>
    ID:          4dd42e6c-5c89-4389-a9b1-4a5388b88517
    Description: Long-lived user authorization
    Scope:       read-protected
    Token:       xxx copy and paste this bit xxx

Then you can paste the token into a GitHub repository secret called `HEROKU_API_KEY`.

Here's a fragment of my action workflow that creates the SQLite database pulling data from Heroku:

```yaml
    - name: Import Heroku DB into SQLite
      env:
        HEROKU_API_KEY: ${{ secrets.HEROKU_API_KEY }}
      run: |-
        db-to-sqlite $(heroku config:get DATABASE_URL -a simonwillisonblog) simonwillisonblog.db \
          --table auth_permission \
          --table auth_user \
          --table blog_blogmark \
          --table blog_blogmark_tags \
          --table blog_entry \
          --table blog_entry_tags \
          --table blog_quotation \
          --table blog_quotation_tags \
          --table blog_tag \
          --table django_content_type \
          --table redirects_redirect
```
