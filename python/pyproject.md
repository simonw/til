# Python packages with pyproject.toml and nothing else

I've been using `setuptools` and `setup.py` for my Python packages for a long time: I like that it works without me having to think about installing and learning any additional tools such as [Flit](https://flit.pypa.io/) or [pip-tools](https://pip-tools.readthedocs.io/) or [Poetry](https://python-poetry.org/) or [Hatch](https://github.com/pypa/hatch).

`pyproject.toml` is the new (or not so new, [the PEP](https://peps.python.org/pep-0621/) is dated June 2020) standard for Python packaging metadata.

Today I figured out how to package a project with a single `pyproject.toml` file, using just `pip` and `build` to install and build that package.

(Note that the approach described in this document likely only works for pure Python packages. If your package includes any binary compiled dependencies you likely need to use a different approach.)

Here's the simplest `pyproject.toml` file I could get to work:

```toml
[project]
name = "demo-package"
version = "0.1"
```
I put this in a folder called `/tmp/demo-package` and then added a file to that folder called `demo_package.py` containing just this:

```python
def say_hello():
    print("Hello world")
```

When I'm working with packages there are really just two main things I do with them. I install them in "editable" development mode using `pip install -e` and I build packages for distribution using `python -m build`.

It turns out both of those commands now work on a folder containing just a `pyproject.toml` file, with no `setup.py` or `setup.cfg` or any of the other old packaging files!

## It defaults to setuptools

The reason this works is that a `pyproject.toml` file without a `[build-system]` section defaults to using [setuptools](https://setuptools.pypa.io/). Effectively it behaves the same as if you had added this block to the file:

```toml
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"
```
If you want to be explicit you can add that section - it does no harm, and likely makes the file easier to understand in the future. I was excited to find that it worked without this though.

## Editable mode with pip install

To demonstrate, I'm going to create a virtual environment and install my package in editable mode.

I put my two files (`pyproject.toml` and `demo_package.py`) in a `/tmp/demo-package` folder.

Then I created a virtual environment elsewhere with:

```bash
python3 -m venv venv
source venv/bin/activate
```
Then I used `pip install -e` to install an editable version of my new, minimal package:
```bash
pip install -e /tmp/demo-package 
```
```
Obtaining file:///tmp/demo-package
  Installing build dependencies ... done
  Checking if build backend supports build_editable ... done
  Getting requirements to build editable ... done
  Preparing editable metadata (pyproject.toml) ... done
Building wheels for collected packages: demo-package
  Building editable for demo-package (pyproject.toml) ... done
  Created wheel for demo-package: filename=demo_package-0.1-0.editable-py3-none-any.whl size=2307 sha256=0c023b20a46bf6e5566658df20866517d7bd9a692fcd2587bc95bf6382881563
  Stored in directory: /private/var/folders/x6/31xf1vxj0nn9mxqq8z0mmcfw0000gn/T/pip-ephem-wheel-cache-jh0fk5iu/wheels/a8/98/44/74568efecc0982a4601580062159e9b5c989ed6f0a697e5c9b
Successfully built demo-package
Installing collected packages: demo-package
Successfully installed demo-package-0.1
```
I can now import my package and run that function:
```bash
python
```
```pycon
>>> import demo_package
>>> demo_package.say_hello()
Hello world
```
If I edit the `demo_package.py` file and change the message to say "Hello word, once more", I can run that again in the virtual environment:
```pycon
>>> import demo_package
>>> demo_package.say_hello()
Hello world, once more
```
So I now have a package that I can actively develop, and I can install it into any environments that need it in a way that will reflect changes to my package.

## Building a package with python -m build

With `setup.py` I used to run `python setup.py sdist wheel` to build source distribution and wheel files.

These days the [build](https://pypi.org/project/build/) package is the recommended way to do that.

I can install that using:

```python
python3 -m pip install build
```
Then run it in my `/tmp/demo-package` folder like this:
```bash
python3 -m build
```
Output (truncated):
```
* Creating venv isolated environment...
* Installing packages in isolated environment... (setuptools >= 40.8.0, wheel)
* Getting build dependencies for sdist...
running egg_info
...
Creating tar archive
removing 'demo-package-0.1' (and everything under it)
* Building wheel from sdist
...
adding 'demo_package.py'
adding 'demo_package-0.1.dist-info/METADATA'
adding 'demo_package-0.1.dist-info/WHEEL'
adding 'demo_package-0.1.dist-info/top_level.txt'
adding 'demo_package-0.1.dist-info/RECORD'
removing build/bdist.macosx-13-arm64/wheel
Successfully built demo-package-0.1.tar.gz and demo_package-0.1-py3-none-any.whl
```
These two files were created in `/tmp/demo-package/dist`:
```bash
ls dist
```
```
demo-package-0.1.tar.gz
demo_package-0.1-py3-none-any.whl
```
## It finds the Python files for you

With `setup.py` I'm used to putting quite a bit of effort into telling Python which files should be included in the package - and making sure it doesn't include the `tests/` and `docs/` folder.

As far as I can tell, the default behaviour now is to find all `*.py` files and all `*/*.py` files and include those - but to exclude common patterns such as `tests/` and `docs/` and `tests.py` and `test_*.py`.

This behaviour is defined by `setuptools`. The [Automatic Discovery](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html#automatic-discovery) section of the `setuptools` documentation describes these rules in detail.

## Adding metadata

I can add metadata to my package directly in that `pyproject.toml`. `description = ` can add a short description, and `readme = "filename"` can add a long description imported from a README file.

```toml
[project]
name = "demo-package"
version = "0.1"
description = "This is a demo package"
readme = "README.md"
```
Then save a `README.md` file in the same directory containing markdown describing the project:
```markdown
# demo-package

This is a demonstration package.

## Usage

>>> import demo_package
>>> demo_package.say_hello()
```
I also like to include an author, a homepage URL and project URLs for things like my issue tracker in my projects. Here's what that would look like:
```toml
[project]
name = "demo-package"
version = "0.1"
description = "This is a demo package"
readme = "README.md"
authors = [{name = "Simon Willison"}]
license = {text = "Apache-2.0"}
classifiers = [
    "Development Status :: 4 - Beta"
]

[project.urls]
Homepage = "https://github.com/simonw/demo-package"
Changelog = "https://github.com/simonw/demo-package/releases"
Issues = "https://github.com/simonw/demo-package/issues"
```
Here's [a list](https://pypi.org/classifiers/) of the available `classifiers`.

## Adding dependencies

Dependencies can be added in a `dependencies=` list like this:

```toml
[project]
# ...
dependencies = [
    "httpx"
]
```
These can use version specifiers, for example `httpx>=0.18.0` or `httpx~=0.18`.

## Test dependencies

I like being able to run `pip install -e '.[test]'` to install test dependencies - things like `pytest`, which are needed to run the project tests but shouldn't be bundled with the project itself when it is installed.

Those can be added in a section like this:

```toml
[project.optional-dependencies]
test = ["pytest"]
```
I added that to my `/tmp/demo-package/pyproject.toml` file, then ran this in my elsewhere virtual environment:
```bash
pip install -e '/tmp/demo-package[test]'
```
The result was an installation of `pytest`, visible when I ran `pip freeze`.

## Package data

The build script will automatically find all Python files, but if you have other assets such as static CSS ond JavaScript, or templates with a `.html` extension, you need to specify package data. This works for adding everything in the `demo_package/static/` and `demo_package/templates/` directories:
```toml
[tool.setuptools.package-data]
demo_package = ["static/*", "templates/*"]
```
## Command-line scripts

I often build tools which include command-line scripts. These can be defined by adding a `scripts=` section to the `[project]` block, like this:

```toml
[project]
# ... previous configuration
scripts = { demo_package_hello = "demo_package:say_hello" }
```
Or use this alternative syntax (here borrowed from my [db-build](https://github.com/simonw/db-build) Click app):
```toml
[project.scripts]
db-build = "db_build.cli:cli"
```
Now run this again:
```bash
pip install -e '/tmp/demo-package'
```
Typing `demo_package_hello` runs that function:
```bash
demo_package_hello
```
```
Hello world, once more
```
We can see how that works with the following commands:
```bash
type demo_package_hello
```
```
demo_package_hello is /private/tmp/my-new-environment/venv/bin/demo_package_hello
```bash
cat $(which demo_package_hello)
```
```
#!/private/tmp/my-new-environment/venv/bin/python3
# -*- coding: utf-8 -*-
import re
import sys
from demo_package import say_hello
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(say_hello())
```

## Entry points for Pluggy plugins

I use [Pluggy](https://pluggy.readthedocs.io/) to provide a plugins mechanism for my [Datasette](https://datasette.io/) and [LLM](https://llm.datasette.io/) projects.

Plugins require entry points to be configured in their packaging. The recipe for doing that for an LLM plugin (with [this feature](https://github.com/simonw/llm/issues/53)) looks like this:
```toml
[project.entry-points.llm]
markov = "llm_markov"
```
For a [Datasette plugin](https://docs.datasette.io/en/stable/writing_plugins.html) that would look like this:
```toml
[project.entry-points.datasette]
cluster_map = "datasette_cluster_map"
```
## These packages work with pipx

Having built my new package (with the `scripts=` section) using `python3 -m build`, I then tried installing it in a brand new terminal window using [pipx](https://pypa.github.io/pipx/):

```bash
pipx install /tmp/demo-package/dist/demo_package-0.1-py3-none-any.whl
```
```
  installed package demo-package 0.1, installed using Python 3.11.4
  These apps are now globally available
    - demo_package_hello
done! ✨ 🌟 ✨
```
And now I can run this command anywhere on my computer:
```
demo_package_hello
```
```
Hello world, once more
```
I can see where it was installed using this:
```bash
which demo_package_hello
```
```
/Users/simon/.local/bin/demo_package_hello
```
## pip and build both depend on tomli

One thing that puzzled me about this: TOML support was only added to the Python standard library in Python 3.11 - how come the `pip` and `build` packages are able to use it?

It turns out `pip` vendors [tomli](https://github.com/hukkin/tomli):

- https://github.com/pypa/pip/tree/23.1.2/src/pip/_vendor/tomli

And `build` lists it as a dependency for versions of Python prior to 3.11:

- https://github.com/pypa/build/blob/0.10.0/pyproject.toml#L40

```toml
dependencies = [
  # ...
  'tomli >= 1.1.0; python_version < "3.11"',
]
```
