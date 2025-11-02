# Testing different Python versions with uv with-editable and uv-test

A quick `uv` recipe I figured out today, for running the tests for a project against multiple Python versions.

The key command option is `uv run --with-editable .[test]`.

Start with any Python project that has a `[test]` extra defined, for example:

```bash
cd /tmp
git clone https://github.com/simonw/datasette
cd datasette
```
Then run `uv` against it with a specific Python version like this:

```bash
uv run --python 3.14 --isolated --with-editable '.[test]' pytest -n auto
```
Here I'm using `--isolated` to make sure nothing from any other environments sneaks in.

The `--with-editable '.[test]'` part is important - it tells `uv` to install the current project in editable mode so that changes you make will be picked up. I first tried this using `--with '.[test]'` and was confused as to why changes I made to the code weren't being picked up when I re-ran the tests.

Datasette uses `pytest-xdist` to run tests in parallel, so I added `-n auto` to have it automatically use all available CPU cores.

## uv-test

I wrote a little helper script (with [ChatGPT's help](https://chatgpt.com/share/68e729ea-13f4-8006-8dd5-17b031ecf8eb)) to make this easier to remember. It uses Python 3.14 by default but you can pass a different version as the `-p` argument. Any subsequent arguments will be passed to `pytest`.
```sh
#!/bin/sh
set -eu  # (no pipefail in POSIX sh)

usage() {
  echo "Usage: uv-test [-p|--python PY_VER] [pytest args...]"
  echo "  -p, --python  Set Python version (default: \$UV_PY or 3.14)"
  echo "  -h, --help    Show this help"
}

PYVER="${UV_PY:-3.14}"

# Parse only our flags; pass the rest to pytest
while [ $# -gt 0 ]; do
  case "$1" in
    -p|--python)
      shift
      [ $# -gt 0 ] || { echo "error: -p/--python requires a version" >&2; exit 2; }
      PYVER="$1"; shift ;;
    -h|--help) usage; exit 0 ;;
    --) shift; break ;;
    *) break ;;
  esac
done

command -v uv >/dev/null 2>&1 || { echo "error: 'uv' not found in PATH" >&2; exit 127; }
if [ ! -f pyproject.toml ] && [ ! -f setup.py ]; then
  echo "error: no project file found (need pyproject.toml or setup.py). Run from project root." >&2
  exit 1
fi

exec uv run --python "$PYVER" --isolated --with-editable '.[test]' -- python -m pytest "$@"
```
Make it executable and put it somewhere in your PATH, then you can run it like this:

```bash
uv-test
```
Or for a specific Python version:

```bash
uv-test -p 3.13
```
And for custom `pytest` arguments:

```bash
uv-test -k permissions
```
Or combined:

```bash
uv-test -p 3.12 -k permissions -vv
```

## Variants: tadd and radd

For [Datasette issue #2549](https://github.com/simonw/datasette/issues/2549) I found myself needing to run the test suites for *many* different Datasette plugins against my local not-released `main` branch of Datasette. I ended up creating two new utility scripts, chmod 755 and on my path.

Here's `tadd`, for "test against Datasette dev":

```bash
#!/bin/sh
uv run --no-project --isolated \
  --with-editable '.[test]' --with-editable ~/dev/datasette \
  python -m pytest "$@"
```
And `radd`, for "run against Datasette dev":

```bash
#!/bin/sh
uv run --no-project --isolated \
  --with-editable '.[test]' --with-editable ~/dev/datasette \
  datasette "$@"
```
They both take arguments, e.g.:

```bash
tadd -x --pdb
radd content.db -p 8004 --root
```
