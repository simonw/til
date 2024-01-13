# Writing Playwright tests for a Datasette Plugin

I really like [Playwright](https://playwright.dev/) for writing automated tests for web applications using a headless browser. It's pretty easy to install and run, and it works well in GitHub Actions.

Today I integrated Playwright into the tests for one of my Datasette plugins for the first time. I based my work off Alex Garcia's [tests for datasette-comments](https://github.com/datasette/datasette-comments/tree/0.1.0/tests).

I added Playwright to my [datasette-search-all](https://github.com/simonw/datasette-search-all) plugin as part of [issue #19](https://github.com/simonw/datasette-search-all/issues/19). Here's what I did.

## Playwright as a test dependency

I ended up needing two new test dependencies to get Playwright running: `pytest-playwright` and `nest-asyncio` (for reasons explained later).

I added those to my `setup.py` file like this:
```python
    extras_require={
        "test": ["pytest", "pytest-asyncio", "sqlite-utils", "nest-asyncio"],
        "playwright": ["pytest-playwright"]
    },
```
I decided to make `playwright` part of its own group, so that I could avoid running Playwright tests by default due to the size of the extra browser dependency.

If I was using `pyproject.toml` for this project I would add this instead:
```toml
[project.optional-dependencies]
test = ["pytest", "pytest-asyncio", "sqlite-utils", "nest-asyncio"]
playwright = ["pytest-playwright"]
```
With either of these patterns in place, the new dependencies can be installed like this:
```bash
pip install -e '.[test,playwright]'
```

## Running a localhost server for the tests

I decided to use a [pytest fixture](https://docs.pytest.org/en/6.2.x/fixture.html) to start a `localhost` server running for the duration of the test. The simplest version of that (`wait_until_responds` from Alex's `datasette-comments`) looks like this:
```python
import pytest
import sqlite3
from subprocess import Popen, PIPE
import sys
import time
import httpx

@pytest.fixture(scope="session")
def ds_server(tmp_path_factory):
    tmpdir = tmp_path_factory.mktemp("tmp")
    db_path = str(tmpdir / "data.db")
    db = sqlite3.connect(db_path)
    db.execute("""
        create table foo (
            id integer primary key,
            bar text
        )
    """)
    process = Popen(
        [
            sys.executable,
            "-m",
            "datasette",
            "--port",
            "8126",
            str(db_path),
        ],
        stdout=PIPE,
    )
    wait_until_responds(
        "http://localhost:8126/"
    )
    yield "http://localhost:8126"
    process.terminate()
    process.wait()


def wait_until_responds(url, timeout=5.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            httpx.get(url)
            return
        except httpx.ConnectError:
            time.sleep(0.1)
    raise AssertionError("Timed out waiting for {} to respond".format(url))
```
The `ds_server` fixture creates a SQLite database in a temporary directory, runs Datasette against it using `subprocess.Popen()` and then waits for the server to respond to a request. Then it yields the URL to that server - that yielded value will become available to any test that uses that fixture.

Note that `ds_server` is marked as `@pytest.fixture(scope="session")`. This means that the fixture will be excuted just once per test session and re-used by each test. Without the `scope="session"` the server will be started and then terminated once per test, which is a lot slower.

See [Session-scoped temporary directories in pytest](https://til.simonwillison.net/pytest/session-scoped-tmp) for an explanation of the `tmp_path_factory` fixture.

Here's what a basic test then looks like (in `tests/test_playwright.py`):
```python
try:
    from playwright import sync_api
except ImportError:
    sync_api = None
import pytest

@pytest.mark.skipif(sync_api is None, reason="playwright not installed")
def test_homepage(ds_server):
    with sync_api.sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(ds_server + "/")
        assert page.title() == "Datasette: data"
```

Within that test, the full [Python Playwright API](https://playwright.dev/python/docs/writing-tests) is available for interacting with the server and running assertions. Since it's running in a real headless Chromium instance all of the JavaScript will be executed as well.

I'm using a `except ImportError` pattern here such that my tests won't fail if Playwright has not been installed. The `@pytest.mark.skipif` decorator causes the test to be marked as skipped if the module was not imported.

## Running the tests

With this module in place, running the tests is like any other `pytest` invocation:
```bash
pytest
```
Or run them specifically like this:
```bash
pytest tests/test_playwright.py
# or
pytest -k test_homepage
```

## Refactoring for cleaner code

After some experimentation I ended up with this pattern instead:

```python
try:
    from playwright import sync_api
except ImportError:
    sync_api = None
import pytest
import nest_asyncio

nest_asyncio.apply()

pytestmark = pytest.mark.skipif(sync_api is None, reason="playwright not installed")


def test_ds_server(ds_server, page):
    page.goto(ds_server + "/")
    assert page.title() == "Datasette: data"
    # It should have a search form
    assert page.query_selector('form[action="/-/search"]')

def test_search(ds_server, page):
    page.goto(ds_server + "/-/search?q=cleo")
    # Should show search results, after fetching them
    assert page.locator("table tr th:nth-child(1)").inner_text() == "rowid"
    # ... assertions continue
```

There are two new tricks in here:

1. I'm using the `pytestmark = pytest.mark.skipif()` pattern to apply that `skipif` decorator to every test in this file, without needing to repeat it.
2. I'm using the `page` fixture [provided by pytest-playwright](https://playwright.dev/python/docs/test-runners#fixtures). This gives me a new `page` object for each test, without me needing to call the `with sync_api.sync_playwright() as playwright` boilerplate every time.

One catch with the `page` fixture is when I first started using it I got this error:
```
This event loop is already running
```
After some digging around I found a solution in [this issue](https://github.com/microsoft/playwright-python/issues/178), which was to apply `nest_asyncio.apply()` at the start of the module.

## Running this in GitHub Actions

I updated my `.github/workflows/test.yml` workflow to look like this:

```yaml
name: Test

on: [push, pull_request]

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11", "3.12"]
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
        cache: pip
        cache-dependency-path: setup.py
    - name: Cache Playwright browsers
      uses: actions/cache@v3
      with:
        path: ~/.cache/ms-playwright/
        key: ${{ runner.os }}-browsers
    - name: Install dependencies
      run: |
        pip install '.[test,playwright]'
        playwright install
    - name: Run tests
      run: |
        pytest
```
This workflow configures caching for Playwright browsers, to ensure that `playwright install` only downloads the browser binaries the first time the workflow is executed.
