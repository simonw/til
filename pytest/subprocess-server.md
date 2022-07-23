# Start a server in a subprocess during a pytest session

I wanted to start an actual server process, run it for the duration of my pytest session and shut it down at the end.

Here's the recipe I came up with. This fixture lives in `conftest.py`:

```python
import pytest
import sqlite_utils
import subprocess

@pytest.fixture(scope="session")
def ds_server(tmp_path_factory):
    db_directory = tmp_path_factory.mktemp("dbs")
    db_path = db_directory / "test.db"
    db = sqlite_utils.Database(db_path)
    insert_test_data(db)
    ds_proc = subprocess.Popen(
        [
            "datasette",
            str(db_path),
            "-p",
            "8041"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    # Give the server time to start
    time.sleep(2)
    # Check it started successfully
    assert not ds_proc.poll(), ds_proc.stdout.read().decode("utf-8")
    yield ds_proc
    # Shut it down at the end of the pytest session
    ds_proc.terminate()
```
A test looks like this:
```python
import httpx

def test_server_starts(ds_server):
    response = httpx.get("http://127.0.0.1:8041/")
    assert response.status_code == 200
```

## Alternative recipe for serving static files

While [adding tests to Datasette Lite](https://github.com/simonw/datasette-lite/issues/35) I found myself needing to run a localhost server that served static files directly.

I completely forgot about this TIL, and instead took inspiration [from pytest-simplehttpserver](https://github.com/ppmdo/pytest-simplehttpserver/blob/a82ad31912121c074ff1a76c4628a1c42c32b41b/src/pytest_simplehttpserver/pytest_plugin.py#L17-L28) - coming up with this pattern:

```python
from subprocess import Popen, PIPE
import pathlib
import pytest
import time
from http.client import HTTPConnection

root = pathlib.Path(__file__).parent.parent.absolute()


@pytest.fixture(scope="module")
def static_server():
    process = Popen(
        ["python", "-m", "http.server", "8123", "--directory", root], stdout=PIPE
    )
    retries = 5
    while retries > 0:
        conn = HTTPConnection("localhost:8123")
        try:
            conn.request("HEAD", "/")
            response = conn.getresponse()
            if response is not None:
                yield process
                break
        except ConnectionRefusedError:
            time.sleep(1)
            retries -= 1

    if not retries:
        raise RuntimeError("Failed to start http server")
    else:
        process.terminate()
        process.wait()
```
Again, including `static_server` as a fixture is enough to ensure requests to `http://localhost:8123/` will be served by that temporary server.

I like how this version polls for a successful HEAD request (a trick inspired by `pytest-simplehttpserver`) rather than just sleeping.
