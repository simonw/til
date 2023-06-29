# CLI tools hidden in the Python standard library

Seth Michael Larson [pointed out](https://twitter.com/sethmlarson/status/1674141676325990400) that the Python `gzip` module can be used as a CLI tool like this:

```bash
python -m gzip --decompress pypi.db.gz
```
This is a neat Python feature: modules with a `if __name__ == "__main__":` block that are available on Python's standard import path can be executed from the terminal using `python -m name_of_module`.

Seth pointed out this is useful if you are on Windows and don't have the `gzip` utility installed.

This made me wonder: what other little tools are lurking in the Python standard library, available on any computer with a working Python installation?

## Finding them with ripgrep

I decided to take a sniff around the standard library and see what I can find.

Jim Crist-Harif [pointed me](https://twitter.com/jcristharif/status/1674146077757276162) to `python -m site`, which outputs useful information about your installation:

```bash
python3.11 -m site
```
```
sys.path = [
    '/opt/homebrew/Cellar/python@3.11/3.11.4_1/Frameworks/Python.framework/Versions/3.11/lib/python3.11',
    '/opt/homebrew/Cellar/python@3.11/3.11.4_1/Frameworks/Python.framework/Versions/3.11/lib/python311.zip',
    '/opt/homebrew/Cellar/python@3.11/3.11.4_1/Frameworks/Python.framework/Versions/3.11/lib/python3.11/lib-dynload',
    '/opt/homebrew/lib/python3.11/site-packages',
    '/opt/homebrew/opt/python@3.11/Frameworks/Python.framework/Versions/3.11/lib/python3.11/site-packages',
]
USER_BASE: '/Users/simon/Library/Python/3.11' (doesn't exist)
USER_SITE: '/Users/simon/Library/Python/3.11/lib/python/site-packages' (doesn't exist)
ENABLE_USER_SITE: True
```
This showed me that the standard library itself for my Homebrew installation of Python 3.11 is in `/opt/homebrew/Cellar/python@3.11/3.11.4_1/Frameworks/Python.framework/Versions/3.11/lib/python3.11`.

So I switched there and used `ripgrep` to find likely packages:

```
cd /opt/homebrew/Cellar/python@3.11/3.11.4_1/Frameworks/Python.framework/Versions/3.11/lib/python3.11
```
Then ran `rg`:
```
rg 'if __name__ =' -l | grep -v 'test/' \
  | grep -v 'tests/' | grep -v idlelib | grep -v turtledemo
```
The `-l` option causes `ripgrep` to list matching files without showing the context of the match.

I built up those `grep -v` exclusions over a few iterations - `idlelib/` and `turtledemo/` have a bunch of matches that I wasn't interested in.

Here's the result:

```
tabnanny.py
pyclbr.py
netrc.py
heapq.py
fileinput.py
site.py
telnetlib.py
smtplib.py
timeit.py
__hello__.py
aifc.py
json/tool.py
asyncio/__main__.py
runpy.py
mailcap.py
tokenize.py
smtpd.py
sysconfig.py
tarfile.py
lib2to3/pgen2/tokenize.py
lib2to3/pgen2/driver.py
lib2to3/pgen2/literals.py
xmlrpc/server.py
xmlrpc/client.py
getopt.py
dbm/__init__.py
doctest.py
pickle.py
imaplib.py
compileall.py
shlex.py
ast.py
venv/__init__.py
py_compile.py
ensurepip/__main__.py
ensurepip/_uninstall.py
http/server.py
pickletools.py
poplib.py
quopri.py
calendar.py
pprint.py
symtable.py
pstats.py
inspect.py
pdb.py
platform.py
wsgiref/simple_server.py
random.py
ftplib.py
mimetypes.py
turtle.py
tkinter/dialog.py
xml/sax/expatreader.py
tkinter/colorchooser.py
tkinter/dnd.py
tkinter/filedialog.py
tkinter/messagebox.py
tkinter/simpledialog.py
tkinter/font.py
tkinter/scrolledtext.py
xml/sax/xmlreader.py
tkinter/__init__.py
code.py
difflib.py
pydoc.py
uu.py
imghdr.py
filecmp.py
profile.py
cgi.py
codecs.py
modulefinder.py
__phello__/__init__.py
__phello__/spam.py
multiprocessing/spawn.py
textwrap.py
base64.py
curses/textpad.py
curses/has_key.py
zipapp.py
cProfile.py
dis.py
webbrowser.py
nntplib.py
sndhdr.py
gzip.py
ctypes/util.py
zipfile.py
encodings/rot_13.py
distutils/fancy_getopt.py
```
That's a lot of neat little tools!

I haven't explored my way through all of them yet, but running `python -m module_name` usually outputs something useful, and adding `-h` frequently provides help.

## A few highlights

Here are a few of the commands I've figured out so far.

### http.server

To run a localhost webserver on port 8000, serving the content of the current directory:

```bash
python -m http.server
```

This takes an optional port. To change port, do this:

```bash
python -m http.server 8001
```
Pass `-h` for more options.

### base64

```bash
python3.11 -m base64 -h
```
```
usage: .../base64.py [-h|-d|-e|-u|-t] [file|-]
        -h: print this help message and exit
        -d, -u: decode
        -e: encode (default)
        -t: encode and decode string 'Aladdin:open sesame'
```

### asyncio

This provides a Python console with top-level await:
```bash
python -m asyncio
```
```pycon
asyncio REPL 3.11.4 (main, Jun 20 2023, 17:23:00) [Clang 14.0.3 (clang-1403.0.22.14.1)] on darwin
Use "await" directly instead of "asyncio.run()".
Type "help", "copyright", "credits" or "license" for more information.
>>> import asyncio
>>> import httpx
>>> async with httpx.AsyncClient() as client:
...     r = await client.get('https://www.example.com/')
... 
>>> r.text[:50]
'<!DOCTYPE html>\n<html lang="en">\n<head>\n  <meta ht'
```

### tokenize

This is fun - it's a debug mode for the Python tokenizer. You can run it directly against a file:

```bash
python -m tokenize cgi.py | head -n 10
```
```
0,0-0,0:            ENCODING       'utf-8'        
1,0-1,24:           COMMENT        '#! /usr/local/bin/python'
1,24-1,25:          NL             '\n'           
2,0-2,1:            NL             '\n'           
3,0-3,66:           COMMENT        '# NOTE: the above "/usr/local/bin/python" is NOT a mistake.  It is'
3,66-3,67:          NL             '\n'           
4,0-4,59:           COMMENT        '# intentionally NOT "/usr/bin/env python".  On many systems'
4,59-4,60:          NL             '\n'           
5,0-5,65:           COMMENT        '# (e.g. Solaris), /usr/local/bin is not in $PATH as passed to CGI'
5,65-5,66:          NL             '\n'           
```
### ast

Even more fun than `tokenize` - a debug mode for the Python AST module!
```bash
python -m ast cgi.py | head -n 10
```
```
Module(
   body=[
      Expr(
         value=Constant(value='Support module for CGI (Common Gateway Interface) scripts.\n\nThis module defines a number of utilities for use by CGI scripts\nwritten in Python.\n\nThe global variable maxlen can be set to an integer indicating the maximum size\nof a POST request. POST requests larger than this size will result in a\nValueError being raised during parsing. The default value of this variable is 0,\nmeaning the request size is unlimited.\n')),
      Assign(
         targets=[
            Name(id='__version__', ctx=Store())],
         value=Constant(value='2.6')),
      ImportFrom(
         module='io',
```
I used this module to build my [symbex](https://github.com/simonw/symbex) tool - this debug mode would have helped quite a bit if I'd found out about it earlier.

### json.tool

Pretty-print JSON:

```bash
echo '{"foo": "bar", "baz": [1, 2, 3]}' | python -m json.tool
```
```json
{
    "foo": "bar",
    "baz": [
        1,
        2,
        3
    ]
}
```
### random

I thought this might provide a utility for generating random numbers, but sadly it's just a benchmarking suite with no additional command-line options:

```bash
python -m random
```
```
0.000 sec, 2000 times random
avg 0.49105, stddev 0.290864, min 0.00216092, max 0.999473

0.001 sec, 2000 times normalvariate
avg -0.00286956, stddev 0.996872, min -3.42333, max 4.2012

0.001 sec, 2000 times lognormvariate
avg 1.64228, stddev 2.13138, min 0.0386213, max 34.0379

0.001 sec, 2000 times vonmisesvariate
avg 3.18754, stddev 2.27556, min 0.00336177, max 6.28306
...
```

### nntplib

"nntplib built-in demo - display the latest articles in a newsgroup"

It defaults to `gmane.comp.python.general`:

```bash
python -m nntplib
```
```
Group gmane.comp.python.general has 757237 articles, range 23546 to 848591
 848582 MRAB via Python-...  Re: Trouble with defaults and timeout ...  (40)
 848583 Dave Ohlsson via...  unable to run the basic Embedded Pytho...  (179)
 848584 Piergiorgio Sart...  Re: Trouble with defaults and timeout ...  (43)
 848585 Dan Kolis via Py...  TKinter in Python - advanced notions - ok  (52)
 848586 Fulian Wang via ...  Re: unable to run the basic Embedded P...  (190)
 848587 Fulian Wang via ...  Re: unable to run the basic Embedded P...  (220)
 848588 Christian Gollwi...  Re: unable to run the basic Embedded P...  (26)
 848589 small marcc via ...  my excel file is not updated to add ne...  (42)
 848590 Thomas Passin vi...  Re: my excel file is not updated to ad...  (47)
 848591 dn via Python-list   Re: my excel file is not updated to ad...  (207)
```
Those look like real, recent messages - I matched them with [this mirror](https://www.mail-archive.com/python-list@python.org/). 

When I tried passing other newsgroup names with `python -m nntplib -g alt.humor.puns` I got an error though:

> `NNTPTemporaryError: 411 No such group alt.humor.puns`

### calendar

Show a calendar for the current year:
```bash
python -m calendar
```
```
                                  2023

      January                   February                   March
Mo Tu We Th Fr Sa Su      Mo Tu We Th Fr Sa Su      Mo Tu We Th Fr Sa Su
                   1             1  2  3  4  5             1  2  3  4  5
 2  3  4  5  6  7  8       6  7  8  9 10 11 12       6  7  8  9 10 11 12
 9 10 11 12 13 14 15      13 14 15 16 17 18 19      13 14 15 16 17 18 19
16 17 18 19 20 21 22      20 21 22 23 24 25 26      20 21 22 23 24 25 26
23 24 25 26 27 28 29      27 28                     27 28 29 30 31
30 31

       April                      May                       June
Mo Tu We Th Fr Sa Su      Mo Tu We Th Fr Sa Su      Mo Tu We Th Fr Sa Su
                1  2       1  2  3  4  5  6  7                1  2  3  4
 3  4  5  6  7  8  9       8  9 10 11 12 13 14       5  6  7  8  9 10 11
10 11 12 13 14 15 16      15 16 17 18 19 20 21      12 13 14 15 16 17 18
17 18 19 20 21 22 23      22 23 24 25 26 27 28      19 20 21 22 23 24 25
24 25 26 27 28 29 30      29 30 31                  26 27 28 29 30

        July                     August                  September
Mo Tu We Th Fr Sa Su      Mo Tu We Th Fr Sa Su      Mo Tu We Th Fr Sa Su
                1  2          1  2  3  4  5  6                   1  2  3
 3  4  5  6  7  8  9       7  8  9 10 11 12 13       4  5  6  7  8  9 10
10 11 12 13 14 15 16      14 15 16 17 18 19 20      11 12 13 14 15 16 17
17 18 19 20 21 22 23      21 22 23 24 25 26 27      18 19 20 21 22 23 24
24 25 26 27 28 29 30      28 29 30 31               25 26 27 28 29 30
31

      October                   November                  December
Mo Tu We Th Fr Sa Su      Mo Tu We Th Fr Sa Su      Mo Tu We Th Fr Sa Su
                   1             1  2  3  4  5                   1  2  3
 2  3  4  5  6  7  8       6  7  8  9 10 11 12       4  5  6  7  8  9 10
 9 10 11 12 13 14 15      13 14 15 16 17 18 19      11 12 13 14 15 16 17
16 17 18 19 20 21 22      20 21 22 23 24 25 26      18 19 20 21 22 23 24
23 24 25 26 27 28 29      27 28 29 30               25 26 27 28 29 30 31
30 31
```
This one has a bunch more options (visible with `-h`). `python -m calendar -t html` produces the calendar in HTML, for example.

### Loads more

There are plenty more in there - these are just the ones I've explored so far.

