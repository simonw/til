# Using io.BufferedReader to peek against a non-peekable stream

When building the [--sniff option](https://github.com/simonw/sqlite-utils/issues/230) for `sqlite-utils insert` (which attempts to detect the correct CSV delimiter and quote character by looking at the first 2048 bytes of a CSV file) I had the need to peek ahead in an incoming stream of data.

I use Click, and Click can automatically handle both files and standard input. The problem I had is that peeking ahead in a file is easy (you can call `.read()` and then `.seek(0)`, or use the `.peek()` method directly) but peaking ahead in standard input is not - anything you consume from that is not available to rewind to later on.

Since my code works by passing a file-like object to the `csv.reader()` function I needed a way to read the first 2048 bytes but then reset the stream ready for that function to consume it.

I figured out how to do that using the `io.BufferedReader` class. Here's the pattern:

```python
import io
import sys
import csv

# Get a file-like object in binary mode
fp = open("myfile.csv", "rb")
# Or from standard input (need to use .buffer here)
fp = sys.stdin.buffer

# Wrap it in a buffered reader with a 4096 byte buffer
buffered = io.BufferedReader(fp, buffer_size=4096)

# Wrap THAT in a text io wrapper that can decode to unicode
decoded = io.TextIOWrapper(buffered, encoding="utf-8")

# Now I can read the first 2048 bytes...
first_bytes = buffered.peek(2048)

# But I can still pass the "decoded" object to csv.reader
reader = csv.reader(decoded)
for row in reader:
    print(row)
```
My implementation is in [this commit](https://github.com/simonw/sqlite-utils/commit/99ff0a288c08ec2071139c6031eb880fa9c95310).
