# Defining setup.py dependencies using a URL

For [sqlite-utils issue 464](https://github.com/simonw/sqlite-utils/issues/464) I implemented a fix to a tiny bug in a dependency in [my own fork](https://github.com/simonw/beanbag-docutils/tree/bytes-in-url) on GitHub.

I wanted to use my fork as a dependency when I ran my build on ReadTheDocs - but for that particular project the ReadTheDocs dependencies are installed using the equivalent of `pip install '.[docs]'` (by [this configuration](https://github.com/simonw/sqlite-utils/blob/45e24deffea042b5db7ab84cd1eb63b3ed9bb9da/.readthedocs.yaml#L9-L12)) - and that `docs` set of extra requirements was defined in my `setup.py` file [like this](https://github.com/simonw/sqlite-utils/blob/271433fdd18e436b0a527ab899cb6f6fa67f23d0/setup.py#L33-L44):

```python
    extras_require={
        "test": ["pytest", "black", "hypothesis", "cogapp"],
        "docs": ["furo", "sphinx-autobuild", "codespell", "sphinx-copybutton"],
        "mypy": [
            "mypy",
            "types-click",
            "types-tabulate",
            "types-python-dateutil",
            "data-science-types",
        ],
        "flake8": ["flake8"],
    },
```

Any branch on GitHub can be installed by `pip` by finding the URL to the zip export of that branch. In this case that URL is:

`https://github.com/simonw/beanbag-docutils/archive/refs/heads/bytes-in-url.zip`

I tried adding that into the list of strings defined for the `"docs"` bundle and got this error when I ran `pip install -e '.[docs]'`:

```
Complete output (1 lines):
    error in sqlite-utils setup command: 'extras_require' must be a dictionary
    whose values are strings or lists of strings containing valid project/version requirement specifiers.
```

It turned out the solution was to use `packagename @ URL` instead, like this:

```python
    extras_require={
        "test": ["pytest", "black", "hypothesis", "cogapp"],
        "docs": [
            "furo",
            "sphinx-autobuild",
            "codespell",
            "sphinx-copybutton",
            "beanbag-docutils @ https://github.com/simonw/beanbag-docutils/archive/refs/heads/bytes-in-url.zip",
        ]
```
