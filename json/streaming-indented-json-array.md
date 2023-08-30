# Streaming output of an indented JSON array

For [paginate-json]() I wanted to implement streaming output of an indented JSON array to my terminal.

The final output should look like this:
```json
[
  {
    "id": 1,
    "name": "One"
  },
  {
    "id": 2,
    "name": "two"
  }
]
```
But I needed this to work for an arbitrarily long sequence of objects, where objects were displayed as the program continued to execute and the indentation and placement of commas was correct despite me not knowing the full length of the final array.

Here's the pattern I came up with:

```python
first = True
for item, last in enumerate_last(iterator()):
    if first:
        print("[")
        first = False
    print(
        textwrap.indent(
            json.dumps(item, indent=2).rstrip() + ("" if last else ","),
            "  "
        )
    )
print("]")
```
Here's how this works:

- Start by outputting a single `[` - the opening square bracket for the array.
- Loop through each object in the iterator. For each one, output a 2-space indented representation of it using `json.dumps()` - and use `textwrap.indent()` to indent that by an additional two spaces.
- Also keep track of if each item is the last object in the sequence. If it isn't the last one, include a trailing comma character.
- At the end, output a closing `]`.

The trickiest part was looping through the objects while keeping track of whether or not each item was the last item. I didn't want to have to load everything into memory first in order to do this.

I got GPT-4 Code Interpreter (now named Advanced Data Analysis, but I don't like that name much) to [write and test this function for me](https://chat.openai.com/share/83c1cac0-0e53-4e24-bebb-1c5437da2f31):

```python
def enumerate_last(iterable):
    it = iter(iterable)
    try:
        last = next(it)
    except StopIteration:
        return
    while True:
        try:
            current = next(it)
            yield last, False
            last = current
        except StopIteration:
            yield last, True
            break
```
This works by creating a new iterator and then advancing it once to fetch the first item from it.

The function then loops, each time fetching the next item and returning the previous one plus a boolean indication of if the next one exists or not.

When it runs out of items, it returns the last one and a `True` to indicate that it has reached the end.

