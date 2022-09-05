# Run pytest against a specific Python version using Docker

For [datasette issue #1802](https://github.com/simonw/datasette/issues/1802) I needed to run my `pytest` test suite using a specific version of Python 3.7.

I decided to do this using Docker, using the official [python:3.7-buster](https://hub.docker.com/_/python/tags?page=1&name=3.7-buster) image.

Here's the recipe that worked for me:
```bash
docker run -it -v `pwd`:/code \
  python:3.7-buster \
  bash -c "cd /code && pip install -e '.[test]' && pytest"
```

This command runs interactively so I can see the output (the `-it` option).

It mounts the current directory (with my testable application in it - I ran this in the root of a `datasette` checkout) as the `/code` volume inside the container.

It then runs the following using `bash -c`:

    cd /code && pip install -e '.[test]' && pytest

This installs my project's dependencies and test dependencies and then runs `pytest`.

The truncated output looks like this:
```
% docker run -it -v `pwd`:/code \
  python:3.7-buster \
  bash -c "cd /code && pip install -e '.[test]' && pytest"
Obtaining file:///code
  Preparing metadata (setup.py) ... done
Collecting asgiref>=3.2.10
  Downloading asgiref-3.5.2-py3-none-any.whl (22 kB)
...
Installing collected packages: rfc3986, mypy-extensions, iniconfig, zipp, typing-extensions, typed-ast, tomli, soupsieve, sniffio, six, PyYAML, pyparsing, pycparser, py, platformdirs, pathspec, mergedeep, MarkupSafe, itsdangerous, idna, hupper, h11, execnet, cogapp, certifi, attrs, aiofiles, python-multipart, packaging, Jinja2, janus, importlib-metadata, cffi, beautifulsoup4, asgiref, anyio, pluggy, pint, httpcore, cryptography, click, asgi-csrf, uvicorn, trustme, pytest, httpx, click-default-group-wheel, black, pytest-timeout, pytest-forked, pytest-asyncio, datasette, blacken-docs, pytest-xdist
  Running setup.py develop for datasette
...
========================================================= test session starts ==========================================================
platform linux -- Python 3.7.13, pytest-7.1.3, pluggy-1.0.0
SQLite: 3.27.2
rootdir: /code, configfile: pytest.ini
plugins: asyncio-0.19.0, anyio-3.6.1, timeout-2.1.0, xdist-2.5.0, forked-1.4.0
asyncio: mode=strict
collected 1054 items                                                                                                                   

tests/test_package.py ..                                                                                                         [  0%]
tests/test_cli.py .                                                                                                              [  0%]
tests/test_cli_serve_get.py ..                                                                                                   [  0%]
tests/test_cli.py .                                                                                                              [  0%]
tests/test_black.py .                                                                                                            [  0%]
tests/test_api.py ..................................................                                                             [  5%]
```
