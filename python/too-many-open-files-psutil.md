# Using psutil to investigate "Too many open files"

I was getting this intermittent error running my Datasette test suite:

    OSError: [Errno 24] Too many open files

To figure out what was going on, I used the `psutil` package and its `open_files()` method.

Here's the documentation for [psutil.Process.open_files](https://psutil.readthedocs.io/en/latest/#psutil.Process.open_files).

I ran `pip install psutil` in my virtual environment.

Then I ran `pytest --pdb` to drop into a Python debugger when a test failed.

In the debugger I ran this:

```python
import psutil
for f in psutil.Process().open_files(): print(f)
```
This showed the current list of open files for that process, which gave me [some clues](https://github.com/simonw/datasette/issues/1843) to help me start resolving the problem.
