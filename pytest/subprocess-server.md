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
