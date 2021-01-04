# Packaging a Python app as a standalone binary with PyInstaller

[PyInstaller](https://www.pyinstaller.org/) can take a Python script and bundle it up as a standalone executable for macOS, Linux and apparently Windows too (I've not tried it on Windows yet).

Today I managed to build [Datasette](https://datasette.io/) executables for macOS and Linux using the following recipe:

```bash
export DATASETTE_BASE=$(python -c 'import os; print(os.path.dirname(__import__("datasette").__file__))') \
pyinstaller -F \
    --add-data "$DATASETTE_BASE/templates:datasette/templates" \
    --add-data "$DATASETTE_BASE/static:datasette/static" \
    --hidden-import datasette.publish \
    --hidden-import datasette.publish.heroku \
    --hidden-import datasette.publish.cloudrun \
    --hidden-import datasette.facets \
    --hidden-import datasette.sql_functions \
    --hidden-import datasette.actor_auth_cookie \
    --hidden-import datasette.default_permissions \
    --hidden-import datasette.default_magic_parameters \
    --hidden-import datasette.blob_renderer \
    --hidden-import datasette.default_menu_links \
    --hidden-import uvicorn \
    --hidden-import uvicorn.logging \
    --hidden-import uvicorn.loops \
    --hidden-import uvicorn.loops.auto \
    --hidden-import uvicorn.protocols \
    --hidden-import uvicorn.protocols.http \
    --hidden-import uvicorn.protocols.http.auto \
    --hidden-import uvicorn.protocols.websockets \
    --hidden-import uvicorn.protocols.websockets.auto \
    --hidden-import uvicorn.lifespan \
    --hidden-import uvicorn.lifespan.on \
    $(which datasette)
```

The `--hidden-import` lines are needed because PyInstaller attempts to follow the module import graph for a package, but is very easily confused. Datasette dynamically imports [a list of default plugins](https://github.com/simonw/datasette/blob/ab7767acbe021ed6ab0a8d4b56ec8b4af6ae9e86/datasette/plugins.py#L7-L17) so I had to explicitly list each of those. I don't know what's going on with `uvicorn` here - I kept on running the script and then running `dist/datasette` and getting errors like this one:

```
(pyinstaller-datasette) pyinstaller-datasette % dist/datasette ~/Dropbox/Development/datasette/fixtures.db
Traceback (most recent call last):
  File "datasette", line 8, in <module>
  File "click/core.py", line 829, in __call__
  File "click/core.py", line 782, in main
  File "click/core.py", line 1259, in invoke
  File "click/core.py", line 1066, in invoke
  File "click/core.py", line 610, in invoke
  File "datasette/cli.py", line 548, in serve
  File "uvicorn/main.py", line 386, in run
  File "uvicorn/server.py", line 48, in run
  File "asyncio/base_events.py", line 642, in run_until_complete
  File "uvicorn/server.py", line 55, in serve
  File "uvicorn/config.py", line 301, in load
  File "uvicorn/importer.py", line 23, in import_from_string
  File "uvicorn/importer.py", line 20, in import_from_string
  File "importlib/__init__.py", line 127, in import_module
  File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
  File "<frozen importlib._bootstrap>", line 972, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
  File "<frozen importlib._bootstrap>", line 1030, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1007, in _find_and_load
  File "<frozen importlib._bootstrap>", line 984, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'uvicorn.protocols.websockets'
[32142] Failed to execute script datasette
```

I solved this by adding each `ModuleNotFoundError` module to `--hidden-import` until it worked.

I've tested this script (and the generated executables) on both macOS and Ubuntu Linux so far, and it's worked perfectly in both cases. See [issue 93](https://github.com/simonw/datasette/issues/93) for more details.
