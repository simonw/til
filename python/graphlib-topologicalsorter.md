# Planning parallel downloads with TopologicalSorter

For [complicated reasons](https://github.com/simonw/datasette/issues/878) I found myself wanting to write Python code to resolve a graph of dependencies and produce a plan for efficiently executing them, in parallel where possible.

I figured out how to do it using [graphlib.TopologicalSorter](https://docs.python.org/3/library/graphlib.html#graphlib.TopologicalSorter), which was added to the Python standard library [in Python 3.9](https://docs.python.org/3/whatsnew/3.9.html#graphlib).

Since I want my code to work on older versions of Python, I was pleased to see that [the graphlib.py module](https://github.com/python/cpython/blob/3.10/Lib/graphlib.py) is standalone and can be easily vendored.

For this example: imagine I know the dependencies of some packages, and I want to fire off some downloads - running them in parallel where possible.

```python
from graphlib import TopologicalSorter

graph = {
    "datasette": {"httpx", "sqlite-utils", "click"},
    "sqlite-utils": {"click", "httpx"}
}

ts = TopologicalSorter(graph)
ts.prepare()
plan = []
while ts.is_active():
    nodes = ts.get_ready()
    plan.append(nodes)
    ts.done(*nodes)

print(plan)
```
This outputs:
```
[('click', 'httpx'), ('sqlite-utils',), ('datasette',)]
```
So the plan would be to download `click` and `httpx` in parallel, then `sqlite-utils`, then `datasette`.

In this usage of the module we're passing the full `graph` as an argument to `TopologicalSorter`. It's also possible to build it up a step at a time like this:

```python
ts = TopologicalSorter()
# add(node, *predecessors)
ts.add("datasette", "httpx", "sqlite-utils", "click")
ts.add("sqlite-utils", "click", "httpx")
ts.prepare()
plan = []
while ts.is_active():
    nodes = ts.get_ready()
    plan.append(nodes)
    ts.done(*nodes)
```
Having called `.prepare()` no further `.add()` calls are allowed.

If you just want the nodes ordered such that none of them come before a dependency you can use `.static_order()`:

```pycon
>>> graph = {
...     "datasette": {"httpx", "sqlite-utils", "click"},
...     "sqlite-utils": {"click", "httpx"}
... }
>>> ts = TopologicalSorter(graph)
>>> list(ts.static_order())
['click', 'httpx', 'sqlite-utils', 'datasette']
```

The `.prepare()` method raises `graphlib.CycleError` if it detects a cycle:

```pycon
>>> TopologicalSorter({"datasette": {"sqlite-utils"}, "sqlite-utils": {"datasette"}}).prepare()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/Users/simon/.pyenv/versions/3.10.0/lib/python3.10/graphlib.py", line 104, in prepare
    raise CycleError(f"nodes are in a cycle", cycle)
graphlib.CycleError: ('nodes are in a cycle', ['datasette', 'sqlite-utils', 'datasette'])
```
