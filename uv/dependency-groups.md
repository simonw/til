# Dependency groups and uv run

I've adopted a new (to me) pattern for my Python projects to make them easier to hack on using `uv run`. I'm using a [PEP 735 dependency group](https://peps.python.org/pep-0735/) called `dev` to declare my development dependencies - in particular `pytest` - such that running `uv run pytest` executes the tests for my project without me having to even think about setting up a virtual environment first.

Here's the pattern I'm using. I start by creating a new library using `uv init --lib` like this:

```bash
mkdir my-new-library
cd my-new-library
uv init --lib
```
This creates a `pyproject.toml` file like this:

```toml
[project]
name = "my-new-library"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
authors = [
    { name = "Simon Willison", email = "...@gmail.com" }
]
requires-python = ">=3.10"
dependencies = []

[build-system]
requires = ["uv_build>=0.9.15,<0.10.0"]
build-backend = "uv_build"
```
It also creates a `src/my_new_library/__init__.py` file with a `hello()` example function.

Next, I add `pytest` as a development dependency using this command:
```bash
uv add --dev pytest
```
Doing so adds a new section to the end of that `pyproject.toml` file:

```toml
[dependency-groups]
dev = [
    "pytest>=9.0.1",
]
```
This also creates the virtual environment in `.venv` and `uv.lock` file, but we don't need to think about those.

Then I create a test:

```bash
mkdir tests
echo  'from my_new_library import hello

def test_hello():
    assert hello() == "Hello from my-new-library!"' > tests/test_my_new_library.py
```
Now I can run that test site using:
```bash
uv run pytest
```
The `dev` dependency group is a special case for `uv run` - it will always install those dependencies as well such that commands like `pytest` can work correctly.

When you package a project for distribution the `dev` dependencies will not be automatically installed for users of your package.

## The importance of [build-system] for specifying a package

That `[build-system]` section is crucial, because it tells `uv` that the directory should be treated as a "package". This means that when `uv run` executes it installs the current directory as an editable package in the virtual environment.

Removing `[build-system]` and then `rm -rf .venv` to delete the virtual environment results in the following error when trying to run `uv run pytest`:

```
________________ ERROR collecting tests/test_my_new_library.py _________________
ImportError while importing test module '/private/tmp/my-new-library/tests/test_my_new_library.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/opt/homebrew/Caskroom/miniconda/base/lib/python3.10/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
tests/test_my_new_library.py:1: in <module>
    from my_new_library import hello
E   ModuleNotFoundError: No module named 'my_new_library'
=========================== short test summary info ============================
ERROR tests/test_my_new_library.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
=============================== 1 error in 0.07s ===============================
```
Adding the `[build-system]` section back in gets rid of this error.

There's an alternative to having a `[build-system]` section, which is to add this to the `pyproject.toml` file instead:

```toml
[tool.uv]
package = true
```
I [had Claude Code investigate this](https://gistpreview.github.io/?e5405e5770d963ee708eea5ecc769457) and it found [this section of code](https://github.com/astral-sh/uv/blob/d2db06983a20630de4247e4a94af7edd5aa35689/crates/uv-workspace/src/pyproject.rs#L135-L143) explaining what's going on:

```rust
pub fn is_package(&self, require_build_system: bool) -> bool {
    // If `tool.uv.package` is set, defer to that explicit setting.
    if let Some(is_package) = self.tool_uv_package() {
        return is_package;
    }
    // Otherwise, a project is assumed to be a package if `build-system` is present.
    self.build_system.is_some() || !require_build_system
}
```

So there's no need to use that `[tool.uv]` section if you already have a `[build-system]` section.

## Installation in CI

If you're still using regular `pip` in your CI scripts you'll need to ensure the `dev` dependency group is installed like this:

```bash
pip install . --group dev
```

## The end result

Projects that use this pattern become a whole lot easier for other people to hack on. I first used this for my [datasette-extract](https://github.com/datasette/datasette-extract) package, with the result that checking out and running the tests is now a case of running just the following commands:

```bash
git clone https://github.com/datasette/datasette-extract
cd datasette-extract
uv run pytest
```
No need to think about virtual environments or development dependencies - this just works.

Building a distributable wheel of the project is a one-liner as well:
```bash
uv build
```
This creates two files:
```
dist/datasette_extract-0.2a0-py3-none-any.whl
dist/datasette_extract-0.2a0.tar.gz
```
The `.tar.gz` file should contain everything including the tests - the `.whl` file should contain just the non-development Python code.


## Bonus tip: defining dev in terms of other dependency groups

The `dev` group is a special case: tools like `uv run` will install everything in that group automatically.

What if you want to divide up your dependencies into test dependencies, documentation dependencies and so on?

Thanks to [Martín Gaitán's python-package-copier-template](https://github.com/mgaitan/python-package-copier-template/blob/676a89117b10f6267cfe45dd1c36efc80af95be7/project/pyproject.toml.jinja#L97-L121) I learned about this pattern for defining `dev` in terms of other groups:

```toml
[dependency-groups]
test = [
    "pytest",
    "pytest-asyncio"
]
docs = [
    "sphinx"
]
dev = [
    { include-group = "test" },
    { include-group = "docs" }
]
```

Now if you just want to use the test depenedncies you can run this:
```bash
uv run --group test pytest
```
