# Registering temporary pluggy plugins inside tests

While implementing more finely-grained permissions for `datasette-insert-api` ([issue 8](https://github.com/simonw/datasette-insert-api/issues/8)) I decided I wanted to register a Datasette pluggy plugin for the duration of a single test.

Here's the pattern I figured out for doing that:

```python
from datasette import hookimpl
from datasette.plugins import pm
import pytest


def test_using_test_plugin():
    class TestPlugin:
        __name__ = "TestPlugin"

        @hookimpl
        def permission_allowed(self, datasette, actor, action):
            if action.startswith("insert-api:"):
                return permissions.get(action.replace("insert-api:", ""))

    pm.register(TestPlugin(), name="undo")
    try:
        # Rest of test goes here
    finally:
        pm.unregister(name="undo")
```

Here's [an example](https://github.com/simonw/datasette-insert/blob/7f4c2b3954190d547619d043bbe714481b10ac1e/tests/test_insert_api.py) of a test that uses a pytest fixture to register (and de-register) a plugin:

```python
from datasette import hookimpl
from datasette.app import Datasette
from datasette.plugins import pm
import pytest


@pytest.fixture
def unsafe():
    class UnsafeInsertAll:
        __name__ = "UnsafeInsertAll"

        @hookimpl
        def permission_allowed(self, action):
            if action == "insert:all":
                return True

    pm.register(UnsafeInsertAll(), name="undo")
    yield
    pm.unregister(name="undo")


@pytest.mark.asyncio
async def test_insert_alter(ds, unsafe):
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.post(
            "http://localhost/-/insert/data/dogs?pk=id",
            json=[{"id": 3, "name": "Cleopaws", "age": 5}],
        )
        assert 200 == response.status_code
```
