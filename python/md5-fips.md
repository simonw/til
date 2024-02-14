# Getting Python MD5 to work with FIPS systems

[This issue](https://github.com/simonw/datasette/issues/2270) by Parand Darugar pointed out that Datasette doesn't currently run on Linux systems with FIPS enabled, due to the way it uses MD5 hashes.

I hadn't heard of FIPS before. It stands for [the Federal Information Processing Standard](https://en.wikipedia.org/wiki/FIPS_140-2), and it's a set of US government standards around how cryptographic algorithms should be used.

Certain operating systems can run in a FIPS mode, and running them like that disables certain cryptographic algorithms that are considered to be too weak.

Unsurprisingly, MD5 is one of the algorithms that is disabled in FIPS mode.

## Legitimate uses of MD5

The problem here is that Datasette uses MD5 for non-cryptographic purposes. It uses it in two places.

```python
 @property 
 def color(self): 
     if self.hash: 
         return self.hash[:6] 
     return hashlib.md5(self.name.encode("utf8")).hexdigest()[:6] 
```
[This method](https://github.com/simonw/datasette/blob/5d7997418664bcdfdba714c16bd5a67c241e8740/datasette/database.py#L73-L77) generates a color associated with a database, using the first 6 characters of the MD5 hash of the database name. I picked this trick up years ago from [Dopplr](https://en.wikipedia.org/wiki/Dopplr).

The second place [is here](https://github.com/simonw/datasette/blob/5d7997418664bcdfdba714c16bd5a67c241e8740/datasette/utils/__init__.py#L705-L725):

```python
def to_css_class(s):
    """
    Given a string (e.g. a table name) returns a valid unique CSS class.
    For simple cases, just returns the string again. If the string is not a
    valid CSS class (we disallow - and _ prefixes even though they are valid
    as they may be confused with browser prefixes) we strip invalid characters
    and add a 6 char md5 sum suffix, to make sure two tables with identical
    names after stripping characters don't end up with the same CSS class.
    """
    if css_class_re.match(s):
        return s
    md5_suffix = hashlib.md5(s.encode("utf8")).hexdigest()[:6]
    # Strip leading _, -
    s = s.lstrip("_").lstrip("-")
    # Replace any whitespace with hyphens
    s = "-".join(s.split())
    # Remove any remaining invalid characters
    s = css_invalid_chars_re.sub("", s)
    # Attach the md5 suffix
    bits = [b for b in (s, md5_suffix) if b]
    return "-".join(bits)
```
The code comment explains what's happening here - this is a way to turn any string into a valid CSS class name. It's actually used [for custom template names as well](https://docs.datasette.io/en/stable/custom_templates.html#custom-templates).

Both of these uses of MD5 are legitimate. But... attempting to run Datasette on a FIPS system produces the following runtime error:

```
else hashlib.md5(name.encode("utf8")).hexdigest()[:6],
ValueError: [digital envelope routines] unsupported
```

## Python MD5 and usedforsecurity=False

Python 3.9, released in 2020, introduced a fix for this issue: the `usedforsecurity=False` parameter, [documented here](https://docs.python.org/3/library/hashlib.html#hashlib.new). This had been under discussion [since 2010](https://github.com/python/cpython/issues/53462#issuecomment-1093510111)!

If you run MD5 like this, FIPS systems won't complain:

```python
value = b"These are some bytes"
digest = hashlib.md5(value, usedforsecurity=False).hexdigest()
```
The default value there is `=True`, so you have to explicitly pass `=False` to pass the FIPS check.

This is a great solution... if you are running Python 3.9 or later.

## A fix for Python 3.8

Datasette supports all versions of Python that are not yet [EOL for support](https://devguide.python.org/versions/). This means Python 3.8 is supported until at least October 2024.

Since this is a runtime error, I figured out a way to fix this with a utility function:

```python
def md5_not_usedforsecurity(s):
    try:
        return hashlib.md5(s.encode("utf8"), usedforsecurity=False).hexdigest()
    except TypeError:
        # For Python 3.8 which does not support usedforsecurity=False
        return hashlib.md5(s.encode("utf8")).hexdigest()
```
This catches the `TypeError` thrown by `hashlib.md5` when `usedforsecurity=False` is not supported, and falls back to running the function without that parameter.

This means that Datasette can now run on FIPS-enabled systems provided they are running Python 3.9 or higher, and can continue to work on Python 3.8 systems that have not enabled FIPS mode.

## Testing this out using Docker

The hardest part of fixing this was figuring out how to test it.

Eventually I found a recent Docker image with FIPS enabled, by searching Docker Hub for "fips" and sorting by recently updated:

https://hub.docker.com/search?q=fips&sort=updated_at&order=desc

I found [ubuntu-ruby-fips](https://hub.docker.com/r/cyberark/ubuntu-ruby-fips) which includes a recent Ubuntu with FIPS enabled.

I started a container like this:
```bash
docker run -it --rm cyberark/ubuntu-ruby-fips /bin/bash
```
Then installed Python 3 and Git in that container like this:
```bash
apt-gen update && apt-get install -y python3 git python3.10-venv
```
Then I could run the Datasette test suite like so:
```bash
cd /tmp
git clone https://github.com/simonw/datasette
cd datasette
python3 -m venv venv
source venv/bin/activate
pip install -e '.[test]'
pytest -n auto
```
This failed the first time with the expected `ValueError: [digital envelope routines] unsupported` errors - but after I applied [this change](https://github.com/simonw/datasette/commit/b89cac3b6a63929325c067d0cf2d5748e4bf4d2e) the tests passed, showing my fix worked.
