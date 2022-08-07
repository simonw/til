# Mocking a Textract LimitExceededException with boto

For [s3-ocr issue #21](https://github.com/simonw/s3-ocr/issues/21) I needed to write a test that simulates what happens when Amazon Textract returns a "LimitExceededException". When using boto this error presents itself as an exception:

> `botocore.errorfactory.LimitExceededException: An error occurred (LimitExceededException) when calling the StartDocumentTextDetection operation: Open jobs exceed maximum concurrent job limit`

I uses [moto](https://github.com/spulec/moto) to simulate AWS in that test suite, but moto does not yet have a mechanism for simulating Textract errors like this one.

I ended up turning to Python mocks, here provided by the the [pytest-mock](https://pypi.org/project/pytest-mock/) fixture. Here's the test I came up with:

```python
def test_limit_exceeded_automatic_retry(s3, mocker):
    mocked = mocker.patch("s3_ocr.cli.start_document_text_extraction")
    # It's going to fail the first time, then succeed
    mocked.side_effect = [
        boto3.client("textract").exceptions.LimitExceededException(
            error_response={},
            operation_name="StartDocumentTextExtraction",
        ),
        {"JobId": "123"},
    ]
    runner = CliRunner()
    result = runner.invoke(cli, ["start", "my-bucket", "--all"])
    assert result.exit_code == 0
    assert result.output == (
        "Found 0 files with .s3-ocr.json out of 1 PDFs\n"
        "An error occurred (Unknown) when calling the StartDocumentTextExtraction operation: Unknown - retrying...\n"
        "Starting OCR for blah.pdf, Job ID: 123\n"
    )
```
Here I'm patching the function identified by the string `"s3_ocr.cli.start_document_text_extraction"`. This is a new function that I wrote specifically to make this mock easier to apply - it lives in `s3_ocr/cli.py` and looks [like this](https://github.com/simonw/s3-ocr/blob/23497aa5741c28c7eee00614a19c398066d61bf7/s3_ocr/cli.py#L552-L554):

```python
def start_document_text_extraction(textract, **kwargs):
    # Wrapper function to make this easier to mock in tests
    return textract.start_document_text_detection(**kwargs)
```
The most confusing thing about working with Python mocks is figuring out the string to use to mock the right piece of code. I like this pattern of refactoring the code under test to make it as simple to mock as possible.

The code I am testing here implements automatic retries. As such, I needed the API method I am simulating to fail the first time and then succeed the second time.

Originally I had done this with a `side_effect()` function - see below - but then [@szotten on Twitter](https://twitter.com/szotten/status/1556337221258575873) pointed out that you can instead set `mock.side_effect` to a list and it will [cycle through those items in turn](https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock.side_effect):

```python
mocked.side_effect = [
    boto3.client("textract").exceptions.LimitExceededException(
        error_response={},
        operation_name="StartDocumentTextExtraction",
    ),
    {"JobId": "123"},
]
```
Any exception objects in that list will be raised by the mocked function; any other kind of object will be returned.

The hardest thing to figure out was how to simulate the exception. The original error message indicated `botocore.errorfactory.LimitExceededException` but that's not actually a class you can import and raise.

Instead, I used `boto3.client("textract").exceptions.LimitExceededException`.

Figuring out that it needed an `error_response` and `operation_name` was tricky too. I eventually [tracked down](https://github.com/boto/botocore/blob/f4ed130b78076fb5683e4384c7df007e82dda71d/botocore/exceptions.py#L500-L517) the `botocore` `ClientError` constructor, which showed me what I needed to provide:

```python
class ClientError(Exception):
    MSG_TEMPLATE = (
        'An error occurred ({error_code}) when calling the {operation_name} '
        'operation{retry_info}: {error_message}'
    )

    def __init__(self, error_response, operation_name):
        retry_info = self._get_retry_info(error_response)
        error = error_response.get('Error', {})
        msg = self.MSG_TEMPLATE.format(
            error_code=error.get('Code', 'Unknown'),
            error_message=error.get('Message', 'Unknown'),
            operation_name=operation_name,
            retry_info=retry_info,
        )
        super().__init__(msg)
        self.response = error_response
        self.operation_name = operation_name
```

## Using a side effect function

Prior to the tip about setting `.side_effect` to a list I used a side effect function instead, with a `nonlocal` variable to change its behaviour the second time it was called:

```

The way to do that is with a `side_effect()` function which changes its behaviour the second time it is called. I used a `nonlocal` variable to keep track of whether the function should fail or not:

```python
should_fail = True

def side_effect(*args, **kwargs):
    nonlocal should_fail
    if should_fail:
        should_fail = False
        raise boto3.client("textract").exceptions.LimitExceededException(
            error_response={},
            operation_name="StartDocumentTextExtraction",
        )
    else:
        return {"JobId": "123"}
```
