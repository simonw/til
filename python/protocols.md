# Protocols in Python

[Datasette](https://datasette.io/) currently has a few API internals that return `sqlite3.Row` objects. I was thinking about how this might work in the future - if Datasette ever expands beyond SQLite (plugin-provided backends for PostgreSQL and DuckDB for example) I'd want a way to return data from other stores using objects that behave like `sqlite3.Row` but are not exactly that class.

I thought about implementing my own wrapper class for `sqlite3.Row`, but one of its benefits is that it's [written in C](https://github.com/python/cpython/blob/v3.11.4/Modules/_sqlite/row.c) and hence should provide optimal memory usage and performance.

It looks like that's what [typing.Protocol()](https://docs.python.org/3/library/typing.html#typing.Protocol) is for.

Here's some code I put together (with initial assistance from both Claude and ChatGPT) to explore what that would look like:
```python
from typing import Any, Dict, List, Protocol, Union
import sqlite3


class RowProtocol(Protocol):
    def keys(self) -> List[str]:
        ...

    def __getitem__(self, index: Union[int, str]) -> Any:
        ...


class MyRow:
    def __init__(self, data: Dict[str, Any]):
        self.data = data

    def keys(self) -> List[str]:
        return list(self.data.keys())

    def __getitem__(self, index: Union[int, str]) -> Any:
        if isinstance(index, int):
            key = self.keys()[index]
            return self.data.get(key)
        elif isinstance(index, str):
            return self.data.get(index)
        else:
            raise TypeError("Index must be either int or str.")


def get_rows() -> List[RowProtocol]:
    row1 = MyRow({"name": "Milo", "species": "cat"})

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    row2 = conn.execute("select 'Cleo' as name, 'dog' as species").fetchone()

    return [row1, row2]


if __name__ == "__main__":
    rows = get_rows()
    for row in rows:
        # Uncomment this when running mypy:
        # reveal_type(row)
        print(row.keys(), row["name"])
```
This passes a `mypy` check. Running it demonstrates that the `MyRow` and `sqlite3.Row` objects can be treated equivalently.

Uncommenting `reveal_type(row)` causes `mypy` to print out the `RowProtocol` type while it is running.

The thing that surprised me about this at first is that I had expected I would need to "register" the types with the protocol in some way - but it turns out protocols really are just a formalization of Python's duck typing.

Effectively this code is saying "the objects returned by `get_rows()` should only be accessed via their `.keys()` and `__getitem__()` methods".

Which looks like exactly what I would need to implement my own alternative to `sqlite3.Row` in the future in a way that works neatly with Python type checking tools.
