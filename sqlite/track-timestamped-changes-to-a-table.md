# Track timestamped changes to a SQLite table using triggers

This is more of a "today I figured out" than a TIL.

I have an idea to implement the [Denormalized Query Engine design pattern](https://2017.djangocon.us/talks/the-denormalized-query-engine-design-pattern/) using SQLite triggers.

My goal is that any time an insert or update occurs on a table, a matching row will be written to a `_dqe_changes` table recording the rowid of the affected row and the unix timestamp (in milliseconds) that the change occurred.

If a row is deleted, a record will be written into tha table with a `1` in the `deleted` column.

This will allow subscribing scripts to poll that table for changes made since their last poll, based on the milliseconds timestamp field. They can then apply those changes to external data stores, such as an Elasticsearch index.

Here's the recipe I came up with:

```sql
-- This table exists just for table -> integer lookups,
-- to save space in the _dqe_changes table
CREATE TABLE _dqe_tables(
  id integer primary key,
  [table] text unique
);
-- This table records the timestamped changes
CREATE TABLE _dqe_changes(
  table_id integer,
  rowid integer,
  deleted integer, -- treated as a null or 1 boolean
  updated_ms integer,
  PRIMARY KEY (table_id, rowid),
  FOREIGN KEY (table_id) REFERENCES _dqe_tables(id)
);
-- Create an index for polling against
CREATE INDEX _dqe_changes_updated_ms ON _dqe_changes(updated_ms);

-- An example table:
CREATE TABLE foo (name text);

-- Each table needs to have these triggers created on it:
CREATE TRIGGER IF NOT EXISTS [foo_dqe_insert] AFTER INSERT ON [foo]
BEGIN
  INSERT OR IGNORE INTO _dqe_tables([table]) VALUES ('foo');
  INSERT OR REPLACE INTO _dqe_changes(table_id, rowid, updated_ms)
     VALUES (
        (select id from _dqe_tables where [table] = 'foo'),
        new.rowid,
        -- This is a recipe for timestamp in milliseconds, from
        -- https://stackoverflow.com/a/56895050/6083 
        strftime('%s','now') || substr(strftime('%f','now'),4)
    );
END;
CREATE TRIGGER IF NOT EXISTS [foo_dqe_update] AFTER UPDATE ON [foo]
BEGIN
  INSERT OR IGNORE INTO _dqe_tables([table]) VALUES ('foo');
  INSERT OR REPLACE INTO _dqe_changes(table_id, rowid, updated_ms)
     VALUES (
        (select id from _dqe_tables where [table] = 'foo'),
        new.rowid,
        strftime('%s','now') || substr(strftime('%f','now'),4)
    );
END;
CREATE TRIGGER IF NOT EXISTS [foo_dqe_delete] AFTER DELETE ON [foo]
BEGIN
  INSERT OR IGNORE INTO _dqe_tables([table]) VALUES ('foo');
  INSERT OR REPLACE INTO _dqe_changes(table_id, rowid, deleted, updated_ms)
     VALUES (
        (select id from _dqe_tables where [table] = 'foo'),
        old.rowid,
        1,
        strftime('%s','now') || substr(strftime('%f','now'),4)
    );
END;

INSERT INTO foo VALUES ('hello');
INSERT INTO foo VALUES ('hello2');
INSERT INTO foo VALUES ('hello3');
INSERT INTO foo VALUES ('hello4');
```
To test this I ran `sqlite3` (with no arguments, which provides an in-memory database to play with), pasted in the above and then ran this:
```
sqlite> .headers on
sqlite> select rowid, * from foo;
rowid|name
1|hello
2|hello2
3|hello3
4|hello4
sqlite> select * from _dqe_changes;
table_id|rowid|deleted|updated_ms
1|1||1629399072866
1|2||1629399072867
1|3||1629399072867
1|4||1629399072974
sqlite> select * from _dqe_tables;
id|table
1|foo
sqlite> delete from foo where name = 'hello3';
sqlite> select * from _dqe_changes;
table_id|rowid|deleted|updated_ms
1|1||1629399072866
1|2||1629399072867
1|4||1629399072974
1|3|1|1629399103169
sqlite> update foo set name = 'hello6' where name = 'hello';
sqlite> select * from _dqe_changes;
table_id|rowid|deleted|updated_ms
1|2||1629399072867
1|4||1629399072974
1|3|1|1629399103169
1|1||1629399115886
sqlite> select rowid, * from foo;
rowid|name
1|hello6
2|hello2
4|hello4
```
There's one catch with the above recipe: if you delete ALL of the rows from a table (`delete * from foo`) SQLite defaults to reusing rowids in that table, starting again from 1. This means that your accompanying records in the `_dqe_changes` table will have stale rowids, which could lead to surprising behaviour.

If tables have a `id integer primary key` column SQLite does NOT reuse rowids, [as explained here](https://www.sqlite.org/autoinc.html).
