# Testing a Click app with streaming input

For [sqlite-utils#364](https://github.com/simonw/sqlite-utils/issues/364) I needed to write a test for a [Click](https://click.palletsprojects.com/) app which dealt with input streamed to standard input. I needed to run some assertions during that process, which ruled out the usual [CliRunner.invoke()](https://click.palletsprojects.com/en/8.0.x/testing/) testing tool since that works by running the command until completion.

I decided to use `subprocess` to run the application. Here's the pattern I came up with for the test:
```python
def test_insert_streaming_batch_size_1(db_path):
    # https://github.com/simonw/sqlite-utils/issues/364
    # Streaming with --batch-size 1 should commit on each record
    # Can't use CliRunner().invoke() here bacuse we need to
    # run assertions in between writing to process stdin
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "sqlite_utils",
            "insert",
            db_path,
            "rows",
            "-",
            "--nl",
            "--batch-size",
            "1",
        ],
        stdin=subprocess.PIPE
    )
    proc.stdin.write(b'{"name": "Azi"}\n')
    proc.stdin.flush()
    # Without this delay the data wasn't yet visible
    time.sleep(0.2)
    assert list(Database(db_path)["rows"].rows) == [{"name": "Azi"}]
    proc.stdin.write(b'{"name": "Suna"}\n')
    proc.stdin.flush()
    time.sleep(0.2)
    assert list(Database(db_path)["rows"].rows) == [{"name": "Azi"}, {"name": "Suna"}]
    proc.stdin.close()
    proc.wait()
    assert proc.returncode == 0
```
The first trick I'm using here is running `sys.executable` to start a Python process. This ensures I run the Python that is available in the current virtual environment.

I modified my `sqlite-utils` command such that it could also be run using `python -m sqlite_utils` - see [sqlite-utils#368](https://github.com/simonw/sqlite-utils/issues/368) for details.

Setting `stdin=subprocess.PIPE` allows me to write data to the process's standard input using `proc.stdin.write()`.

I realized I needed to call `proc.stdin.flush()` after each write to ensure the write was pushed to the process in a predictable manner.

At the end of the test, running `proc.stdin.close()` is equivalent to sending an end-of-file, then `proc.wait()` ensures the process has finished and terminated.
