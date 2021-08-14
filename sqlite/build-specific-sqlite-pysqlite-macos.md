# Building a specific version of SQLite with pysqlite on macOS

I wanted the ability to test my Python software against specific version of SQLite on macOS. I found a way to do that using [pysqlite3](https://github.com/coleifer/pysqlite3).

First, clone the GitHub mirror of SQLite (so I don't have to learn how to use Fossil):

    cd /tmp
    git clone https://github.com/sqlite/sqlite`

Check out the version tag you want to try:

    cd /tmp/sqlite
    git checkout version-3.17.0

The SQLite [build docs](https://github.com/sqlite/sqlite/tree/version-3.36.0#compiling-for-unix-like-systems) suggest using a `bld` directory like this:

    mkdir /tmp/bld
    cd /tmp/bld
    ../sqlite/configure
    make sqlite3.c

This will have constructed the amalgamation source needed by `pysqlite3`.

Now build that:

    cd /tmp
    git clone https://github.com/coleifer/pysqlite3
    cd pysqlite3
    cp /tmp/bld/sqlite3.c .
    cp /tmp/bld/sqlite3.h .
    python3 setup.py build_static build

The end result sits in  a `pysqlite3` folder in, on my machine, `/tmp/pysqlite3/build/lib.macosx-10.15-x86_64-3.9` - test it like this:

    cd /tmp/pysqlite3/build/lib.macosx-10.15-x86_64-3.9
    python3
    Python 3.9.6 (default, Jun 29 2021, 06:20:32) 
    [Clang 12.0.0 (clang-1200.0.32.29)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import pysqlite3
    >>> pysqlite3.connect(":memory:").execute("select sqlite_version()").fetchone()[0]
    '3.17.0'

I'm hoping that this process works almost exactly the same on Linux.
