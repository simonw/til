# Using LD_PRELOAD to run any version of SQLite with Python

I've been wanting to figure this out for ages. [This thread](https://news.ycombinator.com/item?id=23282684) on Hacker News plus [this Stackoverflow post](https://unix.stackexchange.com/questions/24811/changing-linked-library-for-a-given-executable-centos-6/24833#24833:) gave me some initial clues.

The challenge: someone reports a bug in Datasette with a specific version of SQLite. How can I run Datasette against that specific version?

Steps:

1. Download the source code for that specific version
2. Build a `libsqlite3.so` file using that source code
3. Run Datasette prefixed with `LD_PRELOAD=path/to/libsqlite3.so`

## Obtaining source code for old SQLite versions

This took a while to figure out. https://www.sqlite.org/chronology.html has a list of links to different releases. From there clicking on one of the dates takes you to a page like this: https://www.sqlite.org/src/timeline?c=cf538e2783&y=ci

From there clicking the "version-X" link takes you through to the timeline page like this: https://www.sqlite.org/src/timeline?r=version-3.8.11.1 - then click on e.g. "check-in: cf538e27" to get to a page like https://www.sqlite.org/src/info/cf538e2783e468bb which has a link to a Tarball and a Zip archive. Download one of those!

Hopefully shorter version: decide which version you want, then navigate to https://www.sqlite.org/src/timeline?t=version-3.8.11.1 and click the check-in link to get to the page that links to the Zip / Tarball.

Here's the URL to the 3.8.11.1 Tarball: https://www.sqlite.org/src/tarball/cf538e27/SQLite-cf538e27.tar.gz

## Building the library

I first tried this on macOS but I couldn't get the `LD_PRELOAD` trick to work. I think this is because of "system integrity protection" (clue in [this comment](https://github.com/nteract/nteract/issues/1523#issuecomment-284027093)) - so I decided to do it in a Docker Ubuntu container instead.

To start a fresh Ubuntu container:

    docker run -it -p 8001:8001 ubuntu

I'm using `-p 8001:8001` here to allow me to access Datasette running on port 8001 later on.

Now we need python3 and the various build tools (SQLite also needs `tcl` for the build):

    apt-get install -y python3 build-essential tcl wget

Annoyingly installing `tcl` requires us to interactively set the timezone data - I enter `2` for America and then `85` for Los Angeles.

Download and extract the SQLite code:

    cd /tmp
    wget https://www.sqlite.org/src/tarball/cf538e27/SQLite-cf538e27.tar.gz
    tar -xzvf SQLite-cf538e27.tar.gz
    cd SQLite-cf538e27

Now we can build the extension.

    ./configure
    make

No need to run `make install`, we just need the library compiled.

This puts the libraries in a `.libs` directory:

    root@11b79085483e:/tmp/SQLite-cf538e27# ls -l .libs/
    total 22660
    -rw-r--r-- 1 root root 9622164 Jun 17 12:52 libsqlite3.a
    lrwxrwxrwx 1 root root      16 Jun 17 12:52 libsqlite3.la -> ../libsqlite3.la
    -rw-r--r-- 1 root root     955 Jun 17 12:52 libsqlite3.lai
    lrwxrwxrwx 1 root root      19 Jun 17 12:52 libsqlite3.so -> libsqlite3.so.0.8.6
    lrwxrwxrwx 1 root root      19 Jun 17 12:52 libsqlite3.so.0 -> libsqlite3.so.0.8.6
    -rwxr-xr-x 1 root root 4021816 Jun 17 12:52 libsqlite3.so.0.8.6
    -rwxr-xr-x 1 root root  314160 Jun 17 12:52 sqlite3
    -rw-r--r-- 1 root root 9232752 Jun 17 12:52 sqlite3.o

We can confirm that this worked using the following one-liner:

    LD_PRELOAD=.libs/libsqlite3.so python3 -c \
        'import sqlite3; print(sqlite3.connect(":memory").execute("select sqlite_version()").fetchone())'

Which for me now outputs:

    ('3.8.11.1',)

Try that without the `LD_PRELOAD` to see the difference:

    root@11b79085483e:/tmp/SQLite-cf538e27# python3 -c \
    > 'import sqlite3; print(sqlite3.connect(":memory").execute("select sqlite_version()").fetchone())'
    ('3.31.1',)

## Running Datasette

No need for a virtual environent since we are in a Docker container. We need to install `pip`:

    apt-get install -y python3-pip

Then we can install Datasette:

    python3 -mpip install datasette

Now run it like this:

    datasette -h 0.0.0.0
    INFO:     Started server process [10266]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)

We need `-h 0.0.0.0` to allow access from outside. On our machine we can now visit it here:

http://0.0.0.0:8001/-/versions

And confirm that the default SQLite version is `"version": "3.31.1"`.

Quit Datasette and start it again with the `LD_PRELOAD`:

    LD_PRELOAD=.libs/libsqlite3.so datasette -h 0.0.0.0
    INFO:     Started server process [10274]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)

And now http://0.0.0.0:8001/-/versions reports the following:

```json
{
    "python": {
        "version": "3.8.2",
        "full": "3.8.2 (default, Apr 27 2020, 15:53:34) \n[GCC 9.3.0]"
    },
    "datasette": {
        "version": "0.44"
    },
    "asgi": "3.0",
    "uvicorn": "0.11.5",
    "sqlite": {
        "version": "3.8.11.1",
        "fts_versions": [],
        "extensions": {},
        "compile_options": [
            "HAVE_ISNAN",
            "SYSTEM_MALLOC",
            "TEMP_STORE=1",
            "THREADSAFE=1"
        ]
    }
}
```
