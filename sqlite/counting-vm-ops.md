# Counting SQLite virtual machine operations

When SQLite executes a query, it does so by executing a sequence of virtual machine operations.

There are mechanisms for cancelling a query after a specific number of these operations, to protect against long-running queries.

To work with those mechanisms, it's useful to get a feel for how many operations different queries execute.

Thanks to [tips on the SQLite forum](https://sqlite.org/forum/forumpost/dfb178d58c185ee4) I now know how to count these operations using the `sqlite3` command line tool, using `.stats vmstats` to turn on display of that number after each query:

```
% sqlite3 fixtures.db 
SQLite version 3.36.0 2021-06-18 18:58:49
Enter ".help" for usage hints.
sqlite> .stats vmstep
sqlite> select * from facetable;
1|2019-01-14 08:00:00|1|1|CA|1|Mission|["tag1", "tag2"]|[{"foo": "bar"}]|one
2|2019-01-14 08:00:00|1|1|CA|1|Dogpatch|["tag1", "tag3"]|[]|two
3|2019-01-14 08:00:00|1|1|CA|1|SOMA|[]|[]|
4|2019-01-14 08:00:00|1|1|CA|1|Tenderloin|[]|[]|
5|2019-01-15 08:00:00|1|1|CA|1|Bernal Heights|[]|[]|
6|2019-01-15 08:00:00|1|1|CA|1|Hayes Valley|[]|[]|
7|2019-01-15 08:00:00|1|1|CA|2|Hollywood|[]|[]|
8|2019-01-15 08:00:00|1|1|CA|2|Downtown|[]|[]|
9|2019-01-16 08:00:00|1|1|CA|2|Los Feliz|[]|[]|
10|2019-01-16 08:00:00|1|1|CA|2|Koreatown|[]|[]|
11|2019-01-16 08:00:00|1|1|MI|3|Downtown|[]|[]|
12|2019-01-17 08:00:00|1|1|MI|3|Greektown|[]|[]|
13|2019-01-17 08:00:00|1|1|MI|3|Corktown|[]|[]|
14|2019-01-17 08:00:00|1|1|MI|3|Mexicantown|[]|[]|
15|2019-01-17 08:00:00|2|0|MC|4|Arcadia Planitia|[]|[]|
VM-steps: 187
sqlite> select * from facetable limit 3;
1|2019-01-14 08:00:00|1|1|CA|1|Mission|["tag1", "tag2"]|[{"foo": "bar"}]|one
2|2019-01-14 08:00:00|1|1|CA|1|Dogpatch|["tag1", "tag3"]|[]|two
3|2019-01-14 08:00:00|1|1|CA|1|SOMA|[]|[]|
VM-steps: 46
```
Using `.stats on` shows a more detailed group of statistics about the query:
```
sqlite> .stats on
sqlite> select * from facetable limit 3;
1|2019-01-14 08:00:00|1|1|CA|1|Mission|["tag1", "tag2"]|[{"foo": "bar"}]|one
2|2019-01-14 08:00:00|1|1|CA|1|Dogpatch|["tag1", "tag3"]|[]|two
3|2019-01-14 08:00:00|1|1|CA|1|SOMA|[]|[]|
Memory Used:                         195520 (max 195776) bytes
Number of Outstanding Allocations:   525 (max 526)
Number of Pcache Overflow Bytes:     5696 (max 5696) bytes
Largest Allocation:                  122400 bytes
Largest Pcache Allocation:           4104 bytes
Lookaside Slots Used:                94 (max 122)
Successful lookaside attempts:       431
Lookaside failures due to size:      4
Lookaside failures due to OOM:       0
Pager Heap Usage:                    23008 bytes
Page cache hits:                     6
Page cache misses:                   4
Page cache writes:                   0
Page cache spills:                   0
Schema Heap Usage:                   25216 bytes
Statement Heap/Lookaside Usage:      15504 bytes
Fullscan Steps:                      2
Sort Operations:                     0
Autoindex Inserts:                   0
Virtual Machine Steps:               46
Reprepare operations:                0
Number of times run:                 1
Memory used by prepared stmt:        15504
```
There is also a `sqlite_stmt` virtual table ([documented here](https://sqlite.org/stmt.html)) which can be enabled using a loadable module, but I have not yet managed to get this to compile and load into the Python `sqlite3` environment.

## Cancelling queries after a specified number of opcodes

You can set an upper limit on the number of opcodes in the `sqlite3` command line using `.progress 100 --limit 1`, as [described here](https://sqlite.org/forum/forumpost/4a669c7b50f9a64c):

```
sqlite> .progress 100 --limit 1
sqlite> select * from facetable limit 3;
1|2019-01-14 08:00:00|1|1|CA|1|Mission|["tag1", "tag2"]|[{"foo": "bar"}]|one
2|2019-01-14 08:00:00|1|1|CA|1|Dogpatch|["tag1", "tag3"]|[]|two
3|2019-01-14 08:00:00|1|1|CA|1|SOMA|[]|[]|
sqlite> select * from facetable;
1|2019-01-14 08:00:00|1|1|CA|1|Mission|["tag1", "tag2"]|[{"foo": "bar"}]|one
2|2019-01-14 08:00:00|1|1|CA|1|Dogpatch|["tag1", "tag3"]|[]|two
3|2019-01-14 08:00:00|1|1|CA|1|SOMA|[]|[]|
4|2019-01-14 08:00:00|1|1|CA|1|Tenderloin|[]|[]|
5|2019-01-15 08:00:00|1|1|CA|1|Bernal Heights|[]|[]|
6|2019-01-15 08:00:00|1|1|CA|1|Hayes Valley|[]|[]|
7|2019-01-15 08:00:00|1|1|CA|2|Hollywood|[]|[]|
Progress limit reached (1)
Error: interrupted
```
In Python code this can be achieved like so:

```python
conn.set_progress_handler(lambda: 1, 100)
```
This sets a progress handler which will be called after every 100 opcodes - but by returning `1` the handler causes the query to be cancelled:
```pycon
>>> import sqlite3
>>> conn = sqlite3.connect("fixtures.db")
>>> conn.set_progress_handler(lambda: 1, 200)
>>> conn.execute("select * from facetable limit 3").rows()
# Outputs rows
>>> conn.execute("select * from facetable").fetchall()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
sqlite3.OperationalError: interrupted
```
This didn't exactly work how I expected - I had to change the number from 100 to 200 and I'm not sure why. But it illustrates the principle.
