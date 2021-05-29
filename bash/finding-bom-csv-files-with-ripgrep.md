# Finding CSV files that start with a BOM using ripgrep

For [sqlite-utils issue 250](https://github.com/simonw/sqlite-utils/issues/250) I needed to locate some test CSV files that start with a UTF-8 BOM.

Here's how I did that using [ripgrep](https://github.com/BurntSushi/ripgrep):
```
$ rg --multiline --encoding none '^(?-u:\xEF\xBB\xBF)' --glob '*.csv' .
```
The `--multiline` option means the search spans multiple lines - I only want to match entire files that begin with my search term, so this means that `^` will match the start of the file, not the start of individual lines.

`--encoding none` runs the search against the raw bytes of the file, disabling ripgrep's default BOM detection.

`--glob '*.csv'` causes ripgrep to search only CSV files.

The regular expression itself looks like this:

    ^(?-u:\xEF\xBB\xBF)

This is [rust regex](https://docs.rs/regex/1.5.4/regex/#syntax) syntax.

`(?-u:` means "turn OFF the `u` flag for the duration of this block" - the `u` flag, which is on by default, causes the Rust regex engine to interpret input as unicode. So within the rest of that `(...)` block we can use escaped byte sequences.

Finally, `\xEF\xBB\xBF` is the byte sequence for the UTF-8 BOM itself.
