# Opt-in integration tests with pytest --integration

For both [s3-credentials](https://github.com/simonw/s3-credentials) and [datasette-publish-fly](https://github.com/simonw/datasette-publish-fly) I have a need for real-world integration tests that actually interact with the underlying APIs (AWS or Fly) to create and destroy resources on those platforms.

Most of the time I want my tests to run without doing these. I want the option to run `pytest --integration` to opt-in to running those extra integration tests.

Here's the pattern I'm using. First, in `tests/conftest.py`:

```python
import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--integration",
        action="store_true",
        default=False,
        help="run integration tests",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test, only run with --integration",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--integration"):
        # Also run integration tests
        return
    skip_integration = pytest.mark.skip(reason="use --integration option to run")
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_integration)
```
This implements a `@pytest.mark.integration` marker which I can use to mark any test that should be considered part of the integration test suite. These will be skipped by default... but will not be skipped if the `--integration` option is passed to `pytest`.

Then in the tests I can either do this:

```python
@pytest.mark.integration
def test_integration_s3():
    # ...
```
Or if I have a module that only contains integration tests - `tests/test_integration.py` - I can use the following line to apply that decorator to every test in the module:
```python
import pytest

pytestmark = pytest.mark.integration

def test_integration_s3():
    # ...
```
