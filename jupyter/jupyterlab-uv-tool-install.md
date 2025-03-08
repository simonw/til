# Running jupyterlab via uv tool install

I tried to get [jupyterlab](https://jupyter.org/install) working via `uv tool install` today and ran into some sharp edges.

You can start like this:
```bash
uv tool install jupyterlab
```
That ran for a while and output:
```
Installed 4 executables: jlpm, jupyter-lab, jupyter-labextension, jupyter-labhub
```
It also gave me a warning about my PATH. I fixed that with:
```
uv tool ensure-path
```
On one other machine this didn't work because it refused to over-write a previous installation. The fix was to run `uv tool install` with `--force`:
```bash
uv tool install jupyterlab --force
```
Now we can start jupyterlab with:
```bash
jupyter-lab
```
## Getting %pip to work

This was the biggest sticking point for me. Jupyter has a useful magic command for installing packages:

```python
%pip install llm
```
When I tried to run this I got this error:

> `/Users/simon/.local/share/uv/tools/jupyterlab/bin/python: No module named pip`

It turns out we have an installation with no `pip` binary.

There may be a better way to do this, but I found that this worked, run in a Jupyter notebook cell:

```python
import subprocess, sys
subprocess.check_call([sys.executable, "-m", "ensurepip"])
```
After I ran this, the `%pip` magic command worked as expected - I didn't even need to restart the kernel.

## Reported to Jupyter

I [opened an issue](https://github.com/jupyterlab/jupyterlab/issues/17375) about this and [submitted a PR](https://github.com/jupyterlab/jupyterlab/pull/17376) with a potential fix.
