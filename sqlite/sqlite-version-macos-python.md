# Compile and run a new SQLite version with the existing sqlite3 Python library on macOS

I've been trying to figure this out for years. Previous notes include [Using LD_PRELOAD to run any version of SQLite with Python](https://til.simonwillison.net/sqlite/ld-preload) (Linux only), and [Building a specific version of SQLite with pysqlite on macOS/Linux](https://til.simonwillison.net/sqlite/build-specific-sqlite-pysqlite-macos) and [Using pysqlite3 on macOS](https://til.simonwillison.net/sqlite/pysqlite3-on-macos) (both using the `pysqlite3` package). But the dream was always to find a way to let me easily run a different SQLite version with the `sqlite3` module from the Python standard library directly on my Mac.

[Alex Garcia](https://til.simonwillison.net/sqlite/pysqlite3-on-macos) helped me find the solution I've been looking for this morning.

It's pretty simple: you compile a new `libsqlite3.0.dylib` module from the SQLite amalgamation release, then point `DYLD_LIBRARY_PATH` to it before loading Python and importing `sqlite3`.

The amalgamation builds are released as zip files on the [SQLite downloads page](https://www.sqlite.org/download.html) - let's grab 3.42.0, the most recent stable release:

```bash
wget 'https://www.sqlite.org/2023/sqlite-amalgamation-3420000.zip'
```
Then:
```
unzip sqlite-amalgamation-3420000.zip
cd sqlite-amalgamation-3420000
```
Running `ls -lah` shows there's only four files in that zip file:
```
-rw-rw-r--  1 simon  wheel   847K May 16 06:45 shell.c
-rw-rw-r--  1 simon  wheel   8.3M May 16 06:45 sqlite3.c
-rw-rw-r--  1 simon  wheel   611K May 16 06:45 sqlite3.h
-rw-rw-r--  1 simon  wheel    37K May 16 06:45 sqlite3ext.h
```
How do I compile that? I [asked GPT-4](https://chat.openai.com/share/570757ab-8152-441f-ae5e-b045ece3ebe5) and got this recipe:
```bash
gcc -dynamiclib sqlite3.c -o libsqlite3.0.dylib -lm -lpthread
```
On my machine that runs in less than a second and produces a 1.2MB `libsqlite3.0.dylib` file.

To use it, set `DYLD_LIBRARY_PATH` to the folder that contains that `.dylib` file. We can use `$PWD` for that:
```
DYLD_LIBRARY_PATH=$PWD python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
```
Outputs:
```
3.42.0
```
If I run that without the environment variable I get the older version:
```
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
```
Outputs:
```
3.41.1
```
And this works to run Datasette as well:
```bash
DYLD_LIBRARY_PATH=$PWD datasette --get /-/versions.json | jq
```
Shows:
```json
{
  "python": {
    "version": "3.10.10",
    "full": "3.10.10 (main, Mar 21 2023, 13:41:05) [Clang 14.0.6 ]"
  },
  "datasette": {
    "version": "1.0a4"
  },
  "asgi": "3.0",
  "uvicorn": "0.23.2",
  "sqlite": {
    "version": "3.42.0",
    "fts_versions": [],
    "extensions": {
      "json1": null
    },
    "compile_options": [
      "ATOMIC_INTRINSICS=1",
      "COMPILER=clang-14.0.3",
      "DEFAULT_AUTOVACUUM",
      "DEFAULT_CACHE_SIZE=-2000",
      "DEFAULT_FILE_FORMAT=4",
      "DEFAULT_JOURNAL_SIZE_LIMIT=-1",
      "DEFAULT_MMAP_SIZE=0",
      "DEFAULT_PAGE_SIZE=4096",
      "DEFAULT_PCACHE_INITSZ=20",
      "DEFAULT_RECURSIVE_TRIGGERS",
      "DEFAULT_SECTOR_SIZE=4096",
      "DEFAULT_SYNCHRONOUS=2",
      "DEFAULT_WAL_AUTOCHECKPOINT=1000",
      "DEFAULT_WAL_SYNCHRONOUS=2",
      "DEFAULT_WORKER_THREADS=0",
      "MALLOC_SOFT_LIMIT=1024",
      "MAX_ATTACHED=10",
      "MAX_COLUMN=2000",
      "MAX_COMPOUND_SELECT=500",
      "MAX_DEFAULT_PAGE_SIZE=8192",
      "MAX_EXPR_DEPTH=1000",
      "MAX_FUNCTION_ARG=127",
      "MAX_LENGTH=1000000000",
      "MAX_LIKE_PATTERN_LENGTH=50000",
      "MAX_MMAP_SIZE=0x7fff0000",
      "MAX_PAGE_COUNT=1073741823",
      "MAX_PAGE_SIZE=65536",
      "MAX_SQL_LENGTH=1000000000",
      "MAX_TRIGGER_DEPTH=1000",
      "MAX_VARIABLE_NUMBER=32766",
      "MAX_VDBE_OP=250000000",
      "MAX_WORKER_THREADS=8",
      "MUTEX_PTHREADS",
      "SYSTEM_MALLOC",
      "TEMP_STORE=1",
      "THREADSAFE=1"
    ]
  }
}
```
Without the environment variable I get this instead:
```json
{
  "python": {
    "version": "3.10.10",
    "full": "3.10.10 (main, Mar 21 2023, 13:41:05) [Clang 14.0.6 ]"
  },
  "datasette": {
    "version": "1.0a4"
  },
  "asgi": "3.0",
  "uvicorn": "0.23.2",
  "sqlite": {
    "version": "3.41.1",
    "fts_versions": [
      "FTS5",
      "FTS4",
      "FTS3"
    ],
    "extensions": {
      "json1": null
    },
    "compile_options": [
      "ATOMIC_INTRINSICS=1",
      "COMPILER=clang-14.0.6",
      "DEFAULT_AUTOVACUUM",
      "DEFAULT_CACHE_SIZE=-2000",
      "DEFAULT_FILE_FORMAT=4",
      "DEFAULT_JOURNAL_SIZE_LIMIT=-1",
      "DEFAULT_MMAP_SIZE=0",
      "DEFAULT_PAGE_SIZE=4096",
      "DEFAULT_PCACHE_INITSZ=20",
      "DEFAULT_RECURSIVE_TRIGGERS",
      "DEFAULT_SECTOR_SIZE=4096",
      "DEFAULT_SYNCHRONOUS=2",
      "DEFAULT_WAL_AUTOCHECKPOINT=1000",
      "DEFAULT_WAL_SYNCHRONOUS=2",
      "DEFAULT_WORKER_THREADS=0",
      "ENABLE_COLUMN_METADATA",
      "ENABLE_DBSTAT_VTAB",
      "ENABLE_FTS3",
      "ENABLE_FTS3_TOKENIZER",
      "ENABLE_FTS4",
      "ENABLE_FTS5",
      "ENABLE_GEOPOLY",
      "ENABLE_MATH_FUNCTIONS",
      "ENABLE_RTREE",
      "ENABLE_UNLOCK_NOTIFY",
      "MALLOC_SOFT_LIMIT=1024",
      "MAX_ATTACHED=10",
      "MAX_COLUMN=2000",
      "MAX_COMPOUND_SELECT=500",
      "MAX_DEFAULT_PAGE_SIZE=8192",
      "MAX_EXPR_DEPTH=10000",
      "MAX_FUNCTION_ARG=127",
      "MAX_LENGTH=1000000000",
      "MAX_LIKE_PATTERN_LENGTH=50000",
      "MAX_MMAP_SIZE=0x7fff0000",
      "MAX_PAGE_COUNT=1073741823",
      "MAX_PAGE_SIZE=65536",
      "MAX_SQL_LENGTH=1000000000",
      "MAX_TRIGGER_DEPTH=1000",
      "MAX_VARIABLE_NUMBER=250000",
      "MAX_VDBE_OP=250000000",
      "MAX_WORKER_THREADS=8",
      "MUTEX_PTHREADS",
      "SECURE_DELETE",
      "SYSTEM_MALLOC",
      "TEMP_STORE=1",
      "THREADSAFE=1"
    ]
  }
}
```
Interesting that the `dylib` version appears to be missing the FTS extension.
