# Tracking SQLite table history using a JSON audit log

I continue to collect ways of tracking the history of a table of data stored in SQLite - see [sqlite-history](https://simonwillison.net/2023/Apr/15/sqlite-history/) for previous experiments.

Today I decided to try a slightly different approach, using JSON to store changes to a table in an audit log.

I wanted an audit table design that looked something like this:

id | timestamp | row_id | previous_values
--- | --- | --- | ---
1 | 2023-04-15 12:00:00 | 1 | {"name": "Old Name", "age": 42}
2 | 2023-04-15 12:00:01 | 1 | {"age": 37}

Any time a table is updated I want to record a JSON object that contains just the columns that were changed, reflecting their previous values.

I didn't think it was possible to construct such a JSON object using just the SQL dialect supported by SQLite triggers... but with a _lot_ of assistance from ChatGPT Code Interpreter (which could prototype things for me while I was out walking the dog) I found a combination of SQL function calls that works.

Here's what I ended up with:

```sql
CREATE TABLE demo (
    id INTEGER PRIMARY KEY,
    text_col TEXT,
    int_col INTEGER,
    float_col FLOAT,
    blob_col BLOB
);
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    row_id INTEGER,
    previous_values TEXT
);
CREATE TRIGGER audit_log_trigger
AFTER UPDATE ON demo
BEGIN
    INSERT INTO audit_log (timestamp, row_id, previous_values) VALUES (
        datetime('now'),
        NEW.id,
        json_patch(
            json_patch(
                json_patch(
                    json_patch(
                        '{}',
                        CASE
                            WHEN OLD.text_col IS NOT NEW.text_col THEN
                                CASE
                                    WHEN OLD.text_col IS NULL THEN json_object('text_col', json_object('null', 1))
                                    ELSE json_object('text_col', OLD.text_col)
                                END
                            ELSE '{}'
                        END
                    ),
                    CASE
                        WHEN OLD.int_col IS NOT NEW.int_col THEN
                            CASE
                                WHEN OLD.int_col IS NULL THEN json_object('int_col', json_object('null', 1))
                                ELSE json_object('int_col', OLD.int_col)
                            END
                        ELSE '{}'
                    END
                ),
                CASE
                    WHEN OLD.float_col IS NOT NEW.float_col THEN
                        CASE
                            WHEN OLD.float_col IS NULL THEN json_object('float_col', json_object('null', 1))
                            ELSE json_object('float_col', OLD.float_col)
                        END
                    ELSE '{}'
                END
            ),
            CASE
                WHEN OLD.blob_col IS NOT NEW.blob_col THEN
                    CASE
                        WHEN OLD.blob_col IS NULL THEN json_object('blob_col', json_object('null', 1))
                        ELSE json_object('blob_col', json_object('hex', hex(OLD.blob_col)))
                    END
                ELSE '{}'
            END
        )
    );
END;

-- Trying that out
INSERT INTO demo (
    text_col, int_col, float_col, blob_col
) VALUES (
    'Hello', 42, 3.14, x'0102030405060708'
);
UPDATE demo SET text_col = 'World', int_col = 37;
UPDATE demo SET float_col = null;
UPDATE demo SET blob_col = x'0807060504030201';
UPDATE demo SET float_col = 2.71828;
```
And now:
```sql
select * from audit_log;
```

id | timestamp | row_id | previous_values
---|---|---|---
1|2024-02-27 01:34:50|1|`{"text_col": "Hello", "int_col": 42}`
2|2024-02-27 01:34:50|1|`{"float_col": 3.14}`
3|2024-02-27 01:34:50|1|`{"blob_col": {"hex": "0102030405060708"}}`
4|2024-02-27 01:34:50|1|`{"float_col": {"null": 1}}`

There's a lot of stuff going on here!

I had to change the design of the `previous_values` column a bit. Firstly, it turns out you can't store a binary value in a JSON document - so I invented the following syntax for that instead:

```json
{"blob_col": {"hex": "0102030405060708"}}
```
This means that the `blob_col` column was changed, and its previous value was the binary value that can be represented in hex as `0102030405060708`.

I needed special handling for null values as well, which I did like this:

```json
{"float_col": {"null": 1}}
```
This means that the `float_col` column was changed, and its previous value was `null`. I needed to do this because of how the `json_patch()` function worked, described below.

## Building a JSON object representing the changes

The bulk of the complexity in the SQL above relates to how the JSON string that shows which values were changed is constructed.

It works using a nested sequence of calls to the [json_patch() function](https://www.sqlite.org/json1.html#jpatch), which is a SQLite built-in that can combine two JSON objects together.

Let's consider the inner-most nested call:

```sql
json_patch(
    '{}',
    CASE
        WHEN OLD.text_col IS NOT NEW.text_col THEN
            CASE
                WHEN OLD.text_col IS NULL THEN json_object('text_col', json_object('null', 1))
                ELSE json_object('text_col', OLD.text_col)
            END
        ELSE '{}'
    END
)
```
This takes the empty object, `{}`, and merges it with a second object which is either `{}` (if the old and new values were the same), or a JSON object containing the old value of the `text_col` column.

There's a nested `CASE` statement there too to handle the null case: if the previous value is `null` we need to store `{"text_col": {"null": 1}}` instead of `{"text_col": null}`.

That's because `json_patch()` treats `null` as a value that means the key should not be included - which isn't what we want here.

This `json_patch()` unit means we can compare the old and new values and return either an empty object for no-changes or an object containing the column name and the old value.

Nesting those `json_patch()` calls together is the only way I found of building an object that catches changes made to any of the columns in the table.

## An alternative: record the new values

My first design recorded the old values every time a row was updated. This saves a tiny bit of space - a row that is inserted but never updated doesn't need any audit log entries - but makes the act of restoring a previous state more complex. You have to start at the most recent state and then apply all the changes in reverse order. Also, if you only have a copy of the audit table it's not enough information to restore the original table.

Here's an alternative approach - this time recording the new values every time a row is inserted or updated. This requires an insert trigger in addition to an update trigger:

```sql
CREATE TABLE demo (
    id INTEGER PRIMARY KEY,
    text_col TEXT,
    int_col INTEGER,
    float_col FLOAT,
    blob_col BLOB
);
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY,
    timestamp TEXT,
    row_id INTEGER,
    updated_values TEXT
);
CREATE TRIGGER audit_log_trigger
AFTER UPDATE ON demo
BEGIN
    INSERT INTO audit_log (timestamp, row_id, updated_values) VALUES (
        datetime('now'),
        NEW.id,
        json_patch(
            json_patch(
                json_patch(
                    json_patch(
                        '{}',
                        CASE
                            WHEN OLD.text_col IS NOT NEW.text_col THEN
                                CASE
                                    WHEN NEW.text_col IS NULL THEN json_object('text_col', json_object('null', 1))
                                    ELSE json_object('text_col', NEW.text_col)
                                END
                            ELSE '{}'
                        END
                    ),
                    CASE
                        WHEN OLD.int_col IS NOT NEW.int_col THEN
                            CASE
                                WHEN NEW.int_col IS NULL THEN json_object('int_col', json_object('null', 1))
                                ELSE json_object('int_col', NEW.int_col)
                            END
                        ELSE '{}'
                    END
                ),
                CASE
                    WHEN OLD.float_col IS NOT NEW.float_col THEN
                        CASE
                            WHEN NEW.float_col IS NULL THEN json_object('float_col', json_object('null', 1))
                            ELSE json_object('float_col', NEW.float_col)
                        END
                    ELSE '{}'
                END
            ),
            CASE
                WHEN OLD.blob_col IS NOT NEW.blob_col THEN
                    CASE
                        WHEN NEW.blob_col IS NULL THEN json_object('blob_col', json_object('null', 1))
                        ELSE json_object('blob_col', json_object('hex', hex(NEW.blob_col)))
                    END
                ELSE '{}'
            END
        )
    );
END;

CREATE TRIGGER audit_log_insert_trigger
AFTER INSERT ON demo
BEGIN
    INSERT INTO audit_log (timestamp, row_id, updated_values) VALUES (
        datetime('now'),
        NEW.id,
        json_object(
            'text_col',
            CASE WHEN NEW.text_col IS NULL THEN json_object('null', 1) ELSE NEW.text_col END,
            'int_col',
            CASE WHEN NEW.int_col IS NULL THEN json_object('null', 1) ELSE NEW.int_col END,
            'float_col',
            CASE WHEN NEW.float_col IS NULL THEN json_object('null', 1) ELSE NEW.float_col END,
            'blob_col',
            CASE WHEN NEW.blob_col IS NULL THEN json_object('null', 1) ELSE json_object('hex', hex(NEW.blob_col)) END
        )
    );
END;

-- Trying that out
INSERT INTO demo (
    text_col, int_col, float_col, blob_col
) VALUES (
    'Hello', 42, 3.14, x'0102030405060708'
);
UPDATE demo SET text_col = 'World', int_col = 37;
UPDATE demo SET float_col = null;
UPDATE demo SET blob_col = x'0807060504030201';
UPDATE demo SET float_col = 2.71828;
```
The result is an `audit_log` table containing the following:

id | timestamp | row_id | updated_values
---|---|---|---
1|2024-02-27 01:51:44|1|`{"text_col": "Hello", "int_col": 42, "float_col": 3.14, "blob_col": {"hex": "0102030405060708"}}`
2|2024-02-27 01:51:54|1|`{"text_col": "World", "int_col": 37}`
3|2024-02-27 01:51:54|1|`{"float_col": {"null": 1}}`
4|2024-02-27 01:51:54|1|`{"blob_col": {"hex": "0807060504030201"}}`
5|2024-02-27 01:51:54|1|`{"float_col": 2.71828}`

## Next step: automate it with Python

The biggest problem with this approach is that writing those SQL triggers is extremely hazardous - I fought through _so many_ not-specific-enough SQL syntax errors getting the above to work.

To make this system workable, the process of writing the triggers needs to be automated. I've done that [once before for sqlite-history](https://github.com/simonw/sqlite-history/blob/0.1/sqlite_history/sql.py#L26-L101), so I imagine code to build the nested `json_patch()` triggers here would look somewhat similar.
