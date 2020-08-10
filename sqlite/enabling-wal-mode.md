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
