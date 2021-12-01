# Ignoring a line in both flake8 and mypy

I [needed to tell](https://github.com/simonw/sqlite-utils/pull/347#issuecomment-982133970) both `flake8` and `mypy` to ignore the same line of code.

This worked:

```python
from sqlite3.dump import _iterdump as iterdump # type: ignore # noqa: F401
```

The order here mattered. This did not get picked up by both tools:

    # noqa: F401 # type: ignore

But this did:

    # type: ignore # noqa: F401
