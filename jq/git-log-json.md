# Convert git log output to JSON using jq

I just spent way too long messing around with ChatGPT ([transcript here](https://gist.github.com/simonw/c3b486fa90d7c32a0e8dfb47e151090a)) trying to figure this out. After much iteration, here's a recipe that works (mostly written by me at this point):

```bash
git log --pretty=format:'%H%x00%an <%ae>%x00%ad%x00%s%x00' | \
  jq -R -s '[split("\n")[:-1] | map(split("\u0000")) | .[] | {
    "commit": .[0],
    "author": .[1],
    "date": .[2],
    "message": .[3]
  }]'
```
The output looks like this:
```json
[
  {
    "commit": "3feed1f66e2b746f349ee56970a62246a18bb164",
    "author": "Simon Willison <...@gmail.com>",
    "date": "Wed Mar 22 15:54:35 2023 -0700",
    "message": "Re-applied Black"
  },
  {
    "commit": "d97e82df3c8a3f2e97038d7080167be9bb74a68d",
    "author": "Simon Willison <...@gmail.com>",
    "date": "Wed Mar 22 15:49:39 2023 -0700",
    "message": "?_extra= support and TableView refactor to table_view"
  },
  {
    "commit": "56b0758a5fbf85d01ff80a40c9b028469d7bb65f",
    "author": "Simon Willison <...@gmail.com>",
    "date": "Wed Mar 8 12:52:25 2023 -0800",
    "message": "0.64 release notes, refs #2036"
  },
  {
    "commit": "25fdbe6b27888b7ccf1284c0304a8eb282dbb428",
    "author": "Simon Willison <...@gmail.com>",
    "date": "Wed Mar 8 12:33:23 2023 -0800",
    "message": "use tmpdir instead of isolated_filesystem, refs #2037"
  }
]
```
The challenge here was to get `git log` to output text in an unambiguous, easy to parse format.

    git log --pretty=format:'%H%x00%an <%ae>%x00%ad%x00%s%x00'

This outputs each commit as a single line of text, using null bytes as a delimiter.

Null bytes won't render here, but it looks something like this:

    3feed1f66e2b746f349ee56970a62246a18bb164Simon Willison <...@gmail.com>Wed Mar 22 15:54:35 2023 -0700Re-applied Black

An explanation of those formatting codes (thanks, ChatGPT):

- `%H`: The commit hash.
- `%x00`: A null byte (represented by the hexadecimal value 00) as a separator between the different fields.
- `%an`: The author's name.
- `<%ae>`: The author's email address enclosed in angle brackets.
- `%ad`: The author date in the default format.
- `%s`: The commit message title (without the description).

Then I pipe that through this `jq` program:

```jq
[split("\n")[:-1] | map(split("\u0000")) | .[] | {
  "commit": .[0],
  "author": .[1],
  "date": .[2],
  "message": .[3]
}]
```
The `jq -R -s` means "raw input" (don't expect the input to be JSON) and "slurp", to slurp all the input into memory in one go.

Then I can use `split("\n")` to split on newlines, ignoring the empty line at the end with `[:-1]`.

Each of those lines is run through `map` and then split on `"\u0000"` - the null byte.

Those are gathered into a fresh array with `.[]` and finally converted from an array to an object using that object literal syntax.
