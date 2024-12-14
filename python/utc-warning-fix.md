# Fixes for datetime UTC warnings in Python

I was getting the following warning for one of my Python test suites:

> `DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).`

I also saw a deprecation warning elsewhere for my usage of `datetime.datetime.utcfromtimestamp(iso_timestamp_string)`.

## datetime.datetime.now(datetime.timezone.utc)

I tried switching to `datetime.UTC` for the first warning, but that caused my tests to fail on versions of Python prior to 3.11. I support all versions of Python that have not yet hit EOL for support, which is currently [Python 3.9 and higher](https://devguide.python.org/versions/).

According to [the documentation](https://docs.python.org/3/library/datetime.html#datetime.UTC) `datetime.UTC` was added in Python 3.11 as an alias for `datetime.timezone.utc` - so I switched my usage of `datetime.utcnow()` to the following instead:

```python
import datetime

utcnow = datetime.datetime.now(datetime.timezone.utc)
```
These tests now passed for Python 3.9+.

## datetime.datetime.fromtimestamp(s, datetime.timezone.utc)

I found another hint [in the docs](https://docs.python.org/3/library/datetime.html#datetime.datetime.utcfromtimestamp) for replacing the now deprecated `datetime.datetime.utcfromtimestamp`:

> **Warning**: Because naive `datetime` objects are treated by many `datetime` methods as local times, it is preferred to use aware datetimes to represent times in UTC. As such, the recommended way to create an object representing a specific timestamp in UTC is by calling `datetime.fromtimestamp(timestamp, tz=timezone.utc)`.

Again, `timezone.utc` was the right fix here to keep things working in pre-3.11 versions:

```python
import datetime

utc_datetime = datetime.datetime.fromtimestamp(created_string, datetime.timezone.utc)
```
Here's [the commit](https://github.com/simonw/llm/commit/571f4b2a4da52ad127061b7fa953562f6ba6aeb0) where I fixed both of these warnings for my LLM project.
