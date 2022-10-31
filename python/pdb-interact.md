# The pdb interact command

Today [Carlton told me](https://twitter.com/carltongibson/status/1587155176590385159) about the [interact command](https://docs.python.org/3.10/library/pdb.html#pdbcommand-interact) in the Python debugger.

Here's how to use it with `pytest` (but it works anywhere else where you find yourself in a `pdb` session).

Use `pytest --pdb` to cause `pytest` to open a debugger at the first failed assertion (I added `assert False` to my test suite to demonstrate this).

Then type `interact` to drop into a full Python interactive prompt that keeps all of the local and global variables from the debugger:

```
% pytest -k test_drop --pdb                                               
======== test session starts ========
platform darwin -- Python 3.10.3, pytest-7.1.3, pluggy-1.0.0
...
>       assert False
E       assert False

tests/test_api_write.py:272: AssertionError
>>>> entering PDB >>>>

>>>> PDB post_mortem (IO-capturing turned off) >>>>
> /Users/simon/Dropbox/Development/datasette/tests/test_api_write.py(272)test_drop_table()
-> assert False
(Pdb) interact
>>> locals().keys()
dict_keys(['__name__', '__doc__', '__package__', '__loader__', '__spec__', '__file__', '__cached__', '__builtins__',
  '@py_builtins', '@pytest_ar', 'Datasette', 'sqlite3', 'pytest', 'time', 'ds_write', 'write_token', 'test_write_row',
  'test_write_rows', 'test_write_row_errors', 'test_delete_row', 'test_drop_table', 'scenario', 'token', 'should_work',
  'path', 'response', '@py_assert0', '@py_format2'])
```
Crucially, once you are in the interactive prompt you can inspect local variables with names like `s` and `c` without accidentally triggering matching debugger commands.

Hit `Ctrl+D` to exit back to the debugger:

```
>>> <Ctrl+D>
now exiting InteractiveConsole...
(pdb)
```
