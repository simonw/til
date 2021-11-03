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

    pytest -k test_create --record-mode=once

This defaults to creating a YAML file in `tests/cassettes/test_s3_credentials/test_create.yaml`.

Subsequent runs of `pytest -k test_create` will reuse those recorded HTTP requests and will not make any network requests - I confirmed this by turning off my laptop's WiFi.
