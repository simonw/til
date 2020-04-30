# How to mock httpx using pytest-mock

I wrote this test to exercise some [httpx](https://pypi.org/project/httpx/) code today, using [pytest-mock]().

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
