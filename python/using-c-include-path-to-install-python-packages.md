# Using C_INCLUDE_PATH to install Python packages

I tried to install my [datasette-bplist](https://github.com/simonw/datasette-bplist) plugin today in a fresh Python 3.10 virtual environment on macOS and got this error:

```
% pip install datasette-bplist
...
    src/bplist.c:2:10: fatal error: 'pytime.h' file not found
    #include <pytime.h>
             ^~~~~~~~~~
    1 error generated.
    error: command '/usr/bin/clang' failed with exit code 1
    ----------------------------------------
ERROR: Command errored out with exit status 1: /Users/simon/.local/share/virtualenvs/datasette-nska-phcxS5VC/bin/python -u -c 'import io, os, sys, setuptools, tokenize; sys.argv[0] = '"'"'/private/var/folders/wr/hn3206rs1yzgq3r49bz8nvnh0000gn/T/pip-install-8vbksayc/bpylist_af584b1da32f4f7ea8f6eb8548355128/setup.py'"'"'; __file__='"'"'/private/var/folders/wr/hn3206rs1yzgq3r49bz8nvnh0000gn/T/pip-install-8vbksayc/bpylist_af584b1da32f4f7ea8f6eb8548355128/setup.py'"'"';f = getattr(tokenize, '"'"'open'"'"', open)(__file__) if os.path.exists(__file__) else io.StringIO('"'"'from setuptools import setup; setup()'"'"');code = f.read().replace('"'"'\r\n'"'"', '"'"'\n'"'"');f.close();exec(compile(code, __file__, '"'"'exec'"'"'))' install --record /private/var/folders/wr/hn3206rs1yzgq3r49bz8nvnh0000gn/T/pip-record-2m2ya37u/install-record.txt --single-version-externally-managed --compile --install-headers /Users/simon/.local/share/virtualenvs/datasette-nska-phcxS5VC/include/site/python3.10/bpylist Check the logs for full command output.
```
Thanks [to StackOverflow](https://stackoverflow.com/questions/35778495/fatal-error-python-h-file-not-found-while-installing-opencv/35778751) I figured out a workaround. The problem was that the build script didn't know where to find the `pytime.h` header - the solution was to use the `C_INCLUDE_PATH` environment variable to feed it the parent directory of that file.

I found the missing `pytime.h` header file using Spotlight (`mdfind`) like this:
```
% mdfind pytime.h
/usr/local/Cellar/python@3.7/3.7.12/Frameworks/Python.framework/Versions/3.7/include/python3.7m/pytime.h
/usr/local/Cellar/python@3.10/3.10.0_1/Frameworks/Python.framework/Versions/3.10/include/python3.10/cpython/pytime.h
/usr/local/Cellar/python@3.9/3.9.7/Frameworks/Python.framework/Versions/3.9/include/python3.9/pytime.h
/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.8/Headers/pytime.h
/usr/local/Cellar/python@3.8/3.8.12/Frameworks/Python.framework/Versions/3.8/include/python3.8/pytime.h
/Users/simon/Dropbox/Development/datasette-app/python/include/python3.9/pytime.h
/Users/simon/Dropbox/Development/datasette-app/python/lib/python3.9/config-3.9-darwin/Makefile
/Users/simon/Dropbox/Development/datasette-app/python/include/python3.9/Python.h
/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.8/Headers/Python.h
```
Since `python --version` in this environment returned `Python 3.10.0` I decided to go with that second one.

`C_INCLUDE_PATH` accepts one or more directory paths (not file paths), separated by a `:`. I used the following one-liner to successfully install the package:

`C_INCLUDE_PATH=/usr/local/Cellar/python@3.10/3.10.0_1/Frameworks/Python.framework/Versions/3.10/include/python3.10/cpython pip install datasette-bplist`
