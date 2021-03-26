# Introspecting Python function parameters

For https://github.com/simonw/datasette/issues/581 I want to be able to inspect a Python function to determine which named parameters it accepts and send only those arguments.

Python 3.3 added [an inspect.signature() function](https://docs.python.org/3/library/inspect.html#introspecting-callables-with-the-signature-object) that can be used for this.

Here's a function I wrote to take advantage of that and solve my problem:

```python
def call_with_supported_arguments(fn, **kwargs):
    parameters = inspect.signature(fn).parameters.keys()
    call_with = []
    for parameter in parameters:
        if parameter not in kwargs:
            raise TypeError("{} requires parameters {}".format(fn, tuple(parameters)))
        call_with.append(kwargs[parameter])
    return fn(*call_with)
```

And here's an illustrative unit test:

```python
def test_call_with_supported_arguments():
    def foo(a, b):
        return "{}+{}".format(a, b)

    assert "1+2" == utils.call_with_supported_arguments(foo, a=1, b=2)
    assert "1+2" == utils.call_with_supported_arguments(foo, a=1, b=2, c=3)

    with pytest.raises(TypeError):
        utils.call_with_supported_arguments(foo, a=1)
```
