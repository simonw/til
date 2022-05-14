# Efficiently copying a file

**TLDR:** Use `shutil.copyfileobj(fsrc, fdst)`

I'm writing a Datasette plugin that handles an uploaded file, borrowing the Starlette mechanism for handling file uploads, [documented here](https://www.starlette.io/requests/#request-files).

Starlette uploads result in a [SpooledTemporaryFile](https://docs.python.org/3/library/tempfile.html#tempfile.SpooledTemporaryFile) file-like object. These look very much like a file, with one frustrating limitation: they don't have a defined, stable path on disk.

I thought that this meant that you couldn't easily copy it, and ended up coming up with this recipe based on [this code](https://github.com/abersheeran/baize/blob/23791841f30ca92775e50a544a8606d1d4deac93/baize/datastructures.py#L543-L561) I spotted in the [BáiZé](https://github.com/abersheeran/baize) framework:

```python
from shutil import COPY_BUFSIZE

with open(new_filepath, "wb+") as target_file:
    source_file.seek(0)
    source_read = source_file.read
    target_write = target_file.write
    while True:
        buf = source_read(COPY_BUFSIZE)
        if not buf:
            break
        target_write(buf)
```
`COPY_BUFSIZE` defined by Python [here](https://github.com/python/cpython/blob/v3.10.4/Lib/shutil.py#L42) - it handles the difference in ideal buffer size between Windows and other operating systems:
```python
COPY_BUFSIZE = 1024 * 1024 if _WINDOWS else 64 * 1024
```
But then I sat down to write this TIL, and stumbled across [shutil.copyfileobj(fsrc, fdst)](https://docs.python.org/3/library/shutil.html#shutil.copyfileobj) in the standard library which implements the [exact same pattern](https://github.com/python/cpython/blob/v3.10.4/Lib/shutil.py#L187-L198)!

```python
def copyfileobj(fsrc, fdst, length=0):
    """copy data from file-like object fsrc to file-like object fdst"""
    # Localize variable access to minimize overhead.
    if not length:
        length = COPY_BUFSIZE
    fsrc_read = fsrc.read
    fdst_write = fdst.write
    while True:
        buf = fsrc_read(length)
        if not buf:
            break
        fdst_write(buf)
```
So you should use that instead.
