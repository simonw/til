# Checking if something is callable or async callable in Python

I wanted a mechanism to check if a given Python object was "callable" - could be called like a function - or "async callable" - could be called using `await obj()`.

I ended up writing this helper function to help introspect objects and answer those questions:
```python
import asyncio
import types
from typing import NamedTuple, Any


class CallableStatus(NamedTuple):
    is_callable: bool
    is_async_callable: bool


def check_callable(obj: Any) -> CallableStatus:
    if not callable(obj):
        return CallableStatus(False, False)

    if isinstance(obj, type):
        # It's a class
        return CallableStatus(True, False)

    if isinstance(obj, types.FunctionType):
        return CallableStatus(True, asyncio.iscoroutinefunction(obj))

    if hasattr(obj, "__call__"):
        return CallableStatus(True, asyncio.iscoroutinefunction(obj.__call__))

    assert False, "obj {} is somehow callable with no __call__ method".format(repr(obj))
```
`check_callable(obj)` returns a `CallableStatus` named tuple, with an `is_callable` boolean saying if it can be caled and an `is_async_callable` boolean specifying if you need to use `await` with it.

I wrote these `pytest` tests to exercise the `check_callable()` function:

```python
import pytest


class AsyncClass:
    async def __call__(self):
        pass


class NotAsyncClass:
    def __call__(self):
        pass


class ClassNoCall:
    pass


async def async_func():
    pass


def non_async_func():
    pass


@pytest.mark.parametrize(
    "obj,expected_is_callable,expected_is_async_callable",
    (
        (async_func, True, True),
        (non_async_func, True, False),
        (AsyncClass(), True, True),
        (NotAsyncClass(), True, False),
        (ClassNoCall(), False, False),
        (AsyncClass, True, False),
        (NotAsyncClass, True, False),
        (ClassNoCall, True, False),
        ("", False, False),
        (1, False, False),
        (str, True, False),
    ),
)
def test_check_callable(obj, expected_is_callable, expected_is_async_callable):
    status = check_callable(obj)
    assert status.is_callable == expected_is_callable
    assert status.is_async_callable == expected_is_async_callable
```
See [this commit](https://github.com/simonw/datasette/commit/2e43a14da195b3a4d4d413b217cdca0239844e26) for my initial implementation.
