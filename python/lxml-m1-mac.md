# Installing lxml for Python on an M1/M2 Mac

I ran into this error while trying to run `pip install lxml` on an M2 Mac, inside a virtual environment I had intitially created using `pipenv shell`:
```
% pip install lxml
Collecting lxml
  Using cached lxml-4.9.2.tar.gz (3.7 MB)
  Preparing metadata (setup.py) ... done
Building wheels for collected packages: lxml
  Building wheel for lxml (setup.py) ... error
  error: subprocess-exited-with-error
  
  × python setup.py bdist_wheel did not run successfully.
  │ exit code: 1
  ╰─> [121 lines of output]
...
      src/lxml/etree.c:96:10: fatal error: 'Python.h' file not found
      #include "Python.h"
               ^~~~~~~~~~
      1 error generated.
      Compile failed: command '/usr/bin/clang' failed with exit code 1
...
```
I eventually realized that this was using the system Python - `/usr/bin/python3` - which doesn't have access to the necessary headers needed to build `lxml`.

I had also installed Python using Homebrew, which DOES include those headers - but the environment I was working in was using a different Python version.

I'm using `pipenv` to manage my environments, so the fix for me was to do this:

```
pipenv --python /opt/homebrew/bin/python3.11
```
(`/opt/homebrew/bin/python3.10` would have worked too.)

Then within my new environment `pip install lxml` worked just fine.

If I wasn't using `pipenv` I would run this command to create a fresh virtual environment instead:

    /opt/homebrew/bin/python3.11 -m venv venv
    venv/bin/pip install lxml
