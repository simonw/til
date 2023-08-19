# A one-liner to output details of the current Python's SQLite

In investigating [llm/issues/164](https://github.com/simonw/llm/issues/164) I found myself needing to know more precise details of the Python SQLite environment used by the reporter of the bug.

I came up with this one-liner for pasting into a terminal:
```bash
python -c '
import sqlite3
import sys
conn = sqlite3.connect(":memory:")
print("Python version:", sys.version)
print("SQLite version:", conn.execute("select sqlite_version()").fetchone()[0])
print("SQLite compile options\n  " + "\n  ".join(r[0] for r in conn.execute("pragma compile_options").fetchall()))
for pragma in (
        "foreign_keys", "defer_foreign_keys", "ignore_check_constraints", "legacy_alter_table",
        "recursive_triggers", "writable_schema",
    ):
    output = conn.execute("pragma %s" % pragma).fetchone()
    print("Pragma {}: {}".format(pragma, output[0]))
'
```
The output on my machine looks like this:
```
Python version: 3.10.10 (main, Mar 21 2023, 13:41:05) [Clang 14.0.6 ]
SQLite version: 3.41.1
SQLite compile options
  ATOMIC_INTRINSICS=1
  COMPILER=clang-14.0.6
  DEFAULT_AUTOVACUUM
  DEFAULT_CACHE_SIZE=-2000
  DEFAULT_FILE_FORMAT=4
  DEFAULT_JOURNAL_SIZE_LIMIT=-1
  DEFAULT_MMAP_SIZE=0
  DEFAULT_PAGE_SIZE=4096
  DEFAULT_PCACHE_INITSZ=20
  DEFAULT_RECURSIVE_TRIGGERS
  DEFAULT_SECTOR_SIZE=4096
  DEFAULT_SYNCHRONOUS=2
  DEFAULT_WAL_AUTOCHECKPOINT=1000
  DEFAULT_WAL_SYNCHRONOUS=2
  DEFAULT_WORKER_THREADS=0
  ENABLE_COLUMN_METADATA
  ENABLE_DBSTAT_VTAB
  ENABLE_FTS3
  ENABLE_FTS3_TOKENIZER
  ENABLE_FTS4
  ENABLE_FTS5
  ENABLE_GEOPOLY
  ENABLE_MATH_FUNCTIONS
  ENABLE_RTREE
  ENABLE_UNLOCK_NOTIFY
  MALLOC_SOFT_LIMIT=1024
  MAX_ATTACHED=10
  MAX_COLUMN=2000
  MAX_COMPOUND_SELECT=500
  MAX_DEFAULT_PAGE_SIZE=8192
  MAX_EXPR_DEPTH=10000
  MAX_FUNCTION_ARG=127
  MAX_LENGTH=1000000000
  MAX_LIKE_PATTERN_LENGTH=50000
  MAX_MMAP_SIZE=0x7fff0000
  MAX_PAGE_COUNT=1073741823
  MAX_PAGE_SIZE=65536
  MAX_SQL_LENGTH=1000000000
  MAX_TRIGGER_DEPTH=1000
  MAX_VARIABLE_NUMBER=250000
  MAX_VDBE_OP=250000000
  MAX_WORKER_THREADS=8
  MUTEX_PTHREADS
  SECURE_DELETE
  SYSTEM_MALLOC
  TEMP_STORE=1
  THREADSAFE=1
Pragma foreign_keys: 0
Pragma defer_foreign_keys: 0
Pragma ignore_check_constraints: 0
Pragma legacy_alter_table: 0
Pragma recursive_triggers: 0
Pragma writable_schema: 0
```

The script works by querying `pragma compile_options` for the compilation options, then looping through and checking some boolean pragmas as well.

Full documentation on available SQLite pragmas [is here](https://www.sqlite.org/pragma.html).
