# Running PyPy on macOS using Homebrew

[Towards Inserting One Billion Rows in SQLite Under A Minute](https://avi.im/blag/2021/fast-sqlite-inserts/) includes this snippet:

> All I had to do was run my existing code, without any change, using PyPy. It worked and the speed bump was phenomenal. The batched version took only 2.5 minutes to insert 100M rows. I got close to 3.5x speed :)

I decided to try this out against my own Python tool for [inserting CSV files](https://sqlite-utils.datasette.io/en/stable/cli.html#inserting-csv-or-tsv-data), `sqlite-utils`.

I installed PyPy using Homebrew:

    brew install pypy3

Having run this, `pypy3` was available on my command-line.

I used that to create a PyPy virtual environment in my `/tmp` directory:

```
cd /tmp
pypy3 -m venv venv
source venv/bin/activate
```
Running `python --version` confirmed that this had worked:
```
% python --version
Python 3.7.13 (7e0ae751533460d5f89f3ac48ce366d8642d1db5, Apr 26 2022, 09:29:08)
[PyPy 7.3.9 with GCC Apple LLVM 13.1.6 (clang-1316.0.21.2)]
```
Then I installed `sqlite-utils` into that virtual environment like so:
```
pip install sqlite-utils
```
And confirmed the installation like this:
```
(venv) /tmp % which sqlite-utils
/private/tmp/venv/bin/sqlite-utils
(venv) /tmp % head $(which sqlite-utils)
#!/private/tmp/venv/bin/pypy3
# -*- coding: utf-8 -*-
import re
import sys
from sqlite_utils.cli import cli
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(cli())
```
Then I tested an import against a large CSV file like so:
```
(venv) /tmp % time sqlite-utils insert pypy.db t /tmp/en.openfoodfacts.org.products.csv --csv
  [------------------------------------]    0%
  [###################################-]   99%
  12.67s user 2.53s system 92% cpu 16.514 total
```
I tried the same thing using regular Python `sqlite-utils` too:
```
~ % time sqlite-utils insert pydb t /tmp/en.openfoodfacts.org.products.csv --csv 
  [------------------------------------]    0%
  [###################################-]   99%
  12.74s user 2.40s system 93% cpu 16.172 total
```
Surprisingly I didn't get any meaningful difference in performance between the two. But at least I know how to run things using PyPy now.
