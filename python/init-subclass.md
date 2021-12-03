# \_\_init_subclass\_\_

David Beazley [on Twitter](https://twitter.com/dabeaz/status/1466731368956809219) said:

> I think 95% of the problems once solved by a metaclass can be solved by `__init_subclass__` instead

This inspired me to finally learn how to use it! I used [my asyncinject project](https://github.com/simonw/asyncinject/issues/2) as an experimental playground.

The `__init_subclass__` class method is called when the class itself is being constructed. It gets passed the `cls` and can make modifications to it.

Here's the pattern I used:

```python
class AsyncInject:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Decorate any items that are 'async def' methods
        cls._registry = {}
        inject_all = getattr(cls, "_inject_all", False)
        for name in dir(cls):
            value = getattr(cls, name)
            if inspect.iscoroutinefunction(value) and (
                inject_all or getattr(value, "_inject", None)
            ):
                setattr(cls, name, _make_method(value))
                cls._registry[name] = getattr(cls, name)
        # Gather graph for later dependency resolution
        graph = {
            key: {
                p
                for p in inspect.signature(method).parameters.keys()
                if p != "self" and not p.startswith("_")
            }
            for key, method in cls._registry.items()
        }
        cls._graph = graph
```
As you can see, it's using `getattr()` and `setattr()` against the `cls` object to make modifications to the class - in this case it's running a decorator against various methods and adding two new class properties, `_registry` and `_graph`.

The `**kwargs` thing there is interesting: you can define keyword arguments and use them when you subclass, like this:

```python
class MySubClass(AsyncInject, inject_all=True):
    ...
```
This doesn't work with my above example, but I could change it to start like this instead:
```python
class AsyncInject:
    def __init_subclass__(cls, inject_all=False, **kwargs):
        super().__init_subclass__(**kwargs)
        # Decorate any items that are 'async def' methods
        cls._registry = {}
        for name in dir(cls):
            value = getattr(cls, name)
            if inspect.iscoroutinefunction(value) and (
                inject_all or getattr(value, "_inject", None)
            ):
                setattr(cls, name, _make_method(value))
                cls._registry[name] = getattr(cls, name)
```
## Further reading


- [Use \_\_init_subclass\_\_ hook to validate subclasses](https://github.com/rednafi/notes/blob/master/notes/python/use_init_subclass_hook_to_validate_subclasses.md) [via Redowan Delowar](https://twitter.com/rednafi/status/1466833693993930755)
- [PEP 487 -- Simpler customisation of class creation](https://www.python.org/dev/peps/pep-0487/)
