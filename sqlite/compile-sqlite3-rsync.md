# Compiling and running sqlite3-rsync

Today I heard about the [sqlite3-rsync](https://sqlite.org/draft/rsync.html) command, currently available in a branch in the SQLite code repository. It provides a mechanism for efficiently creating or updating a copy of a SQLite database that is running in WAL mode, either locally or via SSH to another server.

**Update:** Thanks to [gary_0 on Hacker News](https://news.ycombinator.com/item?id=41749288#41760082) here's a MUCH simpler recipe:

```bash
git clone https://github.com/sqlite/sqlite.git
cd sqlite
./configure
make sqlite3_rsync
```
So it looks like the `sqlite-rsync` command is no longer limited to a branch.

## How I compiled it without using make sqlite3-rsync

After some poking around (and some hints from Claude) I found a recipe for compiling and running it that seems to work:

```bash
cd /tmp
git clone https://github.com/sqlite/sqlite.git
cd sqlite
git checkout sqlite3-rsync
./configure
make sqlite3.c
cd tool
gcc -o sqlite3-rsync sqlite3-rsync.c ../sqlite3.c -DSQLITE_ENABLE_DBPAGE_VTAB
./sqlite3-rsync --help
```
Here I'm cloning from the [GitHub mirror](https://github.com/sqlite/sqlite.git) of the [SQLite Fossil repo](https://sqlite.org/src/doc/trunk/README.md), purely to save myself from learning how to use Fossil.

The first step is to run `./configure` and then `make sqlite3.c` in the root directory. This creates the SQLite amalgamation file - a single C file containing the full implementation of SQLite, which I can then use as part of compiling the `sqlite3-rsync` tool.

It took me quite a few iterations to get to this recipe for compiling the tool itself:
```bash
gcc -o sqlite3-rsync sqlite3-rsync.c ../sqlite3.c -DSQLITE_ENABLE_DBPAGE_VTAB
```
The `-DSQLITE_ENABLE_DBPAGE_VTAB` flag is necessary to enable the `dbpage` virtual table, which is used by the `sqlite3-rsync` tool. Without that I got this error when trying to run it:

> `ERROR: unable to prepare SQL [SELECT hash(data) FROM sqlite_dbpage WHERE pgno<=min(1,7338) ORDER BY pgno]: no such table: sqlite_dbpage`

## Trying out sqlite-rsync

Having compiled the utility I tested it out like this:

```bash
curl https://datasette.io/content.db -o /tmp/content.db
# Enable WAL mode
sqlite3 /tmp/content.db "PRAGMA journal_mode=WAL"
# And run the copy
./sqlite3-rsync /tmp/content.db /tmp/content-copy.db
```
Then I made a change to `/tmp/content.db`:

```bash
sqlite3 /tmp/content.db 'create table test (id integer primary key)'
```
Confirmed it was not present in `/tmp/content-copy.db`:

```bash
sqlite3 /tmp/content-copy.db '.tables'
```
And ran this command to sync them up again:
    
```bash
./sqlite3-rsync /tmp/content.db /tmp/content-copy.db
```
Which resulted in that new table being created in the copy:
    
```bash
sqlite3 /tmp/content-copy.db '.tables' | grep test
```

I haven't yet tried running the command over SSH: you first need to compile and deploy the `sqlite3-rsync` binary to the remote server and drop it somewhere on the path (the documentation suggests `/usr/local/bin`).

Having done that this should work:

```bash
sqlite3-rsync user@host:/path/to/remote.db /path/to/local-copy.db
```
