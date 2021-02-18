# Using sphinx.ext.extlinks for issue links

Datasette's [release notes](https://github.com/simonw/datasette/blob/main/docs/changelog.rst) are formatted using Sphinx. Almost every bullet point links to the corresponding GitHub issue, so they were full of lines that look like this:

``` - Fixed a bug where ``?_search=`` and ``?_sort=`` parameters were incorrectly duplicated when the filter form on the table page was re-submitted. (`#1214 <https://github.com/simonw/datasette/issues/1214>`__) ```

I noticed that [the aspw documentation](https://github.com/simonw/datasette/issues/1227) was using `sphinx.ext.extlinks` to define a macro for this: `` :issue:`268` `` - so I decided to configure that for Datasette.

I added the following to the `conf.py` for my documentation:

```python
extensions = ["sphinx.ext.extlinks"]

extlinks = {
    "issue": ("https://github.com/simonw/datasette/issues/%s", "#"),
}
```

Then in Visual Studio Code I opened the "Edit -> Replace in Files" tool. I used this search pattern:

    `#(\d+) <https://github.com/simonw/datasette/issues/\1>`__

And this as the replacement value:

    :issue:`$1`

Note that the search pattern uses `\1` as the group reference for the captured number, but in the replacement value you use `$1` to re-use that value.

Here's [the commit](https://github.com/simonw/datasette/commit/d2d53a5559f3014cccba2cba7e1eab1e5854c759) where I applied that change to Datasette's existing documentation.
