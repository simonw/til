# Compiling the SQLite spellfix.c module on macOS

I wanted to browse a backup copy of my Plex database, which is a SQLite file. I tried this:

```
$ datasette databaseBackup.db94acbe6d-7442-4361-9663-61f1e97fe930
Usage: datasette serve [OPTIONS] [FILES]...

Error: Connection to databaseBackup.db94acbe6d-7442-4361-9663-61f1e97fe930 failed check: no such module: spellfix1
```
The `spellfix1` module is an optional module for SQLite. It's not shipped as part of the SQLite amalgamation distribution, so you have to compile it separately.

Here's how I did that.

I needed to know my SQLite version, in order to download the correct C module:

```
$ sqlite3 --version
3.28.0 2019-04-15 14:49:49 378230ae7f4b721c8b8d83c8ceb891449685cd23b1702a57841f1be40b5daapl
```
Now I need the source code for `spellfix.c` for that version. I navigated to https://github.com/sqlite/sqlite/blob/master/ext/misc/spellfix.c and then selected the `version-3.28.0` tag from the tag dropdown. This gave me the following page:

https://github.com/sqlite/sqlite/blob/version-3.28.0/ext/misc/spellfix.c

I downloaded the code using the "Raw" link:

```
cd /tmp
wget 'https://raw.githubusercontent.com/sqlite/sqlite/version-3.28.0/ext/misc/spellfix.c'
```
Next step - compile it:

```
gcc -I. -g -fPIC -shared spellfix.c -o spellfix.so
```
The `spellfix.so` module can now be used with Datasette like this:
```
datasette databaseBackup.db94acbe6d-7442-4361-9663-61f1e97fe930 --load-extension=spellfix.so
```
