# Using iconv to convert the text encoding of a file

In [sqlite-utils issue 439](https://github.com/simonw/sqlite-utils/issues/439) I was testing against a CSV file that used UTF16 little endian encoding, also known as `utf-16-le`.

I converted it to UTF-8 using `iconv` like this:

    iconv -f UTF-16LE -t UTF-8 file-in-utf16le.csv > file-in-utf8.csv

The `-f` argument here is the input encoding and `-t` is the desired output encoding.

I figured out the `-f` argument should be `UTF-16LE` (after first trying and failing with `utf-16-le`) by running:

    iconv -l

This outputs all of the available encoding options. It's a pretty long list so I filtered it like this:
```
% iconv -l | grep UTF
UTF-8 UTF8
UTF-8-MAC UTF8-MAC
UTF-16
UTF-16BE
UTF-16LE
UTF-32
UTF-32BE
UTF-32LE
UNICODE-1-1-UTF-7 UTF-7 CSUNICODE11UTF7
```

## Discarding invalid characters

I picked up this tip [from Ben Brandwood](https://twitter.com/ben_brandwood/status/1617926062213853185): you can also use `iconv` to fix problems when a file includes invalid UTF-8 characters.

The trick is to use the `-c` option, which `iconv --help` tells you will "discard unconvertible characters".

Here's Ben's recipe:

    iconv -f utf-8 -t utf-8 -c FILE.txt -o NEW_FILE

Note that the input encoding (`-f`) and the output encoding (`-t`) are the same here. The `-c` option does all of the work.
