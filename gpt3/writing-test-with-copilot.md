# Writing tests with Copilot

I needed to write a relatively repetitive collection of tests, for a number of different possible error states.

The code I was testing [looks like this](https://github.com/simonw/datasette/blob/187d91d68617ca48e34c1fb0c6722a40f8567d45/datasette/views/database.py#L561-L687):

```python
columns = data.get("columns")
rows = data.get("rows")
row = data.get("row")
if not columns and not rows and not row:
    return _error(["columns, rows or row is required"])

if rows and row:
    return _error(["Cannot specify both rows and row"])

if columns:
    if rows or row:
        return _error(["Cannot specify columns with rows or row"])
    if not isinstance(columns, list):
        return _error(["columns must be a list"])
    for column in columns:
        if not isinstance(column, dict):
            return _error(["columns must be a list of objects"])
        if not column.get("name") or not isinstance(column.get("name"), str):
            return _error(["Column name is required"])
        if not column.get("type"):
            column["type"] = "text"
        if column["type"] not in self._supported_column_types:
            return _error(
                ["Unsupported column type: {}".format(column["type"])]
            )
    # No duplicate column names
    dupes = {c["name"] for c in columns if columns.count(c) > 1}
    if dupes:
        return _error(["Duplicate column name: {}".format(", ".join(dupes))])
```
I wanted to write tests for each of the error cases. I'd already constructed the start of a parameterized `pytest` test for these.

I got Copilot/GPT-3 to write most of the tests for me.

First I used VS Code to select all of the `_error(...)` lines. I pasted those into a new document and turned them into a sequence of comments, like this:

```python
# Error: columns must be a list
# Error: columns must be a list of objects
# Error: Column name is required
# Error: Unsupported column type
# Error: Duplicate column name
# Error: rows must be a list
# Error: rows must be a list of objects
# Error: pk must be a string
```
I pasted those comments into my test file inside the existing list of parameterized tests, then wrote each test by adding a newline beneath a comment and hitting `tab` until Copilot had written the test for me.

It correctly guessed both the error assertion and the desired invalid input for each one!

Here's an animated screenshot:

![In this animation I start typing below the comment that says rows must be a list of objects - Copilot correctly deduces that I neeed an example with a rows item that is a list, and that the expected status code is 400, and that the returned error should match the text in the comment.](https://user-images.githubusercontent.com/9599/201836958-78288b9a-7ee6-4035-bfb3-b37e935cbc5a.gif)

The [finished tests are here](https://github.com/simonw/datasette/blob/187d91d68617ca48e34c1fb0c6722a40f8567d45/tests/test_api_write.py#L548-L722).
