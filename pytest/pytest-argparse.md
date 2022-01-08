# Writing pytest tests against tools written with argparse

I usually build command-line tools using [Click](https://click.palletsprojects.com/) (and my [click-app](https://github.com/simonw/click-app) cookiecutter template), which includes a really nice [set of tools](https://click.palletsprojects.com/en/8.0.x/testing/) for writing tests.

Today I decided to try building a tool called [stream-delay](https://github.com/simonw/stream-delay) using [argparse]() from the Python standard library, since it didn't need any other dependencies.

The one challenge I had was how to write the tests. I used [pytest](https://pytest.org/) as a test-only dependency.

Here's the pattern I came up with, using the [capsys pytest fixture](https://docs.pytest.org/en/6.2.x/capture.html) to capture standard output from my tool.

```python
from stream_delay import main
import pytest

@pytest.mark.parametrize("option", ("-h", "--help"))
def test_help(capsys, option):
    try:
        main([option])
    except SystemExit:
        pass
    output = capsys.readouterr().out
    assert "Stream one or more files with a delay" in output
```
My `main()` function starts like this:
```python
import argparse, sys

parser = argparse.ArgumentParser(
    description="Stream one or more files with a delay between each line"
)
parser.add_argument("files", type=argparse.FileType("r"), nargs="*", default=["-"])
parser.add_argument("-d", "--delay-in-ms", type=int, default=100)


def main(args=None):
    parsed_args = parser.parse_args(args)
    delay_in_s = float(parsed_args.delay_in_ms) / 1000
    # ...
```
As you can see, `main()` takes an optional list of arguments. The default for that is `None` which will cause `argparse` to read `sys.argv` - but I can inject arguments to the function from my tests if I need to.

I'm catching the `SystemExit` exception because this will be raised by default if you use `-h` or `--help` - but I still want to finish my test execution so I can inspect the captured output.

Complete code:

- [stream_delay.py](https://github.com/simonw/stream-delay/blob/0.1/stream_delay.py)
- [tests/test_stream_delay.py](https://github.com/simonw/stream-delay/blob/0.1/tests/test_stream_delay.py)
