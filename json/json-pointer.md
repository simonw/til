# JSON Pointer

I'm [looking at options](https://github.com/simonw/datasette/issues/1875) for representing JSON validation errors in more JSON. The recent [RFC 7807: Problem Details for HTTP APIs](https://datatracker.ietf.org/doc/draft-ietf-httpapi-rfc7807bis/) looks relevant here.

It uses [JSON Pointer](https://www.rfc-editor.org/rfc/rfc6901) to indicate where in a nested JSON object an error occurred. So I need to figure that out.

With the help of GPT-3 I made the following notes:

Given this JSON:
```json
{
   "name": "Bob",
   "inner": {
      "age": 30,
      "ties": ["blue", "black"],
      "1": "one"
   }
}
```
The JSON Pointer to the name is:

    /name

The JSON Pointer to the ties is:

    /inner/ties

The JSON Pointer to "one" is:

    /inner/1

This last one is tricky: how can you tell the difference between an index into an array and the name of a key?

Turns out the answer is to look at whether you are dealing with an object or an array at the time when you are processing the pointer.

Here's [where that is implemented](https://github.com/stefankoegl/python-json-pointer/blob/a95c26fba8ef44af6d16ad6c5b70d7f9c69ae36c/jsonpointer.py#L272-L288) in the [python-json-pointer](https://github.com/stefankoegl/python-json-pointer) library.

(GPT-3 wrote the rest of this.)

## JSON Pointer escape sequences

The JSON Pointer escape sequences are:

- `/` is escaped by `~1`
- `~` is escaped by `~0`

This means that the JSON Pointer `/inner/~0/1` is actually `/inner/~/1`,
which points to the value `"one"` in the example JSON.

[ Simon note: I didn't fully understand this example ]

## JSON Pointer evaluation

To evaluate a JSON Pointer:

1. Split the JSON Pointer on `"/"` to get the parts.
2. Start with the root value (where the pointer was given)
3. For each part:
    1. If the part is `"~1"`, replace it with `"/"`
    2. If the part is `"~0"`, replace it with `"~"`
    3. If the part is `"0"` through `"9"`, take the corresponding element of the current value.
    4. Otherwise, take the value of the field with this name in the current value.
4. The result is the value
