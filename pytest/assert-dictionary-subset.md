# Asserting a dictionary is a subset of another dictionary

My [lazy approach to writing unit tests](https://simonwillison.net/2020/Feb/11/cheating-at-unit-tests-pytest-black/) means that sometimes I want to run an assertion against most (but not all) of a dictionary.

Take for example an API endpoint that returns something like this:

```json
{
    "sqlite_version": "3.27.1",
    "name": "Datasette",
    "columns": ["foo", "bar"]
}
```
I want to efficiently assert against the second two keys, but I don't want to hard-code the SQLite version into my test in case it changes in the future.

Solution:

```python
assert {
    "name": "Datasette",
    "columns": ["foo", "bar"]
}.items() <= api_response.items()
```

The trick here is using `expected.items() <= actual.items()` to assert that one dictionary is a subset of another.

Here's a recent example test that uses this trick: https://github.com/simonw/datasette/blob/40885ef24e32d91502b6b8bbad1c7376f50f2830/tests/test_plugins.py#L414-L446
