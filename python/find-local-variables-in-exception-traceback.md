# Find local variables in the traceback for an exception

For [sqlite-utils issue #309](https://github.com/simonw/sqlite-utils/issues/309) I had an error that looked like this:
```
OverflowError: Python int too large to convert to SQLite INTEGER
Traceback (most recent call last):
  File "/home/sean/.local/bin/sqlite-utils", line 8, in <module>
    sys.exit(cli())
  [...]
  File "/home/sean/.local/lib/python3.8/site-packages/sqlite_utils/db.py", line 257, in execute
    return self.conn.execute(sql, parameters)
```
And I wanted to display the values of the `sql` and `parameters` variables as part of a custom error message.

It turns out Python exceptions have a `e.__traceback__` property which provides access to a traceback - and the local variables in that traceback are avialable on the `tb.tb_frame.f_locals` dictionary - or if not that one, the `tb.tb_next.tb_frame.f_locals` property and so on up to the top of the stack.

I wrote this function to find them:

```python
def _find_variables(tb, vars):
    to_find = list(vars)
    found = {}
    for var in to_find:
        if var in tb.tb_frame.f_locals:
            vars.remove(var)
            found[var] = tb.tb_frame.f_locals[var]
    if vars and tb.tb_next:
        found.update(_find_variables(tb.tb_next, vars))
    return found
```

Use it like this:

```python
    try:
        db[table].insert_all(
            docs, pk=pk, batch_size=batch_size, alter=alter, **extra_kwargs
        )
    except Exception as e:
        # If we can find sql= and params= arguments, show those
        variables = _find_variables(e.__traceback__, ["sql", "params"])
        if "sql" in variables and "params" in variables:
            raise click.ClickException(
                "{}\n\nsql = {}\nparams={}".format(
                    str(e), variables["sql"], variables["params"]
                )
            )
        else:
            raise
```
[Full commit](https://github.com/simonw/sqlite-utils/commit/14f643d9e91f5557d5e46251dadac481f4b41021) add this to `sqlite-utils`.
