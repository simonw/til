# SQLite BLOB literals

I wanted to construct a string of SQL that would return a blob value:

```sql
select 'binary-data' as content, 'x.jpg' as content_filename
```

This was while writing a unit test for `datasette-media` - for [issue #19](https://github.com/simonw/datasette-media/issues/19).

The SQLite documentation for [Literal values](https://www.sqlite.org/lang_expr.html#literal_values_constants_) explains how to do this:

> BLOB literals are string literals containing hexadecimal data and preceded by a single "x" or "X" character. Example: X'53514C697465' 

In Python 3 you can generate the hexadecimal representation of any byte string using `b'...'.hex()`

So my solution looked like this:

```python
jpeg_bytes = open("content.jpg", "rb").read()
sql = "select X'{}' as content, 'x.jpg' as content_filename".format(jpeg_bytes.hex())
```
