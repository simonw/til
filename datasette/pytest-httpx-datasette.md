# Using pytest-httpx to run intercepted requests through an in-memory Datasette instance

I've been working on a tool called [dclient](https://github.com/simonw/dclient) which is a CLI client tool for talking to Datasette instances.

I wanted to write some tests for that tool which would simulate an entire Datasette instance for it to talk to, without starting a `localhost` server running Datasette itself.

I figured out a pattern for doing that using `pytest-httpx` to intercept outbound HTTP requests and send them through a Datasette ASGI application instead.

Here's a simplified example of this pattern, with inline comments explaining how it works.

Dependencies are:
```bash
pip install pytest pytest-httpx httpx datasette
```
I saved this as `test_demo.py` and ran it with `pytest test_demo.py`:
```python
import asyncio
from datasette.app import Datasette
import httpx
import pytest


@pytest.fixture
def non_mocked_hosts():
    # This ensures that httpx-mock will not affect things once a request
    # starts being processed within Datasette itself via datasette.client
    return ["localhost"]


# Here's an example function we will be testing. This uses httpx.get() to
# make an outbound HTTP request to a Datasette instance - we want to intercept
# that call and handle it ourselves using httpx_mock
def get_versions():
    response = httpx.get("https://datasette.example.com/-/versions.json")
    response.raise_for_status()
    return response.json()


# The httpx_mock fixtures comes from pytest-httpx
def test_get_version(httpx_mock):
    ds = Datasette()

    # This test is a regular function, but we need to be able to make some
    # await... calls later on - so we need the event loop to run them against
    loop = asyncio.get_event_loop()

    # This function will be called every time pytest-httpx intercepts an HTTP request
    def custom_response(request: httpx.Request):
        # Need to run this in async loop, because get_versions uses
        # sync HTTPX and not async HTTPX
        async def run():
            # Here we use ds.client.request() - an internal method within Datasette
            # which can be used to simulate passing an HTTP request through the ASGI app
            # This is why we needed to include localhost in non_mocked_hosts earlier
            response = await ds.client.request(
                request.method,
                request.url.path,
                content=request.read(),
                headers=request.headers,
            )
            # Create a fresh response to avoid an error where stream has been consumed
            response = httpx.Response(
                status_code=response.status_code,
                headers=response.headers,
                content=response.content,
            )
            return response

        return loop.run_until_complete(run())

    # We add custom_response as a callback function for any intercepted HTTP requests:
    httpx_mock.add_callback(custom_response)

    # And here's our actual test
    versions = get_versions()
    assert "asgi" in versions
    assert "datasette" in versions
    assert "python" in versions
```
You can see a much more complex example of this pattern in action in this file: https://github.com/simonw/dclient/blob/0.2/tests/test_insert.py
