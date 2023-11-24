# Running pip install '.[docs]' on ReadTheDocs

I decided to use ReadTheDocs for my in-development [datasette-enrichments](https://github.com/datasette/datasette-enrichments) project.

Previously when I've used ReadTheDocs I've had a `docs/` folder in my project with its own `docs/requirements.txt` file containing the requirements.

For this project I decided to try putting my documentation dependencies in a `setup.py` file (which I will likely upgrade to `pyproject.toml` in the future) like this:

```python
    # ...
    extras_require={
        "test": ["pytest", "pytest-asyncio", "black", "cogapp", "ruff"],
        "docs": [
            "sphinx==7.2.6",
            "furo==2023.9.10",
            "sphinx-autobuild",
            "sphinx-copybutton",
            "myst-parser",
            "cogapp",
        ],
    },
    # ...
```
When I'm working on this project locally I install these dependencies like so:
```bash
pip install -e '.[docs]'
```
It took me a few iterations to figure it out, so here's how to run that same command on ReadTheDocs using the `.readthedocs.yaml` configuration file:

```yaml
version: 2

build:
  os: ubuntu-22.04
  tools:
    python: "3.12"

sphinx:
  configuration: docs/conf.py

formats:
- pdf
- epub

python:
  install:
  - method: pip
    path: .
    extra_requirements:
    - docs
```
