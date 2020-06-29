# Writing tests for the ASGI lifespan protocol with HTTPX

Uvicorn silently ignores exceptions that occur during startup against the ASGI lifespan protocol - see [starlette/issues/486](https://github.com/encode/starlette/issues/486).

You can disable this feature using the `lifespan="on"` parameter to `uvicorn.run()` - which Datasette now does as-of [16f592247a2a0e140ada487e9972645406dcae69](https://github.com/simonw/datasette/commit/16f592247a2a0e140ada487e9972645406dcae69)

This exposed a bug in `datasette-debug-asgi`: it wasn't handling lifespan events correctly. [datasette-debug-asgi/issues/1](https://github.com/simonw/datasette-debug-asgi/issues/1)

The unit tests weren't catching this because using HTTPX to make test requests [doesn't trigger lifespan events](https://github.com/encode/httpx/issues/350).

Florimond Manca had run into this problem too, and built [asgi-lifespan](https://github.com/florimondmanca/asgi-lifespan) to address it.

You can wrap an ASGI app in `async with LifespanManager(app):` and the correct lifespan events will be fired by that with block.

Here's how to use it to [trigger lifespan events in a test](https://github.com/simonw/datasette-debug-asgi/blob/72d568d32a3159c763ce908c0b269736935c6987/test_datasette_debug_asgi.py):

```python
@pytest.mark.asyncio
async def test_datasette_debug_asgi():
    ds = Datasette([], memory=True)
    app = ds.app()
    async with LifespanManager(app):
        async with httpx.AsyncClient(app=app) as client:
            response = await client.get("http://localhost/-/asgi-scope")
            assert 200 == response.status_code
            assert "text/plain; charset=UTF-8" == response.headers["content-type"]
```
