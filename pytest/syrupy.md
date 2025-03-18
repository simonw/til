# Snapshot testing with Syrupy

I'm a big fan of snapshot testing - writing tests where you compare the output of some function to a previously saved version, and can re-generate that version from scratch any time something changes.

I usually do this by hand - I run `pytest -x --pdb` to stop at the first failing test and drop into a debugger, then copy out the representation of the generated value and copy it into the test. I wrote about how I use this pattern a few years ago in [How to cheat at unit tests with pytest and Black](https://simonwillison.net/2020/Feb/11/cheating-at-unit-tests-pytest-black/).

Today I learned how to do the same thing with the [Syrupy](https://github.com/tophat/syrupy) plugin for [pytest](https://docs.pytest.org/). I think I'll be using this for many of my future projects.

## Some initial tests

I created a `tests/test_stuff.py` file with the following contents:

```python
def test_one(snapshot):
    assert "hello" == snapshot


def test_two(snapshot):
    assert snapshot == {"foo": [1, 2, 3], "bar": {"baz": "qux"}}
```
Then I installed both `pytest` and `syrupy`:

```bash
pip install pytest syrupy
```
Now in my parent folder I can run this:
```bash
pytest
```
And the tests fail:
```
tests/test_stuff.py FF                                                              [100%]

======================================== FAILURES =========================================
________________________________________ test_one _________________________________________

snapshot = SnapshotAssertion(name='snapshot', num_executions=1)

    def test_one(snapshot):
>       assert "hello" == snapshot
E       AssertionError: assert [+ received] == [- snapshot]
E         Snapshot 'test_one' does not exist!
E         + 'hello'

tests/test_stuff.py:2: AssertionError
________________________________________ test_two _________________________________________

snapshot = SnapshotAssertion(name='snapshot', num_executions=1)

    def test_two(snapshot):
>       assert snapshot == {"foo": [1, 2, 3], "bar": {"baz": "qux"}}
E       AssertionError: assert [- snapshot] == [+ received]
E         Snapshot 'test_two' does not exist!
E         + dict({
E         +   'bar': 
E         
E         ...Full output truncated (9 lines hidden), use '-vv' to show

tests/test_stuff.py:5: AssertionError
--------------------------------- snapshot report summary ---------------------------------
2 snapshots failed.
================================= short test summary info =================================
FAILED tests/test_stuff.py::test_one - AssertionError: assert [+ received] == [- snapshot]
FAILED tests/test_stuff.py::test_two - AssertionError: assert [- snapshot] == [+ received]
==================================== 2 failed in 0.05s ====================================
```
The snapshots don't exist yet. But I can create them automatically by running this:
```bash
pytest --snapshot-update
```
Which outputs passing tests along with:
```
--------------------------------- snapshot report summary ---------------------------------
2 snapshots generated.
==================================== 2 passed in 0.01s ====================================
```
And sure enough, there's now a new folder called `tests/__snapshots__` with a file called `test_stuff.ambr` which contains this:
```
# serializer version: 1
# name: test_one
  'hello'
# ---
# name: test_two
  dict({
    'bar': dict({
      'baz': 'qux',
    }),
    'foo': list([
      1,
      2,
      3,
    ]),
  })
# ---
```
Running `pytest` again passes, because the snapshots exist and continue to match the test output.

The serialized snapshot format is designed to be checked into Git. It's pleasantly readable - I can review that and see what it's testing, and I could even update it by hand - though I'll much more likely use the `--snapshot-update` flag and then eyeball the differences.

## Adding a dataclass

My snapshots so far are pretty simple - a string and a nested dictionary. I decided to add a dataclass to my code and see what that looks like:

```python
import dataclasses


@dataclasses.dataclass
class Foo:
    bar: int
    baz: str


def test_one(snapshot):
    assert "hello" == snapshot


def test_two(snapshot):
    assert snapshot == {"foo": [1, 2, 3], "bar": {"baz": "qux"}}


def test_three(snapshot):
    assert Foo(1, "hello") == snapshot
```
Running `pytest` again failed. `pytest --snapshot-update` passed and updated my snapshot file, adding this to it:
```
# name: test_three
  Foo(bar=1, baz='hello')
```
OK, neat - it looks like it's using the Dataclass's `__repr__` method to serialize the object.

I tried it with a custom non-dataclass object... and it worked too!

```python
class WeirdClass:
    def __init__(self, foo, bar):
        self.foo = foo
        self.bar = bar

def test_four(snapshot):
    assert WeirdClass(1, 2) == snapshot
```
Serialized to:
```
# name: test_four
  WeirdClass(
    bar=2,
    foo=1,
  )
```

I wasn't expecting this to work. The Syrupy documentation says:

> The default serializer supports all python built-in types and provides a sensible default for custom objects.

It looks like there are a bunch of [more advanced ways](https://syrupy-project.github.io/syrupy/#representation) to customize objects to make them work well with Syrupy, but I haven't dived into those yet.

First impressions are that this looks like exactly the snapshot tool I've been waiting for.
