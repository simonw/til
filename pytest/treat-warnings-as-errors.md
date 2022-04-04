# Treating warnings as errors in pytest

I was seeing this warning in a Django project when I thought I was correctly using timezone-aware dates everywhere:

> RuntimeWarning: DateTimeField Shift.shift_start received a naive datetime (2022-04-01 00:00:00) while time zone support is active

Running `pytest -Werror` turns those warnings into errors that fail the tests.

Which means you can investigate them in the Python debugger by running:

    pytest -Werror --pdb -x

The `--pdb` starts the debugger at the warning (now error) and the `-x` stops the tests after the first failure.

## In pytest.ini

You can also set this in `pytest.ini` - useful if you want ALL warnings to be failures in both development and CI.

Add the following to the `pytest.ini` file:

```ini
[pytest]
# ...
filterwarnings =
    error
```

## Ignoring specific warnings

If you do this you may find there are warnings you cannot fix (because they are in dependency libraries). You can ignore those like this:

```ini
[pytest]
# ...
filterwarnings =
    error
    ignore::arrow.factory.ArrowParseWarning
```

You need to figure out the full path to the warning. I used `--pdb` to figure this out.
