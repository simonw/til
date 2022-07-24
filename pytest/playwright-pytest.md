# Using pytest and Playwright to test a JavaScript web application

I [decided to add](https://github.com/simonw/datasette-lite/issues/35) automated tests to my [Datasette Lite](https://simonwillison.net/2022/May/4/datasette-lite/) project. Datasette Lite bundles my Datasette Python web application us a client-side application running inside WebAssembly using Pyodide.

I wrote the tests using [playwright-pytest](https://github.com/microsoft/playwright-pytest), which lets you write tests in Python using Microsoft's [Playwright](https://playwright.dev/) browser automation library.

## Installing playwright-pytest

Two steps:

    pip install playwright-pytest

Then a second step to install the browsers using by Playwright itself:

    playwright install

I had those browsers installed already, but I still needed to run that command since the updated version of `playwright-pytest` needed more recent versions of those libraries.

(I had limited internet while doing this, and discovered that you can trick Playwright into using an older browser version by renaming a folder in `~/Library/Caches/ms-playwright` to the one that shows up in the error message that says that the browsers cannot be found.)

## An initial test

The first test I wrote looked like this, saved in `test_app.py`:

```python
from playwright.sync_api import Page, expect

def test_initial_load(page: Page):
    page.goto("https://lite.datasette.io/")
    loading = page.locator("#loading-indicator")
    expect(loading).to_have_css("display", "block")
    # Give it up to 60s to finish loading
    expect(loading).to_have_css("display", "none", timeout=60 * 1000)

    # Should load faster the second time thanks to cache
    page.goto("https://lite.datasette.io/")
    expect(loading).to_have_css("display", "none", timeout=20 * 1000)
```

Then run the test by running this in the same directory as that file:

    pytest

`playwright-pytest` provides the `page` fixture - annotating it with `: Page` is optional but if you do that then VS Code knows what it is and can provide autocomplete in the editor.

`page.goto()` causes the browser to navigate to that URL.

`page.locator("#loading-indicator")` returns a wrapper "locator" object for the specified CSS selector.

This line is interesting:

```python
expect(loading).to_have_css("display", "block")
```
The `expect()` helper function encapsulates the concept of polling the page to wait for something to become true within a time limit. This is the key technique for avoiding "flaky" tests when working with Playwright.


The assertions [are listed here](https://playwright.dev/python/docs/test-assertions).

You don't actually need to use `expect()` though - that's useful if you don't know how long it will take for the page to load, but if you know the page is already loaded you can write assertions like this instead:

```python
assert [
    el.inner_text()
    for el in page.query_selector_all("h2")
] == ["fixtures", "content"]
```

## pytest options

The `playwright-pytest` package adds a bunch of new options to `pytest`. The most useful is `--headed`:

    pytest --headed

This runs the tests in "headed" mode - which means a visible browser window pops up during the tests so you can see what is happening.

`--browser firefox` runs them using Firefox instead of Chromium.

`--tracing on` is really interesting: it generates a trace ZIP file which you can then open using https://trace.playwright.dev/ to explore a detailed trace of the test as it executed.

`--video on` records a video (as a `.webm` file) of the test. I've not tried it yet, but `--video retain-on-failure` only keeps that video if the test fails.

Here's [documentation on all of the options](https://playwright.dev/python/docs/test-runners).

## Running a localhost static server during the tests

I wanted to run the tests against the most recent version of my code, which consists of an `index.html` file and a `webworker.js` file. Because these use web workers they need to be run from an actual localhost web server, so I needed to start one at the beginning of the tests and shut it down at the end.

I wrote about my solution for this in another TIL: [Start a server in a subprocess during a pytest session](https://til.simonwillison.net/pytest/subprocess-server).

## My test suite so far

Here's where [I've got to so far](https://github.com/simonw/datasette-lite/blob/daba69708c7a72adad20dce3c534b9a399ef11c8/tests/test_datasette_lite.py):

```python
from playwright.sync_api import Browser, Page, expect
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


@pytest.fixture(scope="module")
def dslite(static_server, browser: Browser) -> Page:
    page = browser.new_page()
    page.goto("http://localhost:8123/")
    loading = page.locator("#loading-indicator")
    expect(loading).to_have_css("display", "block")
    # Give it up to 60s to finish loading
    expect(loading).to_have_css("display", "none", timeout=60 * 1000)
    return page


def test_initial_load(dslite: Page):
    expect(dslite.locator("#loading-indicator")).to_have_css("display", "none")


def test_has_two_databases(dslite: Page):
    assert [el.inner_text() for el in dslite.query_selector_all("h2")] == [
        "fixtures",
        "content",
    ]


def test_navigate_to_database(dslite: Page):
    h2 = dslite.query_selector("h2")
    assert h2.inner_text() == "fixtures"
    h2.query_selector("a").click()
    expect(dslite).to_have_title("fixtures")
    dslite.query_selector("textarea#sql-editor").fill(
        "SELECT * FROM no_primary_key limit 1"
    )
    dslite.query_selector("input[type=submit]").click()
    expect(dslite).to_have_title("fixtures: SELECT * FROM no_primary_key limit 1")
    table = dslite.query_selector("table.rows-and-columns")
    table_html = "".join(table.inner_html().split())
    assert table_html == (
        '<thead><tr><thclass="col-content"scope="col">content</th>'
        '<thclass="col-a"scope="col">a</th><thclass="col-b"scope="col">b</th>'
        '<thclass="col-c"scope="col">c</th></tr></thead><tbody><tr>'
        '<tdclass="col-content">1</td><tdclass="col-a">a1</td>'
        '<tdclass="col-b">b1</td><tdclass="col-c">c1</td></tr></tbody>'
    )
```

## Running it in GitHub Actions

Here's the [GitHub Actions workflow](https://github.com/simonw/datasette-lite/blob/main/.github/workflows/test.yml) I'm using to run the tests:

```yaml
name: Test

on:
  push:
  pull_request:

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python 3.10
      uses: actions/setup-python@v3
      with:
        python-version: "3.10"
        cache: 'pip'
        cache-dependency-path: '**/dev-requirements.txt'
    - name: Cache Playwright browsers
      uses: actions/cache@v3
      with:
        path: ~/.cache/ms-playwright/
        key: ${{ runner.os }}-browsers
    - name: Install dependencies
      run: |
        pip install -r dev-requirements.txt
        playwright install
    - name: Run test
      run: |
        pytest
```
[dev-requirements.txt](https://raw.githubusercontent.com/simonw/datasette-lite/main/dev-requirements.txt) contains this:
```
pytest-playwright==0.3.0
playwright==1.24.0
```
