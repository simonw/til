# Treating warnings as errors in pytest

I was seeing this warning in a Django project when I thought I was correctly using timezone-aware dates everywhere:

> RuntimeWarning: DateTimeField Shift.shift_start received a naive datetime (2022-04-01 00:00:00) while time zone support is active

Running `pytest -Werror` turns those warnings into errors that fail the tests.

Which means you can investigate them in the Python debugger by running:

    pytest -Werror --pdb -x

The `--pdb` starts the debugger at the warning (now error) and the `-x` stops the tests after the first failure.
