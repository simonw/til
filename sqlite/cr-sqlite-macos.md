# Trying out cr-sqlite on macOS

[cr-sqlite](https://github.com/vlcn-io/cr-sqlite) is fascinating. It's a loadable SQLite extension by Matt Wonlaw that "allows merging different SQLite databases together that have taken independent writes".

It does that by implementing [CRDTs](https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type), via a set of SQL functions you can use to upgrade a table to a CRDT-backed version.

Since it's a SQLite extension it's available to any language that can use SQLite - so Python, Rust, Go etc are all covered for free.

And yes, there's a WASM build as well, demonstrated in [this Observable notebook](https://observablehq.com/@tantaman/cr-sqlite-basic-setup).

## Trying it out on macOS

It took me a bit of fiddling (see [this issue](https://github.com/vlcn-io/cr-sqlite/issues/338)) to get it up and running on macOS. Here's what worked for me.

1. Install a SQLite version that isn't the macOS default, which doesn't allow loading extensions. I used `brew install sqlite3` for this.
2. Download the [latest release](https://github.com/vlcn-io/cr-sqlite/releases) - at time of writing for my M2 Mac that's [v0.15.1/crsqlite-darwin-aarch64.dylib](https://github.com/vlcn-io/cr-sqlite/releases/download/v0.15.1/crsqlite-darwin-aarch64.dylib).
3. `cd` to the same folder as the download, then run:
    ```bash
    /opt/homebrew/opt/sqlite/bin/sqlite3
    ```
4. In the SQLite shell run this:
    ```
    .load crsqlite-darwin-aarch64 sqlite3_crsqlite_init
    ```
    That second part is essential, it tells SQLite the entrypoint to use. Without that (if you just try `.load crsqlite-darwin-aarch64`) you get a `symbol not found` error.
5. The first time I tried this it failed for me with a macOS security error. So...
6. Open up the System Settings -> Privacy & Security tool and click on the "open anyway" button for that extension.
7. Now try the `.load` command again... and this time it should work!

Once I had done all of that I ran through the [example in the README](https://github.com/vlcn-io/cr-sqlite/blob/v0.15.1/README.md#usage) and it worked as advertised. Broken up here into copy-pastable snippets:
```
.mode qbox
```
This turned on a new-to-me SQLite output mode which is very pleasant.
```
-- create tables as normal
create table foo (a primary key, b);
create table baz (a primary key, b, c, d);
```
```
-- update those tables to be crrs / crdts
select crsql_as_crr('foo');
select crsql_as_crr('baz');
```
```
-- insert some data / interact with tables as normal
insert into foo (a,b) values (1,2);
insert into baz (a,b,c,d) values ('a', 'woo', 'doo', 'daa');
```
```
-- ask for a record of what has changed
select "table", "pk", "cid", "val", "col_version", "db_version", COALESCE("site_id", crsql_site_id()), "cl", "seq" from crsql_changes;
```
Without `.mode qbox` this returned:
```
foo|	|b|2|1|1|ӓ?P??N??5I??|1|0
baz|
    a|c|doo|1|2|ӓ?P??N??5I??|1|1
baz|
    a|d|daa|1|2|ӓ?P??N??5I??|1|2
foo|	|b|thing|5|5|p???1F????????|1|0
baz|
    a|b|123|101|233|p???1F????????|1|0
```
But with `.mode qbox` those binary values were shown as much more readable hex:
```
┌───────┬─────────────┬─────┬─────────┬─────────────┬────────────┬──────────────────────────────────────┬────┬─────┐
│ table │     pk      │ cid │   val   │ col_version │ db_version │ COALESCE("site_id", crsql_site_id()) │ cl │ seq │
├───────┼─────────────┼─────┼─────────┼─────────────┼────────────┼──────────────────────────────────────┼────┼─────┤
│ 'foo' │ x'010901'   │ 'b' │ 2       │ 1           │ 1          │ x'd393ef50a8a84e17be1b32cc354985be'  │ 1  │ 0   │
│ 'baz' │ x'010b0161' │ 'c' │ 'doo'   │ 1           │ 2          │ x'd393ef50a8a84e17be1b32cc354985be'  │ 1  │ 1   │
│ 'baz' │ x'010b0161' │ 'd' │ 'daa'   │ 1           │ 2          │ x'd393ef50a8a84e17be1b32cc354985be'  │ 1  │ 2   │
│ 'foo' │ x'010905'   │ 'b' │ 'thing' │ 5           │ 5          │ x'7096e2d505314699a59c95faba14abb5'  │ 1  │ 0   │
│ 'baz' │ x'010b0161' │ 'b' │ 123     │ 101         │ 233        │ x'7096e2d505314699a59c95faba14abb5'  │ 1  │ 0   │
└───────┴─────────────┴─────┴─────────┴─────────────┴────────────┴──────────────────────────────────────┴────┴─────┘
```
```
-- simulate merging changes from a peer
insert into crsql_changes
  ("table", "pk", "cid", "val", "col_version", "db_version", "site_id", "cl", "seq")
  values
  ('foo', x'010905', 'b', 'thing', 5, 5, X'7096E2D505314699A59C95FABA14ABB5', 1, 0);
insert into crsql_changes ("table", "pk", "cid", "val", "col_version", "db_version", "site_id", "cl", "seq")
  values
  ('baz', x'010b0161', 'b', 123, 101, 233, X'7096E2D505314699A59C95FABA14ABB5', 1, 0);
```
```
-- check that peer's changes were applied
select * from foo;
```
```
select * from baz;
```
```
-- tear down the extension before closing the connection
select crsql_finalize();
```

## What the schema looks like

I ran the above sequence again against a database file on disk called `/tmp/temp.db` and then did this:

```bash
sqlite3 /tmp/temp.db .schema
```
Here's the resulting schema:
```sql
CREATE TABLE foo (a primary key, b);
CREATE TABLE baz (a primary key, b, c, d);
CREATE TABLE crsql_tracked_peers ("site_id" BLOB NOT NULL, "version" INTEGER NOT NULL, "seq" INTEGER DEFAULT 0, "tag" INTEGER, "event" INTEGER, PRIMARY KEY ("site_id", "tag", "event")) STRICT;
CREATE TABLE IF NOT EXISTS "crsql_master" ("key" TEXT PRIMARY KEY, "value" ANY);
CREATE TABLE IF NOT EXISTS "crsql_site_id" (site_id BLOB NOT NULL, ordinal INTEGER PRIMARY KEY AUTOINCREMENT);
CREATE TABLE sqlite_sequence(name,seq);
CREATE UNIQUE INDEX crsql_site_id_site_id ON "crsql_site_id" (site_id);
CREATE TABLE IF NOT EXISTS "foo__crsql_clock" (
      "a",
      __crsql_col_name TEXT NOT NULL,
      __crsql_col_version INT NOT NULL,
      __crsql_db_version INT NOT NULL,
      __crsql_site_id INT,
      __crsql_seq INT NOT NULL,
      PRIMARY KEY ("a", __crsql_col_name)
    );
CREATE INDEX "foo__crsql_clock_dbv_idx" ON "foo__crsql_clock" ("__crsql_db_version");
CREATE TRIGGER "foo__crsql_itrig"
      AFTER INSERT ON "foo" WHEN crsql_internal_sync_bit() = 0
      BEGIN
        UPDATE "foo__crsql_clock" SET
            __crsql_col_version = CASE __crsql_col_version % 2 WHEN 0 THEN __crsql_col_version + 1 ELSE __crsql_col_version + 2 END,
            __crsql_db_version = crsql_next_db_version(),
            __crsql_seq = crsql_increment_and_get_seq(),
            __crsql_site_id = NULL
          WHERE "a" IS NEW."a" AND __crsql_col_name = '-1';
INSERT INTO "foo__crsql_clock" (
          "a",
          __crsql_col_name,
          __crsql_col_version,
          __crsql_db_version,
          __crsql_seq,
          __crsql_site_id
        ) SELECT
          NEW."a",
          'b',
          1,
          crsql_next_db_version(),
          crsql_increment_and_get_seq(),
          NULL
        ON CONFLICT DO UPDATE SET
          __crsql_col_version = __crsql_col_version + 1,
          __crsql_db_version = crsql_next_db_version(),
          __crsql_seq = crsql_get_seq() - 1,
          __crsql_site_id = NULL;
      END;
CREATE TRIGGER "foo_a__crsql_utrig"
          AFTER UPDATE OF "a" ON "foo"
          WHEN crsql_internal_sync_bit() = 0 AND NEW."a" IS NOT OLD."a"
          BEGIN
            INSERT INTO "foo__crsql_clock" (
              "a",
              __crsql_col_name,
              __crsql_col_version,
              __crsql_db_version,
              __crsql_seq,
              __crsql_site_id
            ) SELECT
              OLD."a",
              '-1',
              2,
              crsql_next_db_version(),
              crsql_increment_and_get_seq(),
              NULL WHERE true
            ON CONFLICT DO UPDATE SET
              __crsql_col_version = 1 + __crsql_col_version,
              __crsql_db_version = crsql_next_db_version(),
              __crsql_seq = crsql_get_seq() - 1,
              __crsql_site_id = NULL;
            DELETE FROM "foo__crsql_clock"
              WHERE "a" IS OLD."a" AND __crsql_col_name != '-1';
          END;
CREATE TRIGGER "foo__crsql_utrig"
      AFTER UPDATE ON "foo" WHEN crsql_internal_sync_bit() = 0
      BEGIN
        INSERT INTO "foo__crsql_clock" (
          "a",
          __crsql_col_name,
          __crsql_col_version,
          __crsql_db_version,
          __crsql_seq,
          __crsql_site_id
        ) SELECT
          NEW."a",
          '-1',
          1,
          crsql_next_db_version(),
          crsql_increment_and_get_seq(),
          NULL
        WHERE NEW."a" IS NOT OLD."a"
        ON CONFLICT DO UPDATE SET
          __crsql_col_version = CASE __crsql_col_version % 2 WHEN 0 THEN __crsql_col_version + 1 ELSE __crsql_col_version + 2 END,
          __crsql_db_version = crsql_next_db_version(),
          __crsql_seq = crsql_get_seq() - 1,
          __crsql_site_id = NULL;
INSERT INTO "foo__crsql_clock" (
          "a",
          __crsql_col_name,
          __crsql_col_version,
          __crsql_db_version,
          __crsql_seq,
          __crsql_site_id
        ) SELECT
          NEW."a",
          'b',
          1,
          crsql_next_db_version(),
          crsql_increment_and_get_seq(),
          NULL
        WHERE NEW."b" IS NOT OLD."b"
        ON CONFLICT DO UPDATE SET
          __crsql_col_version = __crsql_col_version + 1,
          __crsql_db_version = crsql_next_db_version(),
          __crsql_seq = crsql_get_seq() - 1,
          __crsql_site_id = NULL;
      END;
CREATE TRIGGER "foo__crsql_dtrig"
    AFTER DELETE ON "foo" WHEN crsql_internal_sync_bit() = 0
    BEGIN
      INSERT INTO "foo__crsql_clock" (
        "a",
        __crsql_col_name,
        __crsql_col_version,
        __crsql_db_version,
        __crsql_seq,
        __crsql_site_id
      ) SELECT
        OLD."a",
        '-1',
        2,
        crsql_next_db_version(),
        crsql_increment_and_get_seq(),
        NULL WHERE true
      ON CONFLICT DO UPDATE SET
        __crsql_col_version = 1 + __crsql_col_version,
        __crsql_db_version = crsql_next_db_version(),
        __crsql_seq = crsql_get_seq() - 1,
        __crsql_site_id = NULL;
      DELETE FROM "foo__crsql_clock"
        WHERE "a" IS OLD."a" AND __crsql_col_name != '-1';
    END;
CREATE TABLE IF NOT EXISTS "baz__crsql_clock" (
      "a",
      __crsql_col_name TEXT NOT NULL,
      __crsql_col_version INT NOT NULL,
      __crsql_db_version INT NOT NULL,
      __crsql_site_id INT,
      __crsql_seq INT NOT NULL,
      PRIMARY KEY ("a", __crsql_col_name)
    );
CREATE INDEX "baz__crsql_clock_dbv_idx" ON "baz__crsql_clock" ("__crsql_db_version");
CREATE TRIGGER "baz__crsql_itrig"
      AFTER INSERT ON "baz" WHEN crsql_internal_sync_bit() = 0
      BEGIN
        UPDATE "baz__crsql_clock" SET
            __crsql_col_version = CASE __crsql_col_version % 2 WHEN 0 THEN __crsql_col_version + 1 ELSE __crsql_col_version + 2 END,
            __crsql_db_version = crsql_next_db_version(),
            __crsql_seq = crsql_increment_and_get_seq(),
            __crsql_site_id = NULL
          WHERE "a" IS NEW."a" AND __crsql_col_name = '-1';
INSERT INTO "baz__crsql_clock" (
          "a",
          __crsql_col_name,
          __crsql_col_version,
          __crsql_db_version,
          __crsql_seq,
          __crsql_site_id
        ) SELECT
          NEW."a",
          'b',
          1,
          crsql_next_db_version(),
          crsql_increment_and_get_seq(),
          NULL
        ON CONFLICT DO UPDATE SET
          __crsql_col_version = __crsql_col_version + 1,
          __crsql_db_version = crsql_next_db_version(),
          __crsql_seq = crsql_get_seq() - 1,
          __crsql_site_id = NULL;
INSERT INTO "baz__crsql_clock" (
          "a",
          __crsql_col_name,
          __crsql_col_version,
          __crsql_db_version,
          __crsql_seq,
          __crsql_site_id
        ) SELECT
          NEW."a",
          'c',
          1,
          crsql_next_db_version(),
          crsql_increment_and_get_seq(),
          NULL
        ON CONFLICT DO UPDATE SET
          __crsql_col_version = __crsql_col_version + 1,
          __crsql_db_version = crsql_next_db_version(),
          __crsql_seq = crsql_get_seq() - 1,
          __crsql_site_id = NULL;
INSERT INTO "baz__crsql_clock" (
          "a",
          __crsql_col_name,
          __crsql_col_version,
          __crsql_db_version,
          __crsql_seq,
          __crsql_site_id
        ) SELECT
          NEW."a",
          'd',
          1,
          crsql_next_db_version(),
          crsql_increment_and_get_seq(),
          NULL
        ON CONFLICT DO UPDATE SET
          __crsql_col_version = __crsql_col_version + 1,
          __crsql_db_version = crsql_next_db_version(),
          __crsql_seq = crsql_get_seq() - 1,
          __crsql_site_id = NULL;
      END;
CREATE TRIGGER "baz_a__crsql_utrig"
          AFTER UPDATE OF "a" ON "baz"
          WHEN crsql_internal_sync_bit() = 0 AND NEW."a" IS NOT OLD."a"
          BEGIN
            INSERT INTO "baz__crsql_clock" (
              "a",
              __crsql_col_name,
              __crsql_col_version,
              __crsql_db_version,
              __crsql_seq,
              __crsql_site_id
            ) SELECT
              OLD."a",
              '-1',
              2,
              crsql_next_db_version(),
              crsql_increment_and_get_seq(),
              NULL WHERE true
            ON CONFLICT DO UPDATE SET
              __crsql_col_version = 1 + __crsql_col_version,
              __crsql_db_version = crsql_next_db_version(),
              __crsql_seq = crsql_get_seq() - 1,
              __crsql_site_id = NULL;
            DELETE FROM "baz__crsql_clock"
              WHERE "a" IS OLD."a" AND __crsql_col_name != '-1';
          END;
CREATE TRIGGER "baz__crsql_utrig"
      AFTER UPDATE ON "baz" WHEN crsql_internal_sync_bit() = 0
      BEGIN
        INSERT INTO "baz__crsql_clock" (
          "a",
          __crsql_col_name,
          __crsql_col_version,
          __crsql_db_version,
          __crsql_seq,
          __crsql_site_id
        ) SELECT
          NEW."a",
          '-1',
          1,
          crsql_next_db_version(),
          crsql_increment_and_get_seq(),
          NULL
        WHERE NEW."a" IS NOT OLD."a"
        ON CONFLICT DO UPDATE SET
          __crsql_col_version = CASE __crsql_col_version % 2 WHEN 0 THEN __crsql_col_version + 1 ELSE __crsql_col_version + 2 END,
          __crsql_db_version = crsql_next_db_version(),
          __crsql_seq = crsql_get_seq() - 1,
          __crsql_site_id = NULL;
INSERT INTO "baz__crsql_clock" (
          "a",
          __crsql_col_name,
          __crsql_col_version,
          __crsql_db_version,
          __crsql_seq,
          __crsql_site_id
        ) SELECT
          NEW."a",
          'b',
          1,
          crsql_next_db_version(),
          crsql_increment_and_get_seq(),
          NULL
        WHERE NEW."b" IS NOT OLD."b"
        ON CONFLICT DO UPDATE SET
          __crsql_col_version = __crsql_col_version + 1,
          __crsql_db_version = crsql_next_db_version(),
          __crsql_seq = crsql_get_seq() - 1,
          __crsql_site_id = NULL;
INSERT INTO "baz__crsql_clock" (
          "a",
          __crsql_col_name,
          __crsql_col_version,
          __crsql_db_version,
          __crsql_seq,
          __crsql_site_id
        ) SELECT
          NEW."a",
          'c',
          1,
          crsql_next_db_version(),
          crsql_increment_and_get_seq(),
          NULL
        WHERE NEW."c" IS NOT OLD."c"
        ON CONFLICT DO UPDATE SET
          __crsql_col_version = __crsql_col_version + 1,
          __crsql_db_version = crsql_next_db_version(),
          __crsql_seq = crsql_get_seq() - 1,
          __crsql_site_id = NULL;
INSERT INTO "baz__crsql_clock" (
          "a",
          __crsql_col_name,
          __crsql_col_version,
          __crsql_db_version,
          __crsql_seq,
          __crsql_site_id
        ) SELECT
          NEW."a",
          'd',
          1,
          crsql_next_db_version(),
          crsql_increment_and_get_seq(),
          NULL
        WHERE NEW."d" IS NOT OLD."d"
        ON CONFLICT DO UPDATE SET
          __crsql_col_version = __crsql_col_version + 1,
          __crsql_db_version = crsql_next_db_version(),
          __crsql_seq = crsql_get_seq() - 1,
          __crsql_site_id = NULL;
      END;
CREATE TRIGGER "baz__crsql_dtrig"
    AFTER DELETE ON "baz" WHEN crsql_internal_sync_bit() = 0
    BEGIN
      INSERT INTO "baz__crsql_clock" (
        "a",
        __crsql_col_name,
        __crsql_col_version,
        __crsql_db_version,
        __crsql_seq,
        __crsql_site_id
      ) SELECT
        OLD."a",
        '-1',
        2,
        crsql_next_db_version(),
        crsql_increment_and_get_seq(),
        NULL WHERE true
      ON CONFLICT DO UPDATE SET
        __crsql_col_version = 1 + __crsql_col_version,
        __crsql_db_version = crsql_next_db_version(),
        __crsql_seq = crsql_get_seq() - 1,
        __crsql_site_id = NULL;
      DELETE FROM "baz__crsql_clock"
        WHERE "a" IS OLD."a" AND __crsql_col_name != '-1';
    END;
```
## Explained (a bit) by GPT-4

And just because I can, using [LLM](https://llm.datasette.io/):

```bash
sqlite3 /tmp/temp.db .schema | llm -m gpt-4 -s 'explain this SQL, with a villainous twist'
```
Outputs:

> This SQL script is establishing database tables and setting up triggers for tracking changes to the database. The villainous twist here is that it's designed to covertly track every change made to certain database tables ("foo" and "baz"), including inserts, updates, and deletions. The changes are logged in system tables ("crsql_tracked_peers", "crsql_master", "crsql_site_id", "foo__crsql_clock", "baz__crsql_clock") and tracked with various specific criteria ("__crsql_col_version", "__crsql_db_version", "__crsql_seq", "__crsql_site_id").
>
> The "foo" and "baz" tables represent databases the villain would like to monitor. The script will create these tables if they don't exist and is also adding triggers to them.
>
> Triggers are procedures that are automatically executed in response to certain events (e.g., insertions, updates, or deletions) on a particular table. 
>
> So the villainous twist is that after every INSERT, UPDATE, or DELETE operation on "foo" or "baz" tables, these changes are tracked and stored in "__crsql_clock" tables.
>
> When a row is inserted into "foo" or "baz", the "foo__crsql_itrig" or "baz__crsql_itrig" triggers fire. They update certain fields in the "foo__crsql_clock" or "baz__crsql_clock" tables and insert new rows if necessary.
>
> When a row is updated in "foo" or "baz", "foo__crsql_utrig" or "baz__crsql_utrig" triggers fire, doing the same thing but additionally checking if value of "a" was changed.  
>
> When a row is deleted from "foo" or "baz", "foo__crsql_dtrig" or "baz__crsql_dtrig" triggers run. They insert info about deleted row into "foo__crsql_clock" or "baz__crsql_clock" tables, and delete rows associated with that object.
>
> The villain's script is making sure no change goes unnoticed. If you don't know the triggers are there, you may never realize what's happening!
