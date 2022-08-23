# Seeing which functions are unique to a specific SQLite / Datasette instance

In reading [Scraping JSON, HTML, and ZIP Files with Pure SQLite](https://observablehq.com/@asg017/scrape-json-html-zip-with-sqlite) by Alex Garcia I got curious to see a full list of functions he had registered in his [sqlite-extension-examples.fly.dev](https://sqlite-extension-examples.fly.dev) Datasette instance that weren't available in a regular Datasette.

Here's how I figured that out.

## pragma_function_list()

You can list all of the functions available to SQLite using `PRAGMA function_list`.

Datasette doesn't allow non-SELECT queries, but it does allow-list a set of `pragma_x()` functions which you can instead call like this:

```sql
select * from pragma_function_list()
```
[Here's that for latest.datasette.io](https://latest.datasette.io/fixtures?sql=select+*+from+pragma_function_list%28%29) (truncated):

| name                          |   builtin | type   | enc   |   narg |   flags |
|-------------------------------|-----------|--------|-------|--------|---------|
| pow                           |         1 | s      | utf8  |      2 | 2099200 |
| group_concat                  |         1 | w      | utf8  |      1 | 2097152 |
| group_concat                  |         1 | w      | utf8  |      2 | 2097152 |
| json_type                     |         1 | s      | utf8  |      1 |    2048 |
| json_type                     |         1 | s      | utf8  |      2 |    2048 |
| julianday                     |         1 | s      | utf8  |     -1 | 2099200 |

I decided to create a comma-separated list of quoted names. I used this query:

```sql
select "'" || group_concat(name, "', '") || "'" from pragma_function_list()
```
Run [against latest.datasette.io](https://latest.datasette.io/fixtures?sql=select+%22%27%22+||+group_concat(name%2C+%22%27%2C+%27%22)+||+%22%27%22+from+pragma_function_list()) this returned the following:

`'pow', 'group_concat', 'group_concat', 'json_type', 'json_type', 'julianday', 'ntile', 'nullif', 'sqlite_compileoption_get', 'json_valid', 'json_quote', 'json_patch', '->', 'json_array', 'current_timestamp', 'power', 'sqlite_compileoption_used', 'json_remove', 'json_object', 'json_insert', '->>', 'sin', 'sum', 'quote', 'printf', 'likelihood', 'json_replace', 'json_extract', 'last_value', 'rank', 'sign', 'sqrt', 'sinh', 'tan', 'round', 'round', 'rtrim', 'rtrim', 'nth_value', 'tanh', 'random', 'trim', 'trim', 'time', 'radians', 'trunc', 'total', 'substr', 'substr', 'replace', 'upper', 'subtype', 'typeof', 'load_extension', 'load_extension', 'soundex', 'json_group_array', 'avg', 'abs', 'json_group_object', 'json_array_length', 'json_array_length', 'strftime', 'atan', 'asin', 'acos', 'substring', 'substring', 'randomblob', 'unicode', 'percent_rank', 'row_number', 'atanh', 'asinh', 'acosh', 'cos', 'atan2', 'last_insert_rowid', 'sqlite_log', 'unlikely', 'cosh', 'ceil', 'char', 'unixepoch', 'exp', 'count', 'count', 'date', 'ceiling', 'total_changes', 'changes', 'sqlite_version', 'degrees', 'floor', 'coalesce', 'glob', 'zeroblob', 'hex', 'iif', 'sqlite_source_id', 'format', 'datetime', 'cume_dist', 'ln', 'instr', 'json', 'dense_rank', 'log', 'log', 'ifnull', 'current_date', 'current_time', 'lag', 'lag', 'lag', 'mod', 'log2', 'like', 'like', 'max', 'max', 'min', 'min', 'lead', 'lead', 'lead', 'log10', 'lower', 'ltrim', 'ltrim', 'first_value', 'pi', 'length', 'likely', 'json_set', 'escape_fts', 'prepare_connection_args', 'convert_units', 'sleep', 'rtreedepth', 'match', 'snippet', 'fts5_source_id', 'offsets', 'matchinfo', 'matchinfo', 'optimize', 'rtreecheck', 'rtreenode', 'highlight', 'bm25', 'fts3_tokenizer', 'fts3_tokenizer', 'fts5'`

## Comparing via copy-and-paste

To see the functions that were registered for https://sqlite-extension-examples.fly.dev/ but not for https://latest.datasette.io/ I used the above output to construct the following query:

`select name from pragma_function_list() where name not in ('pow', 'group_concat', 'group_concat', 'json_type', 'json_type', 'julianday', 'ntile', 'nullif', 'sqlite_compileoption_get', 'json_valid', 'json_quote', 'json_patch', '->', 'json_array', 'current_timestamp', 'power', 'sqlite_compileoption_used', 'json_remove', 'json_object', 'json_insert', '->>', 'sin', 'sum', 'quote', 'printf', 'likelihood', 'json_replace', 'json_extract', 'last_value', 'rank', 'sign', 'sqrt', 'sinh', 'tan', 'round', 'round', 'rtrim', 'rtrim', 'nth_value', 'tanh', 'random', 'trim', 'trim', 'time', 'radians', 'trunc', 'total', 'substr', 'substr', 'replace', 'upper', 'subtype', 'typeof', 'load_extension', 'load_extension', 'soundex', 'json_group_array', 'avg', 'abs', 'json_group_object', 'json_array_length', 'json_array_length', 'strftime', 'atan', 'asin', 'acos', 'substring', 'substring', 'randomblob', 'unicode', 'percent_rank', 'row_number', 'atanh', 'asinh', 'acosh', 'cos', 'atan2', 'last_insert_rowid', 'sqlite_log', 'unlikely', 'cosh', 'ceil', 'char', 'unixepoch', 'exp', 'count', 'count', 'date', 'ceiling', 'total_changes', 'changes', 'sqlite_version', 'degrees', 'floor', 'coalesce', 'glob', 'zeroblob', 'hex', 'iif', 'sqlite_source_id', 'format', 'datetime', 'cume_dist', 'ln', 'instr', 'json', 'dense_rank', 'log', 'log', 'ifnull', 'current_date', 'current_time', 'lag', 'lag', 'lag', 'mod', 'log2', 'like', 'like', 'max', 'max', 'min', 'min', 'lead', 'lead', 'lead', 'log10', 'lower', 'ltrim', 'ltrim', 'first_value', 'pi', 'length', 'likely', 'json_set', 'escape_fts', 'prepare_connection_args', 'convert_units', 'sleep', 'rtreedepth', 'match', 'snippet', 'fts5_source_id', 'offsets', 'matchinfo', 'matchinfo', 'optimize', 'rtreecheck', 'rtreenode', 'highlight', 'bm25', 'fts3_tokenizer', 'fts3_tokenizer', 'fts5')`

This [returned](https://latest.datasette.io/fixtures?sql=select+%22%27%22+||+group_concat(name%2C+%22%27%2C+%27%22)+||+%22%27%22+from+pragma_function_list()) the following list:

```
http_cookies
http_headers_date
http_headers
http_debug
html_count
html_text
html_text
html_extract
html_group_element_span
html_group_element_div
html_element
http_version
html_escape
html
fts5_rowid
fts5_decode_none
html_unescape
html_trim
fts5_decode
http_headers_get
html_attr_has
fts5_expr_tcl
html_attr_get
fts5_expr
fts5_isalnum
html_version
http_headers_has
fts5_fold
html_valid
html_table
html_debug
html_attribute_get
html_attribute_has
```

