# Using pysqlite3 on macOS

While trying to use [pysqlite3](https://github.com/coleifer/pysqlite3) on macOS I got the following error:

```pycon
>>> import pysqlite3
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/Users/simon/.local/share/virtualenvs/datasette-AWNrQs95/lib/python3.8/site-packages/pysqlite3/__init__.py", line 23, in <module>
    from pysqlite3.dbapi2 import *
  File "/Users/simon/.local/share/virtualenvs/datasette-AWNrQs95/lib/python3.8/site-packages/pysqlite3/dbapi2.py", line 28, in <module>
    from pysqlite3._sqlite3 import *
ImportError: dlopen(/Users/simon/.local/share/virtualenvs/datasette-AWNrQs95/lib/python3.8/site-packages/pysqlite3/_sqlite3.cpython-38-darwin.so, 2): Symbol not found: _sqlite3_enable_load_extension
  Referenced from: /Users/simon/.local/share/virtualenvs/datasette-AWNrQs95/lib/python3.8/site-packages/pysqlite3/_sqlite3.cpython-38-darwin.so
  Expected in: flat namespace
 in /Users/simon/.local/share/virtualenvs/datasette-AWNrQs95/lib/python3.8/site-packages/pysqlite3/_sqlite3.cpython-38-darwin.so
```
Thanks to [this tip](https://stackoverflow.com/a/60046923/6083) on Stack Overflow I found that installing a fresh SQLite with `brew install sqlite3` and then running the following first fixed the error:

    export DYLD_LIBRARY_PATH=/usr/local/opt/sqlite/lib:/usr/lib

Then:
```pycon
>>> import pysqlite3
>>> pysqlite3.connect(":memory:").execute("select sqlite_version()").fetchall()
[('3.36.0',)]
```
This is because the Homebrew SQLite is "keg-only", which means that it does not become the default on the system to avoid intefering with the existing SQLite that ships with macOS.

As illustrated by the following:

```
% which sqlite3
/usr/bin/sqlite3
% echo "select sqlite_version()" | /usr/bin/sqlite3
3.28.0
% echo "select sqlite_version()" | /usr/local/opt/sqlite3/bin/sqlite3 
3.36.0
```
