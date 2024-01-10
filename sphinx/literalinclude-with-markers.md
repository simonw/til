# literalinclude with markers for showing code in documentation

I [wanted to include](https://github.com/simonw/datasette/issues/1830) some example Python tests in the Datasette documentation - but since they were tests, I also wanted to execute them as part of my test suite to make sure they worked correctly.

I solved this with the Sphinx [literalinclude directive](https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-literalinclude).

Here's what I put in my [docs/testing_plugins.rst#L92-L111](https://github.com/simonw/datasette/blob/0f63cb83ed31753a9bd9ec5cc71de16906767337/docs/testing_plugins.rst#L92-L111) file:
```rst
A simple test looks like this:

.. literalinclude:: ../tests/test_docs.py
   :language: python
   :start-after: # -- start test_homepage --
   :end-before: # -- end test_homepage --

Or for a JSON API:

.. literalinclude:: ../tests/test_docs.py
   :language: python
   :start-after: # -- start test_actor_is_null --
   :end-before: # -- end test_actor_is_null --

To make requests as an authenticated actor, create a signed ``ds_cookie`` using the ``datasette.client.actor_cookie()`` helper function and pass it in ``cookies=`` like this:

.. literalinclude:: ../tests/test_docs.py
   :language: python
   :start-after: # -- start test_signed_cookie_actor --
   :end-before: # -- end test_signed_cookie_actor --
```
Note that the paths like `../tests/test_docs.py` are relative to the root `docs/` folder, which is a sibling of `tests/`.

Then in [tests/test_docs.py](https://github.com/simonw/datasette/blob/0f63cb83ed31753a9bd9ec5cc71de16906767337/tests/test_docs.py#L109-L141):
```python
# fmt: off

# -- start test_homepage --
@pytest.mark.asyncio
async def test_homepage():
    ds = Datasette(memory=True)
    response = await ds.client.get("/")
    html = response.text
    assert "<h1>" in html
# -- end test_homepage --

# -- start test_actor_is_null --
@pytest.mark.asyncio
async def test_actor_is_null():
    ds = Datasette(memory=True)
    response = await ds.client.get("/-/actor.json")
    assert response.json() == {"actor": None}
# -- end test_actor_is_null --

# -- start test_signed_cookie_actor --
@pytest.mark.asyncio
async def test_signed_cookie_actor():
    ds = Datasette(memory=True)
    cookies = {"ds_actor": ds.client.actor_cookie({"id": "root"})}
    response = await ds.client.get("/-/actor.json", cookies=cookies)
    assert response.json() == {"actor": {"id": "root"}}
# -- end test_signed_cookie_actor --
```
The rendered documentation [can be seen here](https://docs.datasette.io/en/latest/testing_plugins.html#using-datasette-client-in-tests).

The `# fmt: off` line at the start is an instruction to [Black](https://github.com/psf/black) to ignore that section of the file. Without that, running Black would insist on adding newlines before the closing `# -- end` comments, which would show up [as blank space in the documentation](https://github.com/simonw/datasette/issues/2231).
