# Deno KV

I got intrigued by [Deno KV](https://deno.com/kv), which describes itself as "a global database for global apps". It's a key/value store for Deno applications which bundles some kind of worldwide distributed/replicated database service.

The code example looked like this:
```javascript
const kv = await Deno.openKv();
```
Wait, that looks like a core language feature? Are they shipping a client for their own proprietary hosted cloud database as part of their core language?

They're not - at least not in the open source implementation of Deno. I dug in and I think I understand what they're doing.

## The Deno local key/value store

This is a new feature that's still hidden behind Deno's `--unstable` flag. It landed it [Deno 1.32](https://github.com/denoland/deno/releases/tag/v1.32.0) on 22nd March 2023.

The [getting started documentation]([https://deno.com/manual@v1.33.1/runtime/kv](https://deno.com/manual@v1.33.1/runtime/kv#getting-started)) included this confusing text:

> A database can be opened using the `Deno.openKv()` function. This function optionally takes a database path on disk as the first argument. If no path is specified, the database is persisted in a global directory, bound to the script that `Deno.openKv()` was called from. Future invocations of the same script will use the same database.

What does "global directory" mean - is this the cloud service they're talking about?

It's not. I ran the following script and used Activity Monitor to see what it was doing:

```javascript
import { sleep } from "https://deno.land/x/sleep/mod.ts";

const kv = await Deno.openKv();

// Persist an object at the users/alice key.
await kv.set(["users", "alice"], { name: "Alice", age: 44 });

// Read back this key.
const res = await kv.get(["users", "alice"]);
console.log(res.key); // [ "users", "alice" ]
console.log(res.value); // { name: "Alice" }

console.log('About to sleep for a minute')
await sleep(60);
```
I ran it like this:
```
% deno run --unstable hello.js
[ "users", "alice" ]
{ name: "Alice", age: 44 }
About to sleep for a minute
```
This gave me a 60s window to open up Activity Monitor on my Mac, find the `deno` process, click the information icon and click on Open Files and Ports:

![List of open files and ports for Deno](https://user-images.githubusercontent.com/9599/235260598-06b771a3-c51c-4c16-b5a0-1741293d3759.png)

The crucial file was this one:

`/Users/simon/Library/Caches/deno/location_data/82469e8b266758412fd6bbd0058abaee6712cadb9c64024473af6afcff9eba6f/kv.sqlite3-shm`

So that's what it means by "a global directory" - it's talking about the `~/Library/Caches/deno/location_data` folder, which appears to hold directories with hashes for names (possibly the hash of the path to the Deno script) which can contain extra data.

And `kv.sqlite3` is a SQLite database!

Here's the schema of that database:
```
sqlite-utils dump kv.sqlite3 
```
```sql
BEGIN TRANSACTION;
CREATE TABLE data_version (
  k integer primary key,
  version integer not null
);
INSERT INTO "data_version" VALUES(0,5);
CREATE TABLE kv (
  k blob primary key,
  v blob not null,
  v_encoding integer not null,
  version integer not null
) without rowid;
INSERT INTO "kv" VALUES(X'0275736572730002616C69636500',X'FF0F6F22046E616D652205416C696365220361676549587B02',1,5);
CREATE TABLE migration_state(
  k integer not null primary key,
  version integer not null
);
INSERT INTO "migration_state" VALUES(0,2);
CREATE TABLE queue (
  ts integer not null,
  id text not null,
  data blob not null,
  backoff_schedule text not null,
  keys_if_undelivered blob not null,

  primary key (ts, id)
);
CREATE TABLE queue_running(
  deadline integer not null,
  id text not null,
  data blob not null,
  backoff_schedule text not null,
  keys_if_undelivered blob not null,

  primary key (deadline, id)
);
COMMIT;
```
This is interesting. Clearly they've come up with their own atomic key/value primitive, then designed a SQLite schema for storing serialized versions of those objects on disk.

## The Deno Deploy cloud hosted version

It looks to me like they've designed a data structure that will work well with the new hosted, FoundationDB, global infrastructure they've been building for their [Deno Deploy](https://deno.com/deploy) cloud service, then figured out a way to support the same set of operations locally on top of SQLite.

It looks like the magic part is that if you write code that uses `Deno.openKv()` without any extra arguments, your script will use a SQLite database in that `location_data` directory when it runs locally... but once deployed to Deno Deploy it will switch to using a FoundationDB-backed cloud database, replicated around the world.

I find this particularly interesting in terms of open source business models: they're baking a core feature into their framework which their SaaS platform is uniquely positioned to offer as a global-scale upgrade.

## A counter

I tried to copy this from the KV marketing landing page, and ended up having to tweak it a bit to get it to work.

Saved as `counter.js`:
```javascript
import { serve } from "https://deno.land/std/http/server.ts";

const kv = await Deno.openKv('count.db');

serve (async () => {
    await kv.atomic().sum(["visits"], 1n).commit();
    const res = await kv.get(["visits"]);
    console.log(res);
    return new Response(`Visits: ${res.value.value}`);
});
```
Run like this:
```
deno --unstable run counter.js
```
```
✅ Granted read access to "count.db".
✅ Granted write access to "count.db".
✅ Granted net access to "0.0.0.0:8000".
Listening on http://localhost:8000/
```
Now `http://localhost:8000/` serves a blank page with a "Visits: 3" number that increments on every hit.

The console logs this out:

```
{
  key: [ "visits" ],
  value: KvU64 { value: 19n },
  versionstamp: "00000000000000130000"
}
{
  key: [ "visits" ],
  value: KvU64 { value: 20n },
  versionstamp: "00000000000000140000"
}
{
  key: [ "visits" ],
  value: KvU64 { value: 21n },
  versionstamp: "00000000000000150000"
}
```
And the relevant parts of the SQLite database dump look like this:
```sql
CREATE TABLE data_version (
  k integer primary key,
  version integer not null
);
INSERT INTO "data_version" VALUES(0,22);
CREATE TABLE kv (
  k blob primary key,
  v blob not null,
  v_encoding integer not null,
  version integer not null
) without rowid;
INSERT INTO "kv" VALUES(X'0276697369747300',X'1600000000000000',2,22);
CREATE TABLE migration_state(
  k integer not null primary key,
  version integer not null
);
INSERT INTO "migration_state" VALUES(0,2);
```
I had to upgrade to [Deno 1.32.5](https://github.com/denoland/deno/releases/tag/v1.32.5) to get this to work (`brew upgrade deno`) as the `kv.atomic().sum(...)` feature is brand new.

## Further reading

- The [Deno KV Key Space](https://deno.com/manual@v1.33.1/runtime/kv/key_space) documentation has some interesting lower-level details of how this all works.
- [Secondary Indexes](https://deno.com/manual@v1.33.1/runtime/kv/secondary_indexes) shows some advanced patterns for working with Deno KV.
