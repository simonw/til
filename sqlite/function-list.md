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

This [returned]([https://latest.datasette.io/fixtures?sql=select+%22%27%22+||+group_concat(name%2C+%22%27%2C+%27%22)+||+%22%27%22+from+pragma_function_list()](https://sqlite-extension-examples.fly.dev/data?sql=select+name+from+pragma_function_list%28%29+where+name+not+in+%28%27pow%27%2C+%27group_concat%27%2C+%27group_concat%27%2C+%27json_type%27%2C+%27json_type%27%2C+%27julianday%27%2C+%27ntile%27%2C+%27nullif%27%2C+%27sqlite_compileoption_get%27%2C+%27json_valid%27%2C+%27json_quote%27%2C+%27json_patch%27%2C+%27-%3E%27%2C+%27json_array%27%2C+%27current_timestamp%27%2C+%27power%27%2C+%27sqlite_compileoption_used%27%2C+%27json_remove%27%2C+%27json_object%27%2C+%27json_insert%27%2C+%27-%3E%3E%27%2C+%27sin%27%2C+%27sum%27%2C+%27quote%27%2C+%27printf%27%2C+%27likelihood%27%2C+%27json_replace%27%2C+%27json_extract%27%2C+%27last_value%27%2C+%27rank%27%2C+%27sign%27%2C+%27sqrt%27%2C+%27sinh%27%2C+%27tan%27%2C+%27round%27%2C+%27round%27%2C+%27rtrim%27%2C+%27rtrim%27%2C+%27nth_value%27%2C+%27tanh%27%2C+%27random%27%2C+%27trim%27%2C+%27trim%27%2C+%27time%27%2C+%27radians%27%2C+%27trunc%27%2C+%27total%27%2C+%27substr%27%2C+%27substr%27%2C+%27replace%27%2C+%27upper%27%2C+%27subtype%27%2C+%27typeof%27%2C+%27load_extension%27%2C+%27load_extension%27%2C+%27soundex%27%2C+%27json_group_array%27%2C+%27avg%27%2C+%27abs%27%2C+%27json_group_object%27%2C+%27json_array_length%27%2C+%27json_array_length%27%2C+%27strftime%27%2C+%27atan%27%2C+%27asin%27%2C+%27acos%27%2C+%27substring%27%2C+%27substring%27%2C+%27randomblob%27%2C+%27unicode%27%2C+%27percent_rank%27%2C+%27row_number%27%2C+%27atanh%27%2C+%27asinh%27%2C+%27acosh%27%2C+%27cos%27%2C+%27atan2%27%2C+%27last_insert_rowid%27%2C+%27sqlite_log%27%2C+%27unlikely%27%2C+%27cosh%27%2C+%27ceil%27%2C+%27char%27%2C+%27unixepoch%27%2C+%27exp%27%2C+%27count%27%2C+%27count%27%2C+%27date%27%2C+%27ceiling%27%2C+%27total_changes%27%2C+%27changes%27%2C+%27sqlite_version%27%2C+%27degrees%27%2C+%27floor%27%2C+%27coalesce%27%2C+%27glob%27%2C+%27zeroblob%27%2C+%27hex%27%2C+%27iif%27%2C+%27sqlite_source_id%27%2C+%27format%27%2C+%27datetime%27%2C+%27cume_dist%27%2C+%27ln%27%2C+%27instr%27%2C+%27json%27%2C+%27dense_rank%27%2C+%27log%27%2C+%27log%27%2C+%27ifnull%27%2C+%27current_date%27%2C+%27current_time%27%2C+%27lag%27%2C+%27lag%27%2C+%27lag%27%2C+%27mod%27%2C+%27log2%27%2C+%27like%27%2C+%27like%27%2C+%27max%27%2C+%27max%27%2C+%27min%27%2C+%27min%27%2C+%27lead%27%2C+%27lead%27%2C+%27lead%27%2C+%27log10%27%2C+%27lower%27%2C+%27ltrim%27%2C+%27ltrim%27%2C+%27first_value%27%2C+%27pi%27%2C+%27length%27%2C+%27likely%27%2C+%27json_set%27%2C+%27escape_fts%27%2C+%27prepare_connection_args%27%2C+%27convert_units%27%2C+%27sleep%27%2C+%27rtreedepth%27%2C+%27match%27%2C+%27snippet%27%2C+%27fts5_source_id%27%2C+%27offsets%27%2C+%27matchinfo%27%2C+%27matchinfo%27%2C+%27optimize%27%2C+%27rtreecheck%27%2C+%27rtreenode%27%2C+%27highlight%27%2C+%27bm25%27%2C+%27fts3_tokenizer%27%2C+%27fts3_tokenizer%27%2C+%27fts5%27%29)) the following list:

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

## A better solution using json_group_array() and json_each()

[Alex pointed out](https://twitter.com/agarcia_me/status/1562462457976590336) an alternative solution using SQLite's JSON functions, which is actually better because it avoids any risk of commas or quotation marks in the values breaking the resulting string.

```sql
select json_group_array(distinct name)
from pragma_function_list()
```
[Try that against latest.datasette.io](https://latest.datasette.io/_memory?sql=select+json_group_array%28distinct+name%29%0D%0Afrom+pragma_function_list%28%29)

Output:

`["pow","group_concat","json_type","julianday","ntile","nullif","sqlite_compileoption_get","json_valid","json_quote","json_patch","->","json_array","current_timestamp","power","sqlite_compileoption_used","json_remove","json_object","json_insert","->>","sin","sum","quote","printf","likelihood","json_replace","json_extract","last_value","rank","sign","sqrt","sinh","tan","round","rtrim","nth_value","tanh","random","trim","time","radians","trunc","total","substr","replace","upper","subtype","typeof","load_extension","soundex","json_group_array","avg","abs","json_group_object","json_array_length","strftime","atan","asin","acos","substring","randomblob","unicode","percent_rank","row_number","atanh","asinh","acosh","cos","atan2","last_insert_rowid","sqlite_log","unlikely","cosh","ceil","char","unixepoch","exp","count","date","ceiling","total_changes","changes","sqlite_version","degrees","floor","coalesce","glob","zeroblob","hex","iif","sqlite_source_id","format","datetime","cume_dist","ln","instr","json","dense_rank","log","ifnull","current_date","current_time","lag","mod","log2","like","max","min","lead","log10","lower","ltrim","first_value","pi","length","likely","json_set","escape_fts","prepare_connection_args","convert_units","sleep","rtreedepth","match","snippet","fts5_source_id","offsets","matchinfo","optimize","rtreecheck","rtreenode","highlight","bm25","fts3_tokenizer","fts5"]`

Then use this query and run it on the other instance:
```sql
select
  name
from
  pragma_function_list()
where
  name not in (
    select
      value
    from
      json_each(:json)
  )
```
A neat thing about this alternative is you can pass the single JSON string as a named parameter, rather than needing to paste the list of IN terms into the SQL query itself.

[Try that against sqlite-extension-examples.fly.dev](https://sqlite-extension-examples.fly.dev/data?sql=select%0D%0A++name%0D%0Afrom%0D%0A++pragma_function_list()%0D%0Awhere%0D%0A++name+not+in+(%0D%0A++++select%0D%0A++++++value%0D%0A++++from%0D%0A++++++json_each(%3Ajson)%0D%0A++)&json=[%22pow%22%2C%22group_concat%22%2C%22json_type%22%2C%22julianday%22%2C%22ntile%22%2C%22nullif%22%2C%22sqlite_compileoption_get%22%2C%22json_valid%22%2C%22json_quote%22%2C%22json_patch%22%2C%22-%3E%22%2C%22json_array%22%2C%22current_timestamp%22%2C%22power%22%2C%22sqlite_compileoption_used%22%2C%22json_remove%22%2C%22json_object%22%2C%22json_insert%22%2C%22-%3E%3E%22%2C%22sin%22%2C%22sum%22%2C%22quote%22%2C%22printf%22%2C%22likelihood%22%2C%22json_replace%22%2C%22json_extract%22%2C%22last_value%22%2C%22rank%22%2C%22sign%22%2C%22sqrt%22%2C%22sinh%22%2C%22tan%22%2C%22round%22%2C%22rtrim%22%2C%22nth_value%22%2C%22tanh%22%2C%22random%22%2C%22trim%22%2C%22time%22%2C%22radians%22%2C%22trunc%22%2C%22total%22%2C%22substr%22%2C%22replace%22%2C%22upper%22%2C%22subtype%22%2C%22typeof%22%2C%22load_extension%22%2C%22soundex%22%2C%22json_group_array%22%2C%22avg%22%2C%22abs%22%2C%22json_group_object%22%2C%22json_array_length%22%2C%22strftime%22%2C%22atan%22%2C%22asin%22%2C%22acos%22%2C%22substring%22%2C%22randomblob%22%2C%22unicode%22%2C%22percent_rank%22%2C%22row_number%22%2C%22atanh%22%2C%22asinh%22%2C%22acosh%22%2C%22cos%22%2C%22atan2%22%2C%22last_insert_rowid%22%2C%22sqlite_log%22%2C%22unlikely%22%2C%22cosh%22%2C%22ceil%22%2C%22char%22%2C%22unixepoch%22%2C%22exp%22%2C%22count%22%2C%22date%22%2C%22ceiling%22%2C%22total_changes%22%2C%22changes%22%2C%22sqlite_version%22%2C%22degrees%22%2C%22floor%22%2C%22coalesce%22%2C%22glob%22%2C%22zeroblob%22%2C%22hex%22%2C%22iif%22%2C%22sqlite_source_id%22%2C%22format%22%2C%22datetime%22%2C%22cume_dist%22%2C%22ln%22%2C%22instr%22%2C%22json%22%2C%22dense_rank%22%2C%22log%22%2C%22ifnull%22%2C%22current_date%22%2C%22current_time%22%2C%22lag%22%2C%22mod%22%2C%22log2%22%2C%22like%22%2C%22max%22%2C%22min%22%2C%22lead%22%2C%22log10%22%2C%22lower%22%2C%22ltrim%22%2C%22first_value%22%2C%22pi%22%2C%22length%22%2C%22likely%22%2C%22json_set%22%2C%22escape_fts%22%2C%22prepare_connection_args%22%2C%22convert_units%22%2C%22sleep%22%2C%22rtreedepth%22%2C%22match%22%2C%22snippet%22%2C%22fts5_source_id%22%2C%22offsets%22%2C%22matchinfo%22%2C%22optimize%22%2C%22rtreecheck%22%2C%22rtreenode%22%2C%22highlight%22%2C%22bm25%22%2C%22fts3_tokenizer%22%2C%22fts5%22]).
