# Running Python code in a subprocess with a time limit

I figured out how to run a subprocess with a time limit for [datasette-ripgrep](https://github.com/simonw/datasette-ripgrep), using the `asyncio.create_subprocess_exec()` method. The pattern looks like this:

```python
import asyncio

proc = await asyncio.create_subprocess_exec(
    "rg",
    "-e",
    ".*",
    stdout=asyncio.subprocess.PIPE,
    stdin=asyncio.subprocess.PIPE,
)

try:
    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=0.1)
    print(stdout)
except asyncio.exceptions.TimeoutError:
    print("Command timed out")

# If it timed out we should terminate the process
try:
    proc.kill()
except OSError:
    # Ignore 'no such process' error
    pass
```
For [datasette-seaborn](https://github.com/simonw/datasette-seaborn) I wanted to render a chart using the Python seaborn library with a time limit of five seconds for the render.

I realized I could do this by launching Python itself as the subprocess executable (using `sys.executable`) and sending Python code to `stdin` to be executed in a process, using the same time limit mechanism.

It seems to work! Here's the pattern wrapped up in a function:

```python
import asyncio, sys


async def execute_python_with_time_limit(code, time_limit):
    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        "-",
        stdout=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(code.encode("utf-8")), timeout=time_limit
        )
    except asyncio.exceptions.TimeoutError:
        raise
    return stdout, stderr
```
Example of using it (pasting into the shell you get from `python3 -m asyncio` in Python 3.8+):

```
>>> await execute_python_with_time_limit('print("hello")', 1)
(b'hello\n', None)
>>> await execute_python_with_time_limit('import time\ntime.sleep(1)', 0.7)
Traceback (most recent call last):
  File "/usr/local/opt/python@3.8/Frameworks/Python.framework/Versions/3.8/lib/python3.8/concurrent/futures/_base.py", line 439, in result
    return self.__get_result()
  File "/usr/local/opt/python@3.8/Frameworks/Python.framework/Versions/3.8/lib/python3.8/concurrent/futures/_base.py", line 388, in __get_result
    raise self._exception
  File "<console>", line 1, in <module>
  File "<console>", line 9, in execute_python_with_time_limit
  File "/usr/local/opt/python@3.8/Frameworks/Python.framework/Versions/3.8/lib/python3.8/asyncio/tasks.py", line 498, in wait_for
    raise exceptions.TimeoutError()
asyncio.exceptions.TimeoutError
```
It returns the stdout output of the code, so to use this you'll need to figure out some kind of serialization format for the data that is returned from the subprocess. JSON or pickle should work fine.

Is this a good idea? I think so, but I'd love to hear from you if there's a simpler, cleaner way to do this.
