# Subtests in pytest 9.0.0+

[pytest 9.0.0](https://pypi.org/project/pytest/9.0.0/) was released on November 8th 2025. I just got around to looking at the [release notes](https://docs.pytest.org/en/stable/changelog.html#pytest-9-0-0-2025-11-05) and the biggest new feature is **subtests**, previously available as the separate [pytest-subtests](https://pypi.org/project/pytest-subtests/) plugin.

I copied the documentation into Claude Code and [told it to find a good place to try them](https://gistpreview.github.io/?0487e5bb12bcbed850790a6324788e1b) in the Datasette test suite. It suggested [tests/test_docs.py](https://github.com/simonw/datasette/blob/1.0a23/tests/test_docs.py), which currently make heavy use of the `@pytest.mark.parametrize` mechanism. I wrote about how that works a few years ago in [Documentation unit tests](https://simonwillison.net/2018/Jul/28/documentation-unit-tests/) - here's an example test:

```python
@pytest.mark.parametrize("setting", app.SETTINGS)
def test_settings_are_documented(settings_headings, setting):
    assert setting.name in settings_headings
```

## Understanding subtests

The idea behind subtests is to allow a test to programatically create new subtest within itself at runtime.

My above example does the same thing using `@pytest.mark.parametrize` - but it relies on the list of settings being known at test collection time. This might not be possible for things that need to be introspected after the test has run some initial setup code.

Here's the above test ported to use subtests instead:

```python
def test_settings_are_documented(settings_headings, subtests):
    for setting in app.SETTINGS:
        with subtests.test(setting=setting.name):
            assert setting.name in settings_headings
```

`subtests` is a new default pytest fixture - if you list that as a parameter to your test function you can use it in the body of the test.

Using `with subtests.test(...)` creates a new subtest. Here I'm doing that in a loop. The keyword arguments passed to `subtests.test()` are used to identify the subtest in the test report.

That's all it takes! Here's [a commit](https://github.com/simonw/datasette/commit/1d4448fc5603f479f11b37b9da0ee11c2b1a19e4) that ported several of my parameterized tests to use subtests instead.

## How subtests differ from parametrize

If you use `@pytest.mark.parametrize` pytest will behave as if every one of your parameter combinations is a separate test function. Running the old `pytest tests/test_docs.py` tests looked like this:
```
============================= test session starts ==============================
platform darwin -- Python 3.14.0, pytest-9.0.1, pluggy-1.6.0
SQLite: 3.50.4
rootdir: /private/tmp/datasette
configfile: pytest.ini
plugins: anyio-4.12.0, xdist-3.8.0, timeout-2.4.0, asyncio-1.3.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 120 items                                                            

tests/test_docs.py ..................................................... [ 44%]
...................................................................      [100%]

============================= 120 passed in 0.84s ==============================
```
Porting to subtests causes each test to be reported just once:
```
...
collected 9 items                                                             

tests/test_docs.py .........                                            [100%]

============================== 9 passed in 0.15s ==============================
```
But... if you add `-v` for verbose output you get back a report that *does* include every subtest. Truncated, that looks like this:

```
...
collected 9 items                                                                                                

tests/test_docs.py::test_settings_are_documented SUBPASSED(setting='default_page_size')                    [ 11%]
tests/test_docs.py::test_settings_are_documented SUBPASSED(setting='max_returned_rows')                    [ 11%]
...
tests/test_docs.py::test_settings_are_documented PASSED                                                    [ 11%]
tests/test_docs.py::test_plugin_hooks_are_documented SUBPASSED(plugin='actor_from_request')                [ 22%]
tests/test_docs.py::test_plugin_hooks_are_documented SUBPASSED(plugin='actors_from_ids')                   [ 22%]
tests/test_docs.py::test_plugin_hooks_are_documented PASSED                                                [ 22%]...

...
tests/test_docs.py::test_rst_heading_underlines_match_title_length PASSED                                  [ 66%]
tests/test_docs.py::test_homepage PASSED                                                                   [ 77%]
tests/test_docs.py::test_actor_is_null PASSED                                                              [ 88%]
tests/test_docs.py::test_signed_cookie_actor PASSED                                                        [100%]

============================== 9 passed, 116 subtests passed in 0.15s ==============================
```

The last line shows how many subtests passed in addition to how many tests.

It looks to me like subtests run substantially faster than the eqpuivalent parameterized tests. I'm more interested in the fact that subtests can now be programatically generated at runtime based on test setup code.
