# struct endianness in Python

TIL the Python standard library [struct](https://docs.python.org/3/library/struct.html) module defaults to interpreting binary strings using the endianness of your machine.

Which means that this code:

```python
def decode_matchinfo(buf): 
    # buf is a bytestring of unsigned integers, each 4 bytes long 
    return struct.unpack("I" * (len(buf) // 4), buf) 
```
Behaves differently on big-endian v.s. little-endian systems.

I found this out thanks to [this bug report](https://github.com/simonw/sqlite-fts4/issues/6) against my sqlite-fts4 library.

My `decode_matchinfo()` function runs against a binary data structure returned by SQLite - more details on that in [Exploring search relevance algorithms with SQLite](https://simonwillison.net/2019/Jan/7/exploring-search-relevance-algorithms-sqlite/).

SQLite doesn't change the binary format depending on the endianness of the system, which means that my function here works correctly on little-endian but does the wrong thing on big-endian systems:

On little-endian systems:

```pycon
>>> buf = b'\x01\x00\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00'
>>> decode_matchinfo(buf)
(1, 2, 2, 2)
```
But on big-endian systems:
```pycon
>>> buf = b'\x01\x00\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00'
>>> decode_matchinfo(buf)
(16777216, 33554432, 33554432, 33554432)
```
The fix is to add a first character to that format string specifying the endianness that should be used, see [Byte Order, Size, and Alignment](https://docs.python.org/3/library/struct.html#struct-alignment) in the Python documentation.

```pycon
>>> struct.unpack("<IIII", buf)
(1, 2, 2, 2)
>>> struct.unpack(">IIII", buf)
(16777216, 33554432, 33554432, 33554432)
```
So [the fix](https://github.com/simonw/sqlite-fts4/commit/ed6ea76a727243e9b0bff4fe7cf7022fcd1ec834) for my bug was to rewrite the function to look like this:
```python
def decode_matchinfo(buf):
    # buf is a bytestring of unsigned integers, each 4 bytes long
    return struct.unpack("<" + ("I" * (len(buf) // 4)), buf)
```
## Bonus: How to tell which endianness your system has

Turns out Python can tell you if you are big-endian or little-endian like this:

```pycon
>>> from sys import byteorder
>>> byteorder
'little'
```
