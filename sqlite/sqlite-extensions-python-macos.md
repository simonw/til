# Loading SQLite extensions in Python on macOS

I finally found a workaround for this error when attempting to load a SQLite extension in Python on macOS:

```
  File "/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages/datasette/app.py", line 614, in _prepare_connection
    conn.enable_load_extension(True)
AttributeError: 'sqlite3.Connection' object has no attribute 'enable_load_extension'
```

The fix is to install Python using Homebrew, and then use **that** version of Python.

    brew install python

This gives you a version of Python that can load SQLite extensions. The problem is there is a good chance that when you type `python` that's not the version you will get.

One way to fix that is to run the Homebrew Python directly like this:

    /usr/local/opt/python@3/libexec/bin/python

You can create a virtual environment with that Python version like so:

    /usr/local/opt/python@3/libexec/bin/python -m venv my-venv
    source my-venv/bin/activate

Then within that virtual environment any time you run `python` (or install extra tools using `pip`) they will use the correct version of Python and will be able to load extensions.

I expanded this TIL into a section of the Datasette documentation here: https://datasette.io/help/extensions
