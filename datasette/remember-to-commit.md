# Remember to commit when using datasette.execute_write_fn()

I was writing some code for [datasette-auth-tokens](https://github.com/simonw/datasette-auth-tokens) that used [db.execute_write_fn()](https://docs.datasette.io/en/stable/internals.html#await-db-execute-write-fn-fn-block-true) like this:

```python
def expire_tokens(conn):
    # Expire all tokens that are due to expire
    conn.execute(
        """
        update _datasette_auth_tokens
        set token_status = 'E', ended_timestamp = :now
        where token_status = 'A'
        and expires_after_seconds is not null
        and (created_timestamp + expires_after_seconds) < :now
    """, {"now": int(time.time())})

await db.execute_write_fn(expire_tokens)
```
But I got this **database table is locked** error when I ran the tests:

```
  File ".../datasette/database.py", line 228, in in_thread
    return fn(conn)
           ^^^^^^^^
  File ".../datasette/database.py", line 254, in sql_operation_in_thread
    cursor.execute(sql, params if params is not None else {})
sqlite3.OperationalError: database table is locked: _datasette_auth_tokens
```

The fix was to add an explicit commit within that write function:
```python
def expire_tokens(conn):
    # Expire all tokens that are due to expire
    conn.execute(
        """
        update _datasette_auth_tokens
        set token_status = 'E', ended_timestamp = :now
        where token_status = 'A'
        and expires_after_seconds is not null
        and (created_timestamp + expires_after_seconds) < :now
    """, {"now": int(time.time())})
    db.commit()
```
I think the right rule of thumb here is to _always_ explicitly commit in any Datasette code that makes writes to the database in this way.
