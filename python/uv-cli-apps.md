# Using uv to develop Python command-line applications

I finally figured out a process that works for me for hacking on Python CLI utilities using [uv](https://docs.astral.sh/uv/) to manage my development environment, thanks to a little bit of help from Charlie Marsh.

## Starting a new app with cookiecutter

I already have a [cookiecutter](https://cookiecutter.readthedocs.io/) template I like using for CLI applications: [simonw/click-app](https://github.com/simonw/click-app).

Thanks to `uvx` I don't even need to install `cookiecutter` to use it:

```bash
uvx cookiecutter gh:simonw/click-app
```
This outputs a set of questions:
```
  [1/6] app_name (): demo-app
  [2/6] description (): Demo
  [3/6] hyphenated (demo-app): 
  [4/6] underscored (demo_app): 
  [5/6] github_username (): simonw
  [6/6] author_name (): Simon Willison
```
Which creates a `demo-app` directory containing the skeleton of a Python project.

## Setting up the uv virtual environment

`uv` has a number of different commands that can create and work with a `.venv` virtual environment directory.

```bash
cd demo-app
```
In this case, my `pyproject.toml` file (created by that cookiecutter template) defines a separate block of test dependencies. Here's that TOML file in full:

```toml
[project]
name = "demo-app"
version = "0.1"
description = "Demo"
readme = "README.md"
authors = [{name = "Simon Willison"}]
license = {text = "Apache-2.0"}
requires-python = ">=3.8"
classifiers = [
    "License :: OSI Approved :: Apache Software License"
]
dependencies = [
    "click"
]

[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project.urls]
Homepage = "https://github.com/simonw/demo-app"
Changelog = "https://github.com/simonw/demo-app/releases"
Issues = "https://github.com/simonw/demo-app/issues"
CI = "https://github.com/simonw/demo-app/actions"

[project.scripts]
demo-app = "demo_app.cli:cli"

[project.optional-dependencies]
test = ["pytest"]
```
The `[project.optional-dependencies]` section lists that `test` block. I can create a new virtual environment in `.venv/` and install both my project dependencies and those test dependencies like this:
```bash
uv sync --extra test
```
Here's the output:
```
Using CPython 3.11.1
Creating virtual environment at: .venv
Resolved 9 packages in 207ms
   Built demo-app @ file:///private/tmp/for-uv/demo-app
Prepared 1 package in 614ms
Installed 6 packages in 8ms
 + click==8.1.7
 + demo-app==0.1 (from file:///private/tmp/for-uv/demo-app)
 + iniconfig==2.0.0
 + packaging==24.1
 + pluggy==1.5.0
 + pytest==8.3.3
```

## Running the tests

Now I can run `pytest` using the `uv run` command:
```bash
uv run pytest
```
```
==================== test session starts ====================
platform darwin -- Python 3.11.1, pytest-8.3.3, pluggy-1.5.0
rootdir: /private/tmp/for-uv/demo-app
configfile: pyproject.toml
collected 1 item                                                                                          

tests/test_demo_app.py .                                                                            [100%]

===================== 1 passed in 0.03s =====================
```
This runs the `pytest` binary in the current `.venv/` environment. Note that I no longer have to "activate my virtual environment" - using `uv run` habitually solves that for me.

## Running the CLI tool itself

This line in `pyproject.toml` defines a script entry point for my CLI tool:
```toml
[project.scripts]
demo-app = "demo_app.cli:cli"
```
If the tool is correctly installed, I should be able to run it like this:
```bash
uv run demo-app
```
```
Usage: demo-app [OPTIONS] COMMAND [ARGS]...

  Demo

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  command  Command description goes here
```
I can also run it via Python like this (producing the same output):
```bash
uv run python -m demo_app
```

Crucially, the only reason this works is that I included _this_ section in `pyproject.toml`:

```bash
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
```
This may seem unrelated, but it's necessary for the `demo-app` alias to be correctly installed. As Charlie Marsh explained it:

> We support two kinds of projects: packages and non-packages. You want the former in this case, because you actually want to install the package in the environment. (We used to require this, but a lot of people want to be able to create lightweight projects that are just collections of scripts and don't need to be buildable / installable into an environment. We call those non-package projects.)
>
> We consider a project to be a "package" if `[build-system]` is defined or you set `tool.uv.package = true`
>
> Otherwise, we don't install the project itself into the environment.

## Using dev-dependencies instead

The only reason I needed to use `uv sync` here was to specify that `--extra test` to get my test dependencies installed as well.

As an aside, the following would have worked instead:

```bash
uv run --extra test pytest
```
I'd only need to pass that `--extra test` option the first time I ran `uv run` - on subsequent runs the test dependencies would already be installed.

Another option here would be to use the newer concept of [dev-dependencies](https://docs.astral.sh/uv/concepts/dependencies/#development-dependencies). `uv` supports these right now, and they've just been standardized by [PEP 735](https://peps.python.org/pep-0735/). To use those, add this to the `pyproject.toml` file:

```toml
[tool.uv]
dev-dependencies = ["pytest"]
```
Then `uv run pytest` would work without needing to use `--extra` to ensure the test dependencies are installed, and without needing to use `uv sync` at all.

## There's no need for uv pip

I got into a tangle at first trying to figure this out, because I thought I needed to use `uv pip` to manage my environment... and it turns out `uv pip` follows [these rules](https://docs.astral.sh/uv/pip/environments/#discovery-of-python-environments):

> When running a command that mutates an environment such as `uv pip sync` or `uv pip install`, uv will search for a virtual environment in the following order:
>
> - An activated virtual environment based on the `VIRTUAL_ENV` environment variable.
> - An activated Conda environment based on the `CONDA_PREFIX` environment variable.
> - A virtual environment at `.venv` in the current directory, or in the nearest parent directory.

I had Conda installed, which means I had a `CONDAPREFIX` environment variable set, which meant `uv pip` was ignoring my `.venv` directory entirely and using the Conda environment instead! 

This caused all manner of confusion. I [put together this document](https://gist.github.com/simonw/975dfa41e9b03bca2513a986d9aa3dcf) and asked Charlie for help, and he graciously unblocked me.

