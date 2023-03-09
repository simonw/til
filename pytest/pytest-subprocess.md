# Mocking subprocess with pytest-subprocess

For [apple-notes-to-sqlite](https://github.com/dogsheep/apple-notes-to-sqlite) I needed to write some tests that simulated executing the `osascript` command using the Python `subprocess` module.

I wanted my tests to run on Linux CI machines, where that command would not exist.

After failing to use `unittest.mock.patch` to solve this, I went looking for alternatives. I found [pytest-subprocess](https://pypi.org/project/pytest-subprocess/).

Here's the relevant section of [the test I wrote](https://github.com/dogsheep/apple-notes-to-sqlite/blob/0.1/tests/test_apple_notes_to_sqlite.py):

```python
from apple_notes_to_sqlite.cli import cli, COUNT_SCRIPT

FAKE_OUTPUT = b"""
The stuff I would expect to be returned by log lines in
my osascript script.
"""

def test_apple_notes_to_sqlite_dump(fp):
    fp.register_subprocess(["osascript", "-e", COUNT_SCRIPT], stdout=b"2")
    fp.register_subprocess(["osascript", "-e", fp.any()], stdout=FAKE_OUTPUT)
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["--dump"])
        # ...
```
`fp` is the fixture provided by the package (you need to `pip install pytest-subprocess` for this to work).

`COUNT_SCRIPT` here is the first of my `osascript` constants. It looks like this (in `cli.py`):

```python
COUNT_SCRIPT = """
tell application "Notes"
    set noteCount to count of notes
end tell
log noteCount
"""
```
That first fixture line says that any time my program calls `osascript -e that-count-script` the return value sent to standard output should be a binary string `2`.

```python
fp.register_subprocess(["osascript", "-e", COUNT_SCRIPT], stdout=b"2")
```

The second call to `subprocess` made by my script is more complicated - it involves a script that is dynamically generated.

```python
fp.register_subprocess(["osascript", "-e", fp.any()], stdout=FAKE_OUTPUT)
```

I eventually figured that using `fp.any()` was easier than specifying the exact script. This is a wildcard value which matches any string. It returns the full `FAKE_OUTPUT` variable as the simulated standard out.

What's useful about `pytest-subprocess` is that it works for both `subprocess.check_output()` and more complex `subprocess.Popen()` calls - both of which I was using in this script.
