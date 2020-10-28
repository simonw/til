# Decorators with optional arguments

[sqlite-utils](https://sqlite-utils.readthedocs.io/) provides [a decorator](https://sqlite-utils.readthedocs.io/en/stable/python-api.html#registering-custom-sql-functions) for registering custom Python functions that looks like this:

```python
from sqlite_utils import Database

db = Database(memory=True)

@db.register_function
def reverse_string(s):
    return "".join(reversed(list(s)))
```

I wanted to add an [optional deterministic=True parameter](https://github.com/simonw/sqlite-utils/issues/191) to the decorator.

Problem: the decorator currently does not take any arguments. But I wanted this to work as well:

```python
@db.register_function(deterministic=True)
def reverse_string(s):
    return "".join(reversed(list(s)))
```

I don't want to break backwards compatibility with existing code.

First lesson: any time you are designing a decorator that might accept arguments in the future, design it to work like this!

```python
@db.register_function()
def reverse_string(s):
    return "".join(reversed(list(s)))
```

Since I hadn't done that, I needed an alternative pattern that could differentiate between the two ways in which the decorator might be called. I ended up going with this:
```python
    def register_function(self, fn=None, deterministic=None):
        def register(fn):
            name = fn.__name__
            arity = len(inspect.signature(fn).parameters)
            kwargs = {}
            if deterministic and sys.version_info >= (3, 8):
                kwargs["deterministic"] = True
            self.conn.create_function(name, arity, fn, **kwargs)
            return fn

        if fn is None:
            return register
        else:
            register(fn)
```
