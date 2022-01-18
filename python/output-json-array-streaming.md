# Streaming indented output of a JSON array

I wanted to produce the following output from a command-line tool:

```json
[
  {
    "id": 1,
    "name": "Simon"
  },
  {
    "id": 2,
    "name": "Cleo"
  },
  {
    "id": 3,
    "name": "Azi"
  }
]
```
But I wanted to do it from a streaming iterator - without first buffering the entire output in an in-memory Python list and calling `json.dumps()` on it.

Here's the pattern I came up with:

```python
import itertools, json, textwrap

def stream_indented_json(iterator, indent=2):
    # We have to iterate two-at-a-time so we can know if we
    # should output a trailing comma or if we have reached
    # the last item.
    current_iter, next_iter = itertools.tee(iterator, 2)
    next(next_iter, None)
    first = True
    for item, next_item in itertools.zip_longest(current_iter, next_iter):
        is_last = next_item is None
        data = item
        line = "{first}{serialized}{separator}{last}".format(
            first="[\n" if first else "",
            serialized=textwrap.indent(
                json.dumps(data, indent=indent, default=repr), " " * indent
            ),
            separator="," if not is_last else "",
            last="\n]" if is_last else "",
        )
        yield line
        first = False
    if first:
        # We didn't output anything, so yield the empty list
        yield "[]"
```
Example usage:
```python
for line in stream_indented_json(item_iterator):
    click.echo(line)
```
I built this for [s3-credentials issue #48](https://github.com/simonw/s3-credentials/issues/48).
