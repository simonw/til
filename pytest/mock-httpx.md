# How to mock httpx using pytest-mock

I wrote this test to exercise some [httpx](https://pypi.org/project/httpx/) code today, using [pytest-mock](https://pypi.org/project/pytest-mock/).

The key was to use `mocker.patch.object(cli, "httpx")` which patches the `httpx` module that was imported by the `cli` module.

Here the `mocker` function argument is a fixture that is provided by `pytest-mock`.

```python
from conditional_get import cli
from click.testing import CliRunner


def test_performs_conditional_get(mocker):
    m = mocker.patch.object(cli, "httpx")
    m.get.return_value = mocker.Mock()
    m.get.return_value.status_code = 200
    m.get.return_value.content = b"Hello PNG"
    m.get.return_value.headers = {"etag": "hello-etag"}
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli.cli, ["https://example.com/file.png", "-o", "file.png"]
        )
        m.get.assert_called_once_with("https://example.com/file.png", headers={})
        assert b"Hello PNG" == open("file.png", "rb").read()
        # Should have also written the ETags file
        assert {"https://example.com/file.png": "hello-etag"} == json.load(
            open("etags.json")
        )
        # Second call should react differently
        m.get.reset_mock()
        m.get.return_value.status_code = 304
        result = runner.invoke(
            cli.cli, ["https://example.com/file.png", "-o", "file.png"]
        )
        m.get.assert_called_once_with(
            "https://example.com/file.png", headers={"If-None-Match": "hello-etag"}
        )
```
https://github.com/simonw/conditional-get/blob/485fab46f01edd99818b829e99765ed9ce0978b5/tests/test_cli.py

## Mocking httpx.stream

I later had to figure out how to mock the following:

```python
with httpx.stream("GET", url, headers=headers) as response:
    ...
    with open(output, "wb") as fp:
        for b in response.iter_bytes():
            fp.write(b)
```
https://stackoverflow.com/a/6112456 helped me figure out the following:
```python
def test_performs_conditional_get(mocker):
    m = mocker.patch.object(cli, "httpx")
    m.stream.return_value.__enter__.return_value = mocker.Mock()
    m.stream.return_value.__enter__.return_value.status_code = 200
    m.stream.return_value.__enter__.return_value.iter_bytes.return_value = [
        b"Hello PNG"
    ]
```
https://github.com/simonw/conditional-get/blob/80454f972d39e2b418572d7938146830fab98fa6/tests/test_cli.py

## Mocking an HTTP error triggered by response.raise_for_status()

The `response.raise_for_status()` raises an exception if an HTTP error (e.g. a 404 or 500) occurred.

Here's how I [mocked that to return an error](https://github.com/simonw/airtable-to-yaml/blob/ebd94b2e29d6f2ec3dc64d161495a759330027e8/tests/test_airtable_to_yaml.py#L43-L56):

```python
def test_airtable_to_yaml_error(mocker):
    m = mocker.patch.object(cli, "httpx")
    m.get.return_value = mocker.Mock()
    m.get.return_value.status_code = 401
    m.get.return_value.raise_for_status.side_effect = httpx.HTTPError(
        "Unauthorized", request=None
    )
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(
            cli.cli, [".", "appZOGvNJPXCQ205F", "tablename", "-v", "--key", "x"]
        )
        assert result.exit_code == 1
        assert result.stdout == "Error: Unauthorized\n"
```
