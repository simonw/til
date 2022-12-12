# Show files opened by pytest tests

My test suite for [Datasette](https://github.com/simonw/datasette) has grown so large that running the whole thing sometimes causes me to run out of file handles.

I've not solved this yet, but I did figure out a pattern to get `pytest` to show me which new files were opened by which tests.

Add the following to `conftest.py`:

```
import psutil


@pytest.fixture(autouse=True)
def check_for_new_file_handles(request):
    proc = psutil.Process()
    before_files = set(proc.open_files())
    yield
    after_files = proc.open_files()
    new_files = [f for f in after_files if f not in before_files]
    if new_files:
        print("{} opened by {}".format(new_files, request.node))
```

This uses [psutil](https://pypi.org/project/psutil/) (`pip install psutil`) to build a set of the open files before and after the test runs. It then uses a list comprehension to figure out which file handles are new.

Using `@pytest.fixture(autouse=True)` means it will automatically be used for every test.

It's a `yield` fixture, which means the part of the code before the `yield` statement runs before the test, then the part afterwards runs after the test function has finished.

Accepting the `request` argument means it gets access to a `pytest` request object, which includes `request.node` which is an object representing the test that is being executed.

You need to run `pytest -s` to see the output (without the `-s` the output is hidden).

Example output:
  
`tests/test_permissions.py .[popenfile(path='/private/var/folders/wr/hn3206rs1yzgq3r49bz8nvnh0000gn/T/tmp76w2ukin/fixtures.db', fd=8)] opened by <Function test_view_padlock[/-None-200-200]>..`
