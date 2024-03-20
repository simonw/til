# SQLite pragma_function_list()

The SQLite `pragma_function_list()` table-valued function returns a list of functions that have been registered with SQLite, including functions that were added by extensions.

Here's how to interpret its output.

First, an example:

```sql
select * from pragma_function_list() order by random()
```
I'm using `order by random()` here just to mix things up a bit. Here are the first five results:

| name | builtin | type | enc | narg | flags |
| --- | --- | --- | --- | --- | --- |
| likely | 1 | s | utf8 | 1 | 2099200 |
| json_extract | 1 | s | utf8 | -1 | 2048 |
| ceiling | 1 | s | utf8 | 1 | 2099200 |
| ulid_bytes | 0 | s | utf8 | 1 | 0 |
| row_number | 1 | w | utf8 | 0 | 2097152 |

- `name` is the name of the function
- `builtin` shows if the function is built-in to SQLite or was added by an extension
- `type` tells you what kind of function it is - the options are `s` for scalar, `w` for window and `a` for aggregate.
- `enc` I'm not sure about. It's always `utf8` from what I've seen.
- `narg` is the arity of the function: the number of arguments it takes. `-1` means an unlimited number of arguments.
- `flags` is more complicated, see below

In this example `ulid_bytes` is a function added because I loaded the [sqlite-ulid](https://github.com/asg017/sqlite-ulid) extension.

I hadn't realized that `json_extract()` could take unlimited arguments - I thought it just took a value and a path. From the above I learned that this works:
```sql
select json_extract('{"foo": "bar", "bar": "baz"}', '$.foo', '$.bar') as bits
```
This [returns](https://latest.datasette.io/_memory?sql=select+json_extract%28%27%7B%22foo%22%3A+%22bar%22%2C+%22bar%22%3A+%22baz%22%7D%27%2C+%27%24.foo%27%2C+%27%24.bar%27%29+as+bits) a JSON array corresponding to each argument past the first one:

```json
["bar", "baz"]
```
## Interpreting those flags

I found [this forum post](https://sqlite.org/forum/forumpost/48b468b7e4ec9f6c) by D. Richard Hipp explaining how the flags work:

> The flags column is an internal implementation detail and is subject to change. But a few of the bits are fixed. From `sqlite3.h`:
>
> ```
> #define SQLITE_DETERMINISTIC    0x000000800
> #define SQLITE_DIRECTONLY       0x000080000
> #define SQLITE_SUBTYPE          0x000100000
> #define SQLITE_INNOCUOUS        0x000200000
> ```

(I couldn't find these lines in the source code when I looked for them just now.)

But going by that forum post, the following query helps me understand what those flags mean:

```sql
select
  name,
  narg,
  flags,
  type,
  flags & 0x000000800 != 0 as deterministic,
  flags & 0x000080000 != 0 as directonly,
  flags & 0x000100000 != 0 as subtype,
  flags & 0x000200000 != 0 as innocuous
from
  pragma_function_list()
```
[Run against a Datasette instance](https://latest.datasette.io/_memory?sql=select%0D%0A++name%2C%0D%0A++narg%2C%0D%0A++flags%2C%0D%0A++type%2C%0D%0A++flags+%26+0x000000800+%21%3D+0+as+deterministic%2C%0D%0A++flags+%26+0x000080000+%21%3D+0+as+directonly%2C%0D%0A++flags+%26+0x000100000+%21%3D+0+as+subtype%2C%0D%0A++flags+%26+0x000200000+%21%3D+0+as+innocuous%0D%0Afrom%0D%0A++pragma_function_list%28%29) returns the following data (truncated to the highlights):

| name | narg | flags | type | deterministic | directonly | subtype | innocuous |
| --- | --- | --- | --- | --- | --- | --- | --- |
| group_concat | 1 | 2097152 | w | 0 | 0 | 0 | 1 |
| group_concat | 2 | 2097152 | w | 0 | 0 | 0 | 1 |
| julianday | -1 | 2099200 | s | 1 | 0 | 0 | 1 |
| load_extension | 1 | 524288 | s | 0 | 1 | 0 | 0 |
| load_extension | 2 | 524288 | s | 0 | 1 | 0 | 0 |
| fts3_tokenizer | 2 | 524288 | s | 0 | 1 | 0 | 0 |
| fts3_tokenizer | 1 | 524288 | s | 0 | 1 | 0 | 0 |

Here's the official SQLite documentation for those [function flags](https://www.sqlite.org/c3ref/c_deterministic.html).

- `deterministic` means that the function is guaranteed to return the same result for the same input, which is a useful hint that the SQL query executor can reuse those values without re-calculating them every time.
- `directonly` means that the function can only be called from "top-level SQL", not from triggers, views or things like generated columns or check constraints.
- `innocuous` means that the function is "unlikely to cause problems even if misused" - crucially, it means the function has no side effects.
- `subtype` looks like it's a window function concern - though I haven't yet found an example of a function that uses it. The documentation says "Specifying this flag makes no difference for scalar or aggregate user functions. However, if it is not specified for a user-defined window function, then any sub-types belonging to arguments passed to the window function may be discarded before the window function is called (i.e. `sqlite3_value_subtype()` will always return 0)." I don't understand the implications of this at all.

## As a SQL view to support facets

I decided it would be useful to be able to browse these using facets. I came up with [the following SQL view](https://gist.github.com/simonw/c6fa2d722e7599f3874f27cb19fc8fe4):

```sql
create view functions as
select *,
  case when flags & 0x800 != 0 then '1' else '0' end as 'deterministic',
  case when flags & 0x000100000 != 0 then '1' else '0' end as 'subtype',
  case when flags & 0x000200000 != 0 then '1' else '0' end as 'innocuous',
  case when flags & 0x000080000 != 0 then '1' else '0' end as 'directonly'
from pragma_function_list();
```
The `case` statements are necessary because Datasette doesn't currently facet views correctly if they return integer values.

Since I saved this to a Gist I can open it in Datasette Lite like this:

https://lite.datasette.io/?sql=https://gist.github.com/simonw/c6fa2d722e7599f3874f27cb19fc8fe4#/data/functions?_facet=deterministic&_facet=subtype&_facet=innocuous&_facet=directonly

![Functions shown in Datasette Lite with facets for deterministic, subtype, innocuous and directonly](https://github.com/simonw/til/assets/9599/ef3d8238-7f45-4650-af5d-87fa8681532a)
