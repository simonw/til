# Adding Sphinx autodoc to a project, and configuring Read The Docs to build it

I built a [new API reference page](https://sqlite-utils.datasette.io/en/latest/reference.html) today for `sqlite-utils`, using the Sphinx [autodoc extension](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html) to extract docstrings from the code and use them to build a full class reference.

I've avoided this kind of documentation in the past because I think narrative prose is a *much* better way of providing documentation - but ``sqlite-utils`` already has [detailed narrative prose](https://sqlite-utils.datasette.io/en/stable/python-api.html), so I felt that adding reference documentation powered by docstrings could enhance that project - while also providing better inline document for tools such as Visual Studio Code and Jupyter.

<img width="500" alt="Screenshot of the new rendered documentation" src="https://user-images.githubusercontent.com/9599/128947691-403e0332-5bab-4851-a9aa-c29e759e944c.png">

## Setting up autodoc

Getting autodoc working in my local documentation environment took a few steps.

First, I added `"sphinx.ext.autodoc"` to the `extensions = []` list in my `docs/conf.py` file.

Then I created a new page in ``docs/reference.rst`` and added the following:

```rst
===============
 API Reference
===============

.. _reference_db_database:

sqlite_utils.db.Database
========================

.. autoclass:: sqlite_utils.db.Database
    :members:
    :undoc-members:
```
This was enough to start generating documentation for the `sqlite_utils.db.Database` class.

`:members:` means "show documentation for everything in the class that has a docstring".

`:undoc-members:` means "also include class members that don't have a docstring yet".

I added my own rST headings and reference links - this ensured that the classes would automatically show up in the table of contents for my documentation.

## More options

I ended up using the following:

```rst
.. autoclass:: sqlite_utils.db.Database
    :members:
    :undoc-members:
    :show-inheritance:
    :special-members: __getitem__
    :exclude-members: use_counts_table, execute_returning_dicts, resolve_foreign_keys
```
`:show-inheritance:` adds a note about the inheritance hierarchy for the class.

By default `__special__` methods like `__getitem__` are not included. `:special-members:` fixes this for specified methods.

`:exclude-members;` accepts a comma-separated list of methods that shouldn't be shown in the documentation. I used this to remove some internal methods.

I could have renamed these to `_use_counts_table` but that would be a breaking API change, even though these methods are deliberately undocumented and shouldn't be used by anyone.

## Source, not alphabetical order

The class methods default to being shown in alphabetical order - adding ` autodoc_member_order = "bysource"` to `docs/conf.py` changed that to source order instead.

## reStructuredText in the docstrings

Adding reStructuredText to the docstrings works for formatting the generated API documentation. You can also use `:ref:reference-links`. Here's an example of a docstring with more complex formatting:

```python
    def rows_where(
        where: str = None,
        where_args: Optional[Union[Iterable, dict]] = None,
        order_by: str = None,
        select: str = "*",
        limit: int = None,
        offset: int = None,
    ) -> Generator[dict, None, None]:
        """
        Iterate over every row in this table or view that matches the specified
        where clause.

        - ``where`` - a SQL fragment to use as a ``WHERE`` clause, for example
          ``age > ?`` or``age > :age``.
        - ``where_args`` - a list of arguments (if using ``?``) or a dictionary
          (if using ``:age``).
        - ``order_by`` - optional column or fragment of SQL to order by.
        - ``select`` - optional comma-separated list of columns to select.
        - ``limit`` - optional integer number of rows to limit to.
        - ``offset`` - optional integer for SQL offset.

        Returns each row as a dictionary. See :ref:`python_api_rows` for more details.
        """
        if not self.exists():
            # ...
```
## Getting it working on Read The Docs

Read The Docs has the option to deploy branches - you can set that up in  the "Versions" tab. I was working in an `autodoc` branch - I set that branch to be "Active" and "Hidden", so it would be built by Read The Docs but not linked to from anywhere.

My first attempt failed to render the generated documentation, because Read The Docs did not know where to import my code from.

I solved that by adding a `.readthedocs.yaml` configuration file to my repository containing the following:

```yaml

version: 2

sphinx:
  configuration: docs/conf.py

python:
  version: "3.8"
  install:
  - method: pip
    path: .
    extra_requirements:
    - docs
```

The key thing here is that `install` block, which tells Read The Docs to run the equivalent of this before building the documentation:

    pip install -e '.[docs]'

For my repository that installs the `docs` optional dependencies from the `setup.py`, but also installs the `sqlite_utils` Python package itself. That way Sphinx can find and import `sqlite_utils.db.Database` in order to generate the documentation.

## The end result

The new page of documentation is now live at [en/latest/reference.html](https://sqlite-utils.datasette.io/en/latest/reference.html). The pull request in which I figured this all out is [sqlite-utils/pull/312](https://github.com/simonw/sqlite-utils/pull/312).
