# json_extract() path syntax in SQLite

Several of the [SQLite JSON functions](), such as `json_extract()` and `json_array_length()`, take a path argument. This uses custom syntax along the lines of `$.a[2].b` - but the syntax is not fully documented.

The syntax is similar to that used by MySQL, which is [documented here](https://dev.mysql.com/doc/refman/8.0/en/json.html#json-path-syntax).

Today I figured out the full rules for the path syntax, based on [this forum thread](https://sqlite.org/forum/forumpost/e1d3b6a054) and some dives into the SQLite source code.

## Basic syntax for objects and arrays

Paths must always start with a `$`, which represnts the root of the JSON value.

This can be followed by `.key` or `."key"` to navigate into object keys, and `[0]` to navigate into arrays.

The double quote syntax is useful if your key includes `.` characters.

Given this example document:

```json
{
  "creatures": [
    {
      "name": "Cleo",
      "species": "dog"
    },
    {
      "name": "Azi",
      "species": "chicken",
      "weight.lb": 1.6
    },
  ]
}
```
- `$.creatures` returns the JSON array ([demo](https://latest.datasette.io/_memory?sql=select+json_extract%28%27%7B%0D%0A++++%22creatures%22%3A+%5B%0D%0A++++++++%7B%0D%0A++++++++++++%22name%22%3A+%22Cleo%22%2C%0D%0A++++++++++++%22species%22%3A+%22dog%22%0D%0A++++++++%7D%2C%0D%0A++++++++%7B%0D%0A++++++++++++%22name%22%3A+%22Azi%22%2C%0D%0A++++++++++++%22species%22%3A+%22chicken%22%2C%0D%0A++++++++++++%22weight.lb%22%3A+1.6%0D%0A++++++++%7D%0D%0A++++%5D%0D%0A%7D%27%2C+%3Apath%29&path=%24.creatures))
- `$.creatures[0].name` returns `Cleo` ([demo](https://latest.datasette.io/_memory?sql=select+json_extract%28%27%7B%0D%0A++++%22creatures%22%3A+%5B%0D%0A++++++++%7B%0D%0A++++++++++++%22name%22%3A+%22Cleo%22%2C%0D%0A++++++++++++%22species%22%3A+%22dog%22%0D%0A++++++++%7D%2C%0D%0A++++++++%7B%0D%0A++++++++++++%22name%22%3A+%22Azi%22%2C%0D%0A++++++++++++%22species%22%3A+%22chicken%22%2C%0D%0A++++++++++++%22weight.lb%22%3A+1.6%0D%0A++++++++%7D%0D%0A++++%5D%0D%0A%7D%27%2C+%3Apath%29&path=%24.creatures%5B0%5D.name))
- `$.creatures[1]."weight.lb"` returns `1.6` ([demo](https://latest.datasette.io/_memory?sql=select+json_extract%28%27%7B%0D%0A++++%22creatures%22%3A+%5B%0D%0A++++++++%7B%0D%0A++++++++++++%22name%22%3A+%22Cleo%22%2C%0D%0A++++++++++++%22species%22%3A+%22dog%22%0D%0A++++++++%7D%2C%0D%0A++++++++%7B%0D%0A++++++++++++%22name%22%3A+%22Azi%22%2C%0D%0A++++++++++++%22species%22%3A+%22chicken%22%2C%0D%0A++++++++++++%22weight.lb%22%3A+1.6%0D%0A++++++++%7D%0D%0A++++%5D%0D%0A%7D%27%2C+%3Apath%29&path=%24.creatures%5B1%5D.%22weight.lb%22))

## The mysterious \#

You can also use `#` inside the `[]` array syntax to refer to the length of the array.

This means `$.creatures[#]` (demo) will return `null` - because array indexing is from 0 so using the length as an index returns the item that's just past the end.

But... you can apply a single integer subtraction operation to that `#` - so you can return the name of the last creature in the array using this:

- `$.creatures[#-1].name` returns `Azi` ([demo](https://latest.datasette.io/_memory?sql=select+json_extract%28%27%7B%0D%0A++++%22creatures%22%3A+%5B%0D%0A++++++++%7B%0D%0A++++++++++++%22name%22%3A+%22Cleo%22%2C%0D%0A++++++++++++%22species%22%3A+%22dog%22%0D%0A++++++++%7D%2C%0D%0A++++++++%7B%0D%0A++++++++++++%22name%22%3A+%22Azi%22%2C%0D%0A++++++++++++%22species%22%3A+%22chicken%22%2C%0D%0A++++++++++++%22weight.lb%22%3A+1.6%0D%0A++++++++%7D%0D%0A++++%5D%0D%0A%7D%27%2C+%3Apath%29&path=%24.creatures%5B%23-1%5D.name))

Here's [the commit](https://sqlite.org/src/info/35ed68a651f) that added that custom SQLite extension in 2019.

## Keys containing a "

If your object key contains a `"` character you can't use the `$."..."` syntax to access it - but provided it does not also contain a `.` character you can escape it like this:

`$.has\" quotes in it`

For example ([demo](https://latest.datasette.io/_memory?sql=select+json_extract(%27%7B%0D%0A++++%22has%5C%22+quotes+in+it%22:+%22hello%22%0D%0A%7D%27,+%27$.has%5C%22+quotes+in+it%27)&path=$.has%5C%22+quotes+in+it)):

```sql
select json_extract('{
    "has\" quotes in it": "hello"
}', '$.has\" quotes in it')
```
Outputs `hello`.

## Source code

The latest source code for the JSON module can be found in [ext/misc/json.c](https://www3.sqlite.org/src/file?name=ext/misc/json.c) - in particular the `static JsonNode *jsonLookup(...)
` function.

The unit tests are really useful - those are spread across these six files:

- [test/json1.test](https://www3.sqlite.org/src/file?name=test/json1.test)
- [test/json101.test](https://www3.sqlite.org/src/file?name=test/json101.test)
- [test/json102.test](https://www3.sqlite.org/src/file?name=test/json102.test)
- [test/json103.test](https://www3.sqlite.org/src/file?name=test/json103.test)
- [test/json104.test](https://www3.sqlite.org/src/file?name=test/json104.test)
- [test/json105.test](https://www3.sqlite.org/src/file?name=test/json105.test) - this one has the tests for `[#]` syntax.
