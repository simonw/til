# Using VCR and pytest with pytest-recording

[pytest-recording](https://github.com/kiwicom/pytest-recording) is a neat pytest plugin that makes it easy to use the [VCR library](https://vcrpy.readthedocs.io/), which helps write tests against HTTP resources by automatically capturing responses and baking them into a YAML file to be replayed during the tests.

It even works with [boto3](https://aws.amazon.com/sdk-for-python/)!

To use it, first install it with `pip install pytest-recording` and then add the `@pytest.mark.vcr` decorator to a test that makes HTTP calls:

```python
@pytest.mark.vcr
def test_create():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["create", "pytest-bucket-simonw-1", "-c"])
        assert result.exit_code == 0
```

The first time you run the tests, use the `--record-mode=once` option:
```bash
python -m pytest -k test_create --record-mode=once
```
This defaults to creating a YAML file in `tests/cassettes/test_s3_credentials/test_create.yaml`.

Subsequent runs of `pytest -k test_create` will reuse those recorded HTTP requests and will not make any network requests - I confirmed this by turning off my laptop's WiFi.

## Filtering out HTTP headers and hiding API keys

For my tests that use API key services like the OpenAI API I've settled on this pattern:

```python
import os
import pytest

API_KEY = os.environ.get("PYTEST_OPENAI_API_KEY") or "fake-key"


@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": ["authorization"]}
```

The `vcr_config()` there ensures that any `authorization` HTTP headers in the resulting cassette YAML files are redacted, so they don't accidentally get checked in to a public GitHub repo.

I use that `PYTEST_OPENAI_API_KEY` environment variable in tests like this:

```
@pytest.mark.vcr
def test_ask(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", API_KEY)
    # ...
```
Then for the duration of that test the `OPENAI_API_KEY` environment key will either be `fake-key` for test runs against previously recorded cassette or the value of `PYTEST_OPENAI_API_KEY` - which means I can update the cassettes like this:

```bash
PYTEST_OPENAI_API_KEY=your-key python -m pytest --record-mode once
```
