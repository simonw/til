# Replicating SQLite with rqlite

I tried out [rqlite](https://github.com/rqlite/rqlite) today, a "lightweight, distributed relational database, which uses SQLite as its storage engine". It uses the Raft consensus algorithm to allow multiple SQLite instances to elect a leader and replicate changes amongst themselves.

By default `rqlite` asks you to use its own custom HTTP API - but I wanted to try running it against Datasette. Raft author Philip O'Toole confirmed that [this should work](https://twitter.com/general_order24/status/1343619601758908419) provided any writes go through the API - each node can be configured to write to an on-disk database file which Datasette can then read from (the default is to use in-memory databases and an on-disk Raft log).

Here's how I got that working on my macOS laptop. I used the latest macOS binary from https://github.com/rqlite/rqlite/releases (`rqlite` is written in Go and provides pre-complied binaries for different systems).

    cd /tmp
    curl -L https://github.com/rqlite/rqlite/releases/download/v5.7.0/rqlite-v5.7.0-darwin-amd64.tar.gz \
      -o rqlite-v5.7.0-darwin-amd64.tar.gz
    tar xvfz rqlite-v5.7.0-darwin-amd64.tar.gz
    cd rqlite-v5.7.0-darwin-amd64

I started the first node like this:

    ./rqlited -on-disk ~/node.1

This created a SQLite database file in `~/node.1/db.sqlite` which I could open with Datasette.

Note that the `-on-disk` option has to come before the `~/node.1` - if it comes afterwards it silently fails to take effect.

I created a table and inserted a record using the client binary like this:

    ./rqlite
    CREATE TABLE foo (id INTEGER NOT NULL PRIMARY KEY, name TEXT)
    INSERT INTO foo(name) VALUES("fiona")

Running Datasette against `~/node.1/db.sqlite` confirmed the table had been created.

Then I started a second node like this:

    ./rqlited -on-disk -node-id 2 -http-addr localhost:4003 \
        -raft-addr localhost:4004 -join http://localhost:4001 \
        ~/node.2

Since it was running on the same machine I had to pick different ports for it, then tell it to join the existing cluster at `http://localhost:4001`

This created a database file at `~/node.2/db.sqlite`.

I confirmed that this database had the `foo` table in it, then inserted another row and watched as both of my database files were updated with the new record.
