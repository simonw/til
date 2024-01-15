# Using pprint() to print dictionaries while preserving their key order

While parsing a CSV file using `csv.DictReader` today I noticed the following surprising result:

```python
import csv
from io import StringIO
from pprint import pprint

csv_content = """id,name,latitude,longitude,country
nyc,New York City,40.7128,-74.006,US
lon,London,51.5074,-0.1278,GB
tok,Tokyo,35.6895,139.6917,JP"""

rows = list(csv.DictReader(StringIO(csv_content)))
pprint(rows)
```
This output the following:
```python
[{'country': 'US',
  'id': 'nyc',
  'latitude': '40.7128',
  'longitude': '-74.006',
  'name': 'New York City'},
 {'country': 'GB',
  'id': 'lon',
  'latitude': '51.5074',
  'longitude': '-0.1278',
  'name': 'London'},
 {'country': 'JP',
  'id': 'tok',
  'latitude': '35.6895',
  'longitude': '139.6917',
  'name': 'Tokyo'}]
```
I had expected `DictReader()` to preserve the order of keys from the CSV file, since Python has defaulted to ordered dictionaries for a while now.

It turns out `DictReader()` does do that... but `pprint()` does not! From the [pprint documentation](https://docs.python.org/3/library/pprint.html#pprint.pprint):

> `pprint.pprint(object, stream=None, indent=1, width=80, depth=None, *, compact=False, sort_dicts=True, underscore_numbers=False)`

Note that `sort_dicts` defaults to `True`, presumably for historical reasons.

So the following does what I had expected in the first place:
```python
pprint(rows, sort_dicts=False)
```
Output:
```python
[{'id': 'nyc',
  'name': 'New York City',
  'latitude': '40.7128',
  'longitude': '-74.006',
  'country': 'US'},
 {'id': 'lon',
  'name': 'London',
  'latitude': '51.5074',
  'longitude': '-0.1278',
  'country': 'GB'},
 {'id': 'tok',
  'name': 'Tokyo',
  'latitude': '35.6895',
  'longitude': '139.6917',
  'country': 'JP'}]
```

