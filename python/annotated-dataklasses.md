# Annotated explanation of David Beazley's dataklasses

David Beazley [on Twitter](https://twitter.com/dabeaz/status/1472742536649351173):

> So, I just published this deliciously evil spin on dataclasses. It's tiny and the resulting classes import about 15-20 faster than dataclasses.  https://github.com/dabeaz/dataklasses

I decided to create a heavily annotated version of [his original code](https://github.com/dabeaz/dataklasses/blob/78d29d40091eb55d2e0196a9eee9d842b5b82835/dataklasses.py) to figure out for myself how it worked.

## What this code does

It takes this:
```python
@dataklass
class Coordinates:
    x: int
    y: int
```
And turns it into this:
```python
class Coordinates:
    __match_args__ = {'x': <class 'int'>, 'y': <class 'int'>}

    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return f"Coordinates({self.x!r}, {self.y!r})"

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return (self,x, self.y,) == (other.x, other.y,)
        else:
            return NotImplemented
```
## The key trick: code generation

The key to understanding how the code works is to understand that it is using code generation. David introspects out the annotated class properties, from the class itself and any superclasses, and then counts how many they are. He then generates methods that look like this:

```python
def __init__(self, _0, _1):
    self._0 = _0
    self._1 = _1
```
Then uses the `func.__code__.replace(co_names=repl_co_names, co_varnames=repl_co_varnames)` method to rename those `_0` and `_1` variables back to `x` and `y`.

I don't yet understand why he does this as opposed to generating the code using `x` and `y` directly. I'll update this with an explanation once I find one!

Update: Jacob Kaplan-Moss [explains it here](https://twitter.com/jacobian/status/1472789373552762884)!

> That's the absolutely _wild_ trick at the heart of this, and what makes it fast:
>
> the bytecode for `__init__(self, x, y)` is exactly the same as the bytecode for `__init__(self, foo, bar)`!
>
> So that means Dave can cache the generated code for for "any `__init__` function with two args" and then _re-use the exact same code_ for any later 2-arity `__init__`s!

## My annotated copy

First, including the copyright message as required by the copyright message:
```python
# dataklasses.py
#
#     https://github.com/dabeaz/dataklasses
#
# Author: David Beazley (@dabeaz).
#         http://www.dabeaz.com
#
# Copyright (C) 2021-2022.
#
# Permission is granted to use, copy, and modify this code in any
# manner as long as this copyright message and disclaimer remain in
# the source code.  There is no warranty.  Try to use the code for the
# greater good.
```
My annotations start here (I also ran it through [Black](https://black.vercel.app/)).
```python
__all__ = ["dataklass"]
# This ensures "from dataklasses import *" will only import the dataklass symbol

from functools import lru_cache, reduce

# This decorator takes a function that returns Python source code and compiles
# that into a Python function. So if func(fields) returns the following string:
#
# def __init__(self, a):
#     self.a = a
#
# The return value will be that compiled function. With some enhancements.
def codegen(func):
    # This caches the result so if you pass the same numfields it won't have to
    # carry out the same work twice.
    #
    # This is the key performance optimization for this code - it means that
    # the same generated code can be reused for any class that has the same
    # number of arguments!
    @lru_cache
    def make_func_code(numfields):
        # numfields in len(fields)
        names = [f"_{n}" for n in range(numfields)]
        # names is now ["_0", "_1", "_2"] depending on numfields
        #
        # We call func() with that list of names and exec() the
        # returned source code. The third argument to exec() is
        # locals() - it's a dictionary that the exec() function
        # will populate with any new symbols.
        #
        # We use the d:={} walrus operator here so that we can
        # refer to that dictionary by the name d in a moment.
        exec(func(names), globals(), d := {})
        # d.popitem() returns the first (key, value) pair in
        # the dictionary. We know that the locals() dictionary
        # is only going to have a single symbol in it, because
        # we now that the code returned by func(names) only
        # defines a single function. So this returns the value
        # from the first item in locals(), the function object
        return d.popitem()[1]

    # This decorate() is the return value from the decorator,
    # which means that the following code:
    #
    # @codegen
    # def make__init__(fields):
    #     # ...
    # Turns make__init__ into the function defined by decorate()
    def decorate(fields):
        # As shown above, this uses exec() to compile and return
        # a function body created using the generated source code
        func = make_func_code(len(fields))

        # But remember: because we cache and reuse method bodies, this has
        # ugly _0, _1 parameters and variables that we want to make nicer.

        # co_names: tuple of names other than arguments and function locals
        co_names = func.__code__.co_names
        # For the Coordinates example, co_names = ("_0", "_1")

        # co_varnames: tuple of names of arguments and local variables
        co_varnames = func.__code__.co_varnames
        # For the Coordinates example, co_varnames = ("self", "_0", "_1")

        # We are about to replace co_names and co_varnames with modified
        # versions - so we need to create two replacement tuples for them.
        #
        # start := co_names.index("_0") uses the walrus operator to both
        # figure out the 0-based index of the _0 symbol and assign it to s
        #
        # We use (*a, *b, *c) to create a new tuple that is the result of
        # combining those three input tuples.
        repl_co_names = (
            # Slice everything in co_names up to that first _0 symbol
            *co_names[: (start := co_names.index("_0"))],
            # Then insert the fields, which are the annotated class properties
            *fields,
            # Now everything in co_names following 
            *co_names[start + len(fields) :],
        )
        # For Coordinates this is now ("x", "y")

        repl_co_varnames = (
            # We only modify co_varnames if _0 is one of them, otherwise
            # we leave them unchanged.
            (
                *co_varnames[: (start := co_varnames.index("_0"))],
                *fields,
                *co_varnames[start + len(fields) :],
            )
            if "_0" in co_varnames
            else co_varnames
        )
        # For Coordinates this is now ("self", "x", "y")

        # type(func) returns a Python internal object called "function"
        # which is callable and has this function signature:
        #
        # function(code, globals, name=None, argdefs=None, closure=None)
        #
        # It creates a brand new function object
        return type(func)(
            # func.__code__.replace docstring says:
            # "Return a copy of the code object with new values for the specified fields"
            # So we are rewriting the co_names and co_varnames here
            func.__code__.replace(co_names=repl_co_names, co_varnames=repl_co_varnames),
            func.__globals__,
        )

    return decorate


def all_hints(cls):
    # This introspects the class to find all of the annotated class members
    # In Coordinates case this returns {'x': <class 'int'>, 'y': <class 'int'>}
    #
    # The "x" to that lambda starts out as that {} empty dictionary and each time
    # is the dictionary with new stuff added to it.
    #
    # reversed(Coordinates.__mro__) loops through every superclass of the current
    # class, starting at "object".
    #
    # So the lambda is called against each superclass in turn, and each time it
    # reads the __annotations__ field, if one is available.
    #
    # Coordinates.__annotations__ returns {'x': int, 'y': int}
    #
    # dict1 | dict2 in Python returns a new dict that combines the previous two
    #
    # So this function returns a combined dictionary of the __annotations__ from
    # every class in the superclass hierarchy.
    return reduce(
        lambda x, y: x | getattr(y, "__annotations__", {}), reversed(cls.__mro__), {}
    )


# Next are the functions that generate the different methods. Remember they get passed
# fields which is {'x': <class 'int'>, 'y': <class 'int'>}
@codegen
def make__init__(fields):
    # Calling ",".join(dict) joins just the keys of that dictionary
    code = "def __init__(self, " + ",".join(fields) + "):\n"
    # So here we have:
    #    def __init__(self, x, y):
    return code + "\n".join(f" self.{name} = {name}\n" for name in fields)
    # This adds on:
    #   self.x = x
    #   self.y = y


@codegen
def make__repr__(fields):
    return (
        "def __repr__(self):\n"
        # type(self).__name__ gives us the class name: "Coordinates"
        ' return f"{type(self).__name__}('
        # This gives us {self.x!r}, {self.y!r} which in an f-string
        # gives us the __repr__() version of those object properties
        + ", ".join("{self." + name + "!r}" for name in fields)
        + ')"\n'
    )
    # So this generates:
    # def __repr__(self):
    #  return f"Coordinates({self.x!r}, {self.y!r})" 


@codegen
def make__eq__(fields):
    selfvals = ",".join(f"self.{name}" for name in fields)
    othervals = ",".join(f"other.{name}" for name in fields)
    return (
        "def __eq__(self, other):\n"
        "  if self.__class__ is other.__class__:\n"
        f"    return ({selfvals},) == ({othervals},)\n"
        "  else:\n"
        "    return NotImplemented\n"
    )
    # This generates:
    # def __eq__(self, other):
    #   if self.__class__ is other.__class__:
    #     return (self,x, self.y,) == (other.x, other.y)
    #   else:
    #     return NotImplemented


@codegen
def make__iter__(fields):
    return "def __iter__(self):\n" + "\n".join(
        f"   yield self.{name}" for name in fields
    )


@codegen
def make__hash__(fields):
    self_tuple = "(" + ",".join(f"self.{name}" for name in fields) + ",)"
    return "def __hash__(self):\n" f"    return hash({self_tuple})\n"


def dataklass(cls):
    fields = all_hints(cls)
    # fields is now {'x': <class 'int'>, 'y': <class 'int'>}
    clsdict = vars(cls)
    # clsdict looks like this:
    # {'__module__': '__main__',
    #  '__annotations__': {'x': <class 'int'>, 'y': <class 'int'>},
    #  '__dict__': <attribute '__dict__' of 'Coordinates' objects>,
    #  '__weakref__': <attribute '__weakref__' of 'Coordinates' objects>,
    #  '__doc__': None}
    #
    # The purpose of this function is mainly to add __init__ and
    # __repr__ and __eq__ methods, but only if they are not yet defined
    if not "__init__" in clsdict:
        cls.__init__ = make__init__(fields)
    if not "__repr__" in clsdict:
        cls.__repr__ = make__repr__(fields)
    if not "__eq__" in clsdict:
        cls.__eq__ = make__eq__(fields)
    # Not sure why these are commented out right now:
    # if not '__iter__' in clsdict:  cls.__iter__ = make__iter__(fields)
    # if not '__hash__' in clsdict:  cls.__hash__ = make__hash__(fields)
    cls.__match_args__ = fields
    # This sets __match_args__ to {'x': <class 'int'>, 'y': <class 'int'>}
    # Usually __match_args__ is expected to be a tuple like ("x", "y")
    # but presumably this still works with a dictionary because it is used
    # for "name in __match_args__" style lookups.
    #
    # __match_args__ is a property used by Python structural typing:
    # https://www.python.org/dev/peps/pep-0622/#special-attribute-match-args
    return cls


# Example use
if __name__ == "__main__":

    @dataklass
    class Coordinates:
        x: int
        y: int
```
