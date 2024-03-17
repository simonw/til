# Programmatically comparing Python version strings

I found myself wanting to compare the version numbers `0.63.1`, `1.0` and the `1.0a13` in Python code, in order to mark a `pytest` test as skipped if the installed version of Datasette was pre-1.0.

This is very slightly tricky, because `1.0` is a higher version than `1.0a13` but comparing it based on string comparison or a `tuple` of components split by `.` would give the wrong result.

It turns out the [packaging.version](https://packaging.pypa.io/en/stable/version.html) Python package solves this exact problem:

```bash
python -m pip install packaging
```
Then:
```python
from packaging.version import parse

v_1_0 = parse("1.0")
v_1_0a13 = parse("1.0a13")
v_0631 = parse("0.63.1")
```
And some comparisons:
```pycon
>>> v_1_0 > v_1_0a13
True
>>> v_1_0 < v_1_0a13
False
>>> v_0631 < v_1_0
True
>>> v_0631 < v_1_0a13
True
```

## Using this with pytest

Here's how I used this to decorate a `pytest` test so it would only run on versions of Datasette more recent than `1.0a13`:
```python
from datasette import version
from packaging.version import parse
import pytest


@pytest.mark.asyncio
@pytest.mark.skipif(
    parse(version.__version__) < parse("1.0a13"),
    reason="uses row_actions() plugin hook",
)
async def test_row_actions():
    # ...
```
Full [example test here](https://github.com/datasette/datasette-enrichments/blob/c0deca1481d1c1e4b4d6a5802d4252adc3d84fb8/tests/test_enrichments.py#L153-L180).
