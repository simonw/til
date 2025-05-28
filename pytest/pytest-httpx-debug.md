# A tip for debugging pytest-httpx

I use [pytest-httpx](https://colin-b.github.io/pytest_httpx/) in a bunch of my projects. Occasionally I run into test failures like this one, which can sometimes be really hard to figure out:

```
E       AssertionError: The following responses are mocked but not requested:
E         - Match POST request on https://api.mistral.ai/v1/chat/completions
E         
E         If this is on purpose, refer to https://github.com/Colin-b/pytest_httpx/blob/master/README.md#allow-to-register-more-responses-than-what-will-be-requested
E       assert not [<pytest_httpx._request_matcher._RequestMatcher object at 0x107d4e560>]
```
Today I figured out a pattern for investigating these that works *really well*.

Drop a variant of this decorator onto your failing test:

```python
def intercept(request):
    from pprint import pprint
    import json

    print(request.url)
    pprint(json.loads(request.content))
    breakpoint()
    return True

@pytest.mark.httpx_mock(should_mock=intercept)
def test_tools_stream(mocked_tool_stream):
    model = llm.get_model("mistral/mistral-medium")
    ...
```
The `intercept()` function will then be called for _every_ request that `pytest-httpx` has the chance to intercept. In my function here I'm printing out the URL and pretty-printing the JSON body (I was debugging a Mistral API call) but you can leave those out entirely and just rely on the `breakpoint()`.

When you run `pytest` your tests will pause at every instance of that function call, and you can then inspect the `request` object and figure out what's going on.
