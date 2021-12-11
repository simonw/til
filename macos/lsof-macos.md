# Using lsof on macOS

`lsof` stands for "list open files". Here are some very basic usage notes for the version that ships with macOS.

## Listing processes that have a specific file open
```
~ % lsof /tmp/covid-smaller.db
COMMAND   PID  USER   FD   TYPE DEVICE  SIZE/OFF      NODE NAME
Python  17990 simon    6r   REG    1,5 747413504 187550734 /private/tmp/covid-smaller.db
Python  17990 simon   12r   REG    1,5 747413504 187550734 /private/tmp/covid-smaller.db
```
Note that this file is opened twice by the same process (Datasette maintains multiple connections to the same SQLite database). The `PID` column is useful.

In the `FD` column `6r` means "file descriptor 6, open for read access". `w` would mean write access, `u` would mean both.

## Files for a specific process

I removed some of the output here trying to leave the most interesting bits:

```
~ % lsof -p 17990
COMMAND   PID  USER   FD     TYPE             DEVICE  SIZE/OFF                NODE NAME
Python  17990 simon  cwd      DIR                1,5      1344           174186151 /private/tmp
Python  17990 simon  txt      REG                1,5     49400           163507251 /usr/local/Cellar/python@3.9/3.9.7/Frameworks/Python.framework/Versions/3.9/Resources/Python.app/Contents/MacOS/Python
Python  17990 simon  txt      REG                1,5   3632512           163507083 /usr/local/Cellar/python@3.9/3.9.7/Frameworks/Python.framework/Versions/3.9/Python
...
Python  17990 simon  txt      REG                1,5     50840           152019254 /usr/local/Cellar/datasette/0.58.1/libexec/lib/python3.9/site-packages/markupsafe/_speedups.cpython-39-darwin.so
...
Python  17990 simon  txt      REG                1,5   1069536           148927587 /usr/local/Cellar/sqlite/3.36.0/lib/libsqlite3.0.dylib
Python  17990 simon  txt      REG                1,5     24552           179047672 /usr/local/Cellar/datasette/0.58.1/libexec/lib/python3.9/site-packages/bpylist/bplist.cpython-39-darwin.so
Python  17990 simon  txt      REG                1,5   1572480 1152921500312757159 /usr/lib/dyld
Python  17990 simon    0u     CHR               16,5   0t94656                6931 /dev/ttys005
Python  17990 simon    1u     CHR               16,5   0t94656                6931 /dev/ttys005
Python  17990 simon    2u     CHR               16,5   0t94656                6931 /dev/ttys005
Python  17990 simon    3u  KQUEUE                                                  count=0, state=0xa
Python  17990 simon    4u    unix 0x67a396d5b54b61cb       0t0                     ->0x67a396d5b54b522b
Python  17990 simon    5u    unix 0x67a396d5b54b522b       0t0                     ->0x67a396d5b54b61cb
Python  17990 simon    6r     REG                1,5 747413504           187550734 /private/tmp/covid-smaller.db
Python  17990 simon    7u  KQUEUE                                                  count=0, state=0xa
Python  17990 simon    8u    unix 0x67a396d5b54b68d3       0t0                     ->0x67a396d5b54b5613
Python  17990 simon    9u    unix 0x67a396d5b54b5613       0t0                     ->0x67a396d5b54b68d3
Python  17990 simon   10u    IPv4 0x67a396d59c718b2b       0t0                 TCP localhost:8422 (LISTEN)
Python  17990 simon   12r     REG                1,5 747413504           187550734 /private/tmp/covid-smaller.db
```
The column with `FD=cwd`, `TYPE=DIR` shows the working directory for the process.

The `TYPE=IPv4` one is interesting, it shows that we are lestining on `localhost:8422`.
