# Using namedtuple for pytest parameterized tests

I'm writing some quite complex [pytest]() parameterized tests this morning, and I was finding it a little bit hard to read the test cases as the number of parameters grew.

Here's a pattern I figured out using Python's `namedtuple` to make the test cases easier to read and edit:

```python
from collections import namedtuple
import pytest


ManageTableTest = namedtuple(
    "ManageTableTest",
    (
        "description",
        "setup_post_data",
        "post_data",
        "expected_acls",
        "should_fail_then_succeed",
        "expected_audit_rows",
    ),
)
@pytest.mark.asyncio
@pytest.mark.parametrize(
    ManageTableTest._fields,
    (
        ManageTableTest(
            description="Group: add insert-row",
            setup_post_data={},
            post_data={"group_permissions_staff_insert-row": "on"},
            expected_acls=[
                {
                    "group_name": "staff",
                    "actor_id": None,
                    "action_name": "insert-row",
                    "database_name": "db",
                    "resource_name": "t",
                }
            ],
            should_fail_then_succeed=[
                dict(
                    actor={"id": "simon", "is_staff": True},
                    action="insert-row",
                    resource=["db", "t"],
                ),
            ],
            expected_audit_rows=[
                {
                    "group_name": "staff",
                    "actor_id": None,
                    "action_name": "insert-row",
                    "database_name": "db",
                    "resource_name": "t",
                    "operation_by": "root",
                    "operation": "added",
                }
            ],
        ),
    )
):
def test_manage_table_permissions(
    description,
    setup_post_data,
    post_data,
    expected_acls,
    should_fail_then_succeed,
    expected_audit_rows,
):
    # Tests go here
```
You can see [a more complete example here](https://github.com/datasette/datasette-acl/blob/ea0e092a33295f95b52c23d3fa21e8dee4fdc5e7/tests/test_acl.py).

There are a couple of tricks here. I'm defining this `namedtuple` with the fields that I know I want to use in the tests:

```python
ManageTableTest = namedtuple(
    "ManageTableTest",
    (
        "description",
        "setup_post_data",
        "post_data",
        "expected_acls",
        "should_fail_then_succeed",
        "expected_audit_rows",
    ),
)
```
I'm doing this purely to be able to use keyword arguments when defining my tests, which are much easier to read than a ordered list of arguments.

The `pytest.mark.parametrize` decorator is usually called with a comma-separated string of field names, which would look like this:

```python
@pytest.mark.parametrize(
    "description,setup_post_data,post_data,expected_acls,should_fail_then_succeed,expected_audit_rows", [
    ManageTableTest(description="...",)
])
def test_manage_table_permissions(...)
```
That's a bit ugly, and you end up duplicating the list of fields. Instead, I reuse the definition from the `namedtuple` like this:
```python
@pytest.mark.parametrize(
    ManageTableTest._fields,
    (
        ManageTableTest(
            description="...",
        )
    )
```
One last trick: that `description=` field isn't actually used by my code. Initially I had a code comment instead.

Then I found myself running `pytest -x --pdb` to drop into a debugger in a failing test but getting confused over which of the parameterized tests I was in. So I added the `description` argument so I can type `description` in the debugger and find out which test case failed.
