# Enabling WAL mode for SQLite database files

I was getting occasional `Error: database is locked` messages from a Datasette instance that was running against a bunch of different SQLite files that were updated by cron scripts (my personal [Dogsheep](https://dogsheep.github.io/)).

I had read about SQLite's WAL mode but never fully understood how it works. I asked [some clarifying questions](https://sqlite.org/forum/forumpost/e6c238e854) on the SQLite forum and learned that WAL is actually a property of the database file itself, not of the connection to that database.

This means that turning on WAL is a thing you can do directly to a database file!

Here's the incantation:

    sqlite3 github.db 'PRAGMA journal_mode=WAL;'

I ran this against all of the `*.db` files in a directory like this:

    ls *.db | while read filename;
      do sqlite3 $filename 'PRAGMA journal_mode=WAL;';
    done;

The first time I ran this it worked on all but one file, which showed the `Error: database is locked` message - so I kept trying against that file until it worked.

After running this each `.db` file has an accompanying `.db-shm` and `.db-wal` file. So far I've not seen the "database is locked" message, so I think it had the desired effect.

## Turning WAL mode off again

If you want to turn WAL mode off and go back to the SQLite default, the unintuitive way to do that is:

    PRAGMA journal_mode=delete;

## Using sqlite-utils

I added a command to [sqlite-utils 2.15](https://sqlite-utils.datasette.io/en/stable/changelog.html#v2-15) that does this:

    sqlite-utils enable-wal *.db

The `disable-Wal` command disables it again.

## Futher notes

Ben Johnson wrote about how WAL mode internals work in great detail in [How SQLite Scales Read Concurrency ](https://fly.io/blog/sqlite-internals-wal/).

In a Hacker News comment, Ben [points out](https://news.ycombinator.com/item?id=32581486):

>  The other odd thing is that the journal_mode is only persistent for WAL, I believe. The DELETE, TRUNCATE, & PERSIST modes are per-connection. It makes sense though since those 3 modes deal with the rollback journal and are compatible with each other while the WAL is totally separate. https://www.sqlite.org/pragma.html#pragma_journal_mode
