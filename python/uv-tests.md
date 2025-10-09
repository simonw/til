# Running tests against different Python versions with uv

A quick `uv` recipe I figured out today, for running the tests for a project against multiple Python versions.

The key command option is `uv run --with .[test]`.

Start with any Python project that has a `[test]` extra defined, for example:

```bash
cd /tmp
git clone https://github.com/simonw/datasette
cd datasette
```
Then run `uv` against it with a specific Python version like this:

```bash
uv run --python 3.14 --isolated --with '.[test]' pytest -n auto
```
Here I'm using `--isolated` to make sure nothing from any other environments sneaks in, `--with '.[test]'` to install both the project dependencies and the test dependencies and `pytest -n auto` to run the tests in parallel using an automatically determined number of workers (via `pytest-xdist`).
