# Handling CSV files with wide columns in Python

Users [were reporting](https://github.com/simonw/sqlite-utils/issues/229) the following error using `sqlite-utils` to import some CSV files:

    _csv.Error: field larger than field limit (131072)

It turns out the Python standard library CSV module enforces a default field size limit on columns, and anything with more than 128KB of text in a column will raise an error.

You can modify this error using the [csv.field_size_limit(new_limit)](https://docs.python.org/3/library/csv.html#csv.field_size_limit) function.

There's one catch: the method doesn't provide a way to say "no limit". And it can throw an error if you feed it a value that is larger than the C long integer size on your platform.

So how do you set it to the maximum possible value? There's [an extensive StackOverflow thread](https://stackoverflow.com/questions/15063936/csv-error-field-larger-than-field-limit-131072) about this, with a number of different proposed solutions. Several of those use `ctypes` to find the correct value.

I didn't want to add a `ctypes` dependency out of paranoia that someone would try to use my library on a platform that didn't support it (I don't know if that paranoia has any basis at all). So I picked this pattern, [suggested by](https://stackoverflow.com/a/15063941) StackOverflow user **user1251007**:

```python
# Increase CSV field size limit to maximim possible
# https://stackoverflow.com/a/15063941
field_size_limit = sys.maxsize

while True:
    try:
        csv_std.field_size_limit(field_size_limit)
        break
    except OverflowError:
        field_size_limit = int(field_size_limit / 10)
```
This appears to work just fine. On macOS `sys.maxsize` works already, and on other platforms it should pick a field size limit that works.
