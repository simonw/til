# Trying out Python packages with ipython and uvx

I figured out a really simple pattern for experimenting with new Python packages today:

```bash
uvx --with llm --with sqlite-utils ipython
```
This command will work if you have [uv](https://github.com/astral-sh/uv) installed and nothing else. It uses [uvx](https://docs.astral.sh/uv/guides/tools/) to install and run the excellent [ipython](https://ipython.org/) Python REPL in a new, dedicated virtual environment with two additional Python libraries - [llm](https://llm.datasette.io/) and [sqlite-utils](https://sqlite-utils.datasette.io/). You don't need to install ANY of those packages first - `uvx` will fetch and cache them the first time you run this, and reuse the cached versions on future invocations.

![Screenshot of the command running - I can then import llm and sqlite_utils and start using them.](https://github.com/user-attachments/assets/016ee9a2-636f-4ee7-ba43-5356a6b91b90)

You can also set which Python version will be used with the `--python 3.13` option:

```bash
uvx --python 3.13 --with llm --with sqlite-utils ipython
```

I turned this into a shell script (with [help from Claude](https://gist.github.com/simonw/c6f7e7f27a29eb6b7df0876c78f66ac2)):

```bash
#!/bin/sh
# itry - A portable script for launching ipython with uvx packages

# Show help if requested
[ "$1" = "--help" ] && {
    echo "Usage: itry [packages...]"
    echo "Example: itry llm sqlite-utils datasette"
    exit 0
}

# Initialize empty string for packages
PACKAGES=""

# Process all arguments, adding --with before each
for arg in "$@"; do
    PACKAGES="$PACKAGES --with $arg"
done

# Remove leading space if present
PACKAGES="${PACKAGES# }"

# Execute uvx command with Python 3.13
exec uvx $PACKAGES --python 3.13 ipython
```
This is saved as `~/.local/bin/itry` - then `chmod 755 ~/.local/bin/itry` - and now I can jump straight into an interactive ipython REPL with any Python packages I like using this command:
```bash
itry cowsay
```
Then:
```python
import cowsay
cowsay.cow("hello")
```
```
  _____
| hello |
  =====
     \
      \
        ^__^
        (oo)\_______
        (__)\       )\/\
            ||----w |
            ||     ||
```
