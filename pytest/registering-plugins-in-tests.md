# Registering temporary pluggy plugins inside tests

While implementing more finely-grained permissions for `datasette-insert-api` ([issue 8](https://github.com/simonw/datasette-insert-api/issues/8)) I decided I wanted to register a Datasette pluggy plugin for the duration of a single test.

Here's the pattern I figured out for doing that:

```python
from datasette import hookimpl
from datasette.plugins import pm
import pytest


@pytest.mark.asyncio
async def test_using_test_plugin():
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
