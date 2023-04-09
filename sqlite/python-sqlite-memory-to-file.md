# Saving an in-memory SQLite database to a file in Python

I was messing around in Python with an in-memory SQLite database, when I decided I actually wanted to save my experimental database to a file so I could explore it using [Datasette](https://datasette.io/).

In-memory databases can be created using `sqlite3` like this:

```python
import sqlite3

db = sqlite.connect(":memory:")
```
Or with [sqlite-utils](https://sqlite-utils.datasette.io/) like this:
```python
import sqlite_utils

db = sqlite_utils.Database(memory=True)
```

The `VACUUM INTO` command can be used to save a copy of the database to a new file. Here's how to use it:

```python
import sqlite3

db = sqlite3.connect(":memory:")
db.execute("create table foo (bar text)")

db.execute("vacuum main into '/tmp/saved.db'")

# Or with sqlite-utils
import sqlite_utils

db = sqlite_utils.Database(memory=True)

db["foo"].insert({"bar": "Example record"})

db.execute("vacuum main into '/tmp/saved2.db'")
```
