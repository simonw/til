# Using the sqlite3 Python module in Pyodide - Python WebAssembly

[Pyodide](https://github.com/pyodide/pyodide) provides "Python with the scientific stack, compiled to WebAssembly" - it's an incredible project which lets you run a full working Jupyter notebook, complete with complex packages such as numpy and pandas, entirely in your browser without any server-side Python component running at all.

It turns out it also now includes [a working version](https://github.com/pyodide/pyodide/issues/345) of the standard library `sqlite3` module, by bundling a WebAssembly compiled version of SQLite!

## Trying this in the REPL

[pyodide.org/en/stable/console.html](https://pyodide.org/en/stable/console.html) provides an interactive REPL for trying eut Pyodide. You can run a one-liner to demonstrate the available SQLite version like this:

```pycon
Welcome to the Pyodide terminal emulator 🐍
Python 3.9.5 (default, Sep 16 2021 11:22:45) on WebAssembly VM
Type "help", "copyright", "credits" or "license" for more information.
>>> import sqlite3
>>> sqlite3.connect(":memory:").execute("select sqlite_version()").fetchall()
[('3.27.2',)]
```

## Querying an existing database file from JupyterLite

[JupyterLite](https://blog.jupyter.org/jupyterlite-jupyter-%EF%B8%8F-webassembly-%EF%B8%8F-python-f6e2e41ab3fa) is "a JupyterLab distribution that runs entirely in the web browser, backed by in-browser language kernels."

Their online demo is at [jupyterlite.github.io/demo/lab/index.html](https://jupyterlite.github.io/demo/lab/index.html). I opened that demo and created a new Pyolite notebook there, then used the bridge to the JavaScript `fetch()` function to download the 11MB [power plants database file](https://global-power-plants.datasettes.com/global-power-plants) from this URL:

`https://global-power-plants.datasettes.com/global-power-plants.db`

(Downloading this via `fetch()` works because Datasette includes CORS headers for these files.)

```python
from js import fetch

res = await fetch("https://global-power-plants.datasettes.com/global-power-plants.db")
buffer = await res.arrayBuffer()

# Now write that to the in-memory simulated filesystem:
open("tmp/power.db", "wb").write(bytes(buffer.valueOf().to_py()))

# And run some queries against it:
import sqlite3
c = sqlite3.connect("tmp/power.db")
c.execute('select * from "global-power-plants" limit 10').fetchall()
```
This works!

<img width="1546" alt="Screenshot of JupyterLite running my example code" src="https://user-images.githubusercontent.com/9599/137788071-c39bbdbb-7d8d-464e-9729-ad1c63bb8be8.png">

