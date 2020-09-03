# Debugging a Click application using pdb

If you're working on a Python Click application and it throws an exception:

```
% dogsheep-beta index beta.db dogsheep-beta.yml 
Traceback (most recent call last):
...
  File "/Users/simon/Dropbox/Development/dogsheep-beta/dogsheep_beta/utils.py", line 46, in run_indexer
    columns = derive_columns(other_db, sql)
  File "/Users/simon/Dropbox/Development/dogsheep-beta/dogsheep_beta/utils.py", line 63, in derive_columns
    cursor = db.conn.execute(sql + " limit 0")
sqlite3.OperationalError: near "from": syntax error
```

You can run the Python debugger against it using `python -i $(which dogsheep-beta)` to get an interactive prompt, then `import pdb; pdb.pm()` to open the debugger at the last exception:

```
% python -i $(which dogsheep-beta) index beta.db dogsheep-beta.yml
Traceback (most recent call last):
  File "/Users/simon/.local/share/virtualenvs/dogsheep-beta-u_po4Rpj/bin/dogsheep-beta", line 11, in <module>
    load_entry_point('dogsheep-beta', 'console_scripts', 'dogsheep-beta')()
  File "/Users/simon/.local/share/virtualenvs/dogsheep-beta-u_po4Rpj/lib/python3.8/site-packages/click/core.py", line 829, in __call__
    return self.main(*args, **kwargs)
  File "/Users/simon/.local/share/virtualenvs/dogsheep-beta-u_po4Rpj/lib/python3.8/site-packages/click/core.py", line 782, in main
    rv = self.invoke(ctx)
  File "/Users/simon/.local/share/virtualenvs/dogsheep-beta-u_po4Rpj/lib/python3.8/site-packages/click/core.py", line 1259, in invoke
    return _process_result(sub_ctx.command.invoke(sub_ctx))
  File "/Users/simon/.local/share/virtualenvs/dogsheep-beta-u_po4Rpj/lib/python3.8/site-packages/click/core.py", line 1066, in invoke
    return ctx.invoke(self.callback, **ctx.params)
  File "/Users/simon/.local/share/virtualenvs/dogsheep-beta-u_po4Rpj/lib/python3.8/site-packages/click/core.py", line 610, in invoke
    return callback(*args, **kwargs)
  File "/Users/simon/Dropbox/Development/dogsheep-beta/dogsheep_beta/cli.py", line 30, in index
    run_indexer(db_path, rules, tokenize=None if tokenize == "none" else tokenize)
  File "/Users/simon/Dropbox/Development/dogsheep-beta/dogsheep_beta/utils.py", line 46, in run_indexer
    columns = derive_columns(other_db, sql)
  File "/Users/simon/Dropbox/Development/dogsheep-beta/dogsheep_beta/utils.py", line 63, in derive_columns
    cursor = db.conn.execute(sql + " limit 0")
sqlite3.OperationalError: near "from": syntax error
>>> import pdb; pdb.pm()
> /Users/simon/Dropbox/Development/dogsheep-beta/dogsheep_beta/utils.py(63)derive_columns()
-> cursor = db.conn.execute(sql + " limit 0")
(Pdb) print(sql)
...
```
