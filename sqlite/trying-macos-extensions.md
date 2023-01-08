# Trying out SQLite extensions on macOS

Alex Garcia has been building some really cool new custom extensions for SQLite, working in C and Go. So far he's released two:

- [sqlite-lines](https://github.com/asg017/sqlite-lines), written in C, which adds `lines(text, optional-delimiter)` and `lines_read(filepath, optional-delimiter)` table-valued functions, for processing files line-by-line.
- [sqlite-html](https://github.com/asg017/sqlite-html), 
written in Go, which provides a [whole family of functions](https://github.com/asg017/sqlite-html/blob/main/docs.md) for parsing and constructing HTML strings.

Both of these have interactive demos, which you can try out in your browser in Alex's Observable notebooks:

- [Introducing sqlite-lines - a SQLite extension for reading files line-by-line](https://observablehq.com/@asg017/introducing-sqlite-lines)
- [Introducing sqlite-html: query, parse, and generate HTML in SQLite](https://observablehq.com/@asg017/introducing-sqlite-html)

Getting them to run on a macOS laptop is harder. Here's how I got them to work.

## Don't use the sqlite3 command that came with macOS

The `sqlite3` command that comes built in to macOS has a frustrating limitation: it has been compiled without the ability to load new extensions.

You can confirm this by running the following:

    sqlite3 :memory: 'select * from pragma_compile_options()'

On my machine part of the ouput from this says `OMIT_LOAD_EXTENSION`.

You can run `which sqlite3` to see where it is located - on my system that outputs `/usr/bin/sqlite3`.

If you use Homebrew you can run `brew install sqlite` - this will install a modern version of SQLite, but it won't link it into your path (it's a "key-only package" in Homebrew jargon) to avoid conflicting with the macOS default installation. Running `brew info sqlite` confirms this.

```
% brew info sqlite 
sqlite: stable 3.39.2 (bottled) [keg-only]
Command-line interface for SQLite
https://sqlite.org/index.html
/usr/local/Cellar/sqlite/3.39.2 (11 files, 4.4MB)
  Poured from bottle on 2022-07-24 at 14:46:49
From: https://github.com/Homebrew/homebrew-core/blob/HEAD/Formula/sqlite.rb
License: blessing
==> Dependencies
Required: readline ✔
==> Caveats
sqlite is keg-only, which means it was not symlinked into /usr/local,
because macOS already provides this software and installing another version in
parallel can cause all kinds of trouble.

If you need to have sqlite first in your PATH, run:
  echo 'export PATH="/usr/local/opt/sqlite/bin:$PATH"' >> ~/.zshrc
...
```
So the command is installed but is not on your path. It lives at `/usr/local/opt/sqlite/bin/sqlite3` - so you can run this version using that full path.

Running this confirms that it doesn't have that `OMIT_LOAD_EXTENSION` option:

    /usr/local/opt/sqlite/bin/sqlite3 :memory: \
      'select * from pragma_compile_options()'

(It also reveals some exciting extra extensions: `ENABLE_GEOPOLY` and `ENABLE_RTREE` are both listed there.)

You can also download a precompiled SQLite binary for macOS from the [SQLite downloads page](https://www.sqlite.org/download.html) - though this isn't signed, so you'll need to follow the steps described next to get it to run.

## Download the .dylib files using wget

I figured this out after first writing this TIL. If you download a `.dylib` extension using `wget` it will work straight away:
```
% cd /tmp
/tmp % wget https://github.com/asg017/sqlite-lines/releases/download/v0.1.1/lines0.dylib
...
Saving to: ‘lines0.dylib’
/tmp % /usr/local/opt/sqlite/bin/sqlite3
SQLite version 3.39.2 2022-07-21 15:24:47
Enter ".help" for usage hints.
Connected to a transient in-memory database.
Use ".open FILENAME" to reopen on a persistent database.
sqlite> .load lines0
sqlite> .mode column
sqlite> select
  line ->> 'color' as color, 
  sum(line ->> 'value') as sum
from lines('{"color":"red","value":56}
{"color":"red","value":79}
{"color":"blue","value":52}
{"color":"blue","value":15}') group by color;
color  sum
-----  ---
blue   67 
red    135
```
## And for sqlite-html

Grab the `html0.dylib` extension from Alex's [releases page](https://github.com/asg017/sqlite-html/releases/tag/v0.1.0), again using `wget`:
```
% cd /tmp
% wget https://github.com/asg017/sqlite-html/releases/download/v0.1.0/html0.dylib
 % /usr/local/opt/sqlite/bin/sqlite3
sqlite> .load html0.dylib
sqlite> select name from pragma_function_list where name like 'html_%';
html_valid
html_count
html_text
html_text
html_group_element_div
html_attr_get
html_attribute_has
html_group_element_span
html_attr_has
html_element
html_trim
html_table
html_attribute_get
html_extract
html_version
html_debug
html_escape
html_unescape
sqlite> .mode column
sqlite> select * from html_each('<ul>
<li>Alpha</li>
<li>Bravo</li>
<li>Charlie</li>
<li>Delta</li>', 'li');
html              text   
----------------  -------
<li>Alpha</li>    Alpha  
<li>Bravo</li>    Bravo  
<li>Charlie</li>  Charlie
<li>Delta</li>    Delta  
```

## If you download with your browser you'll have to jump through more hoops

I first tried downloading the `lines0.dylib` file from the [0.1.1 release page](https://github.com/asg017/sqlite-lines/releases/tag/v0.1.1).

The first time I tried loading the extension I got this error:

```
% /usr/local/opt/sqlite/bin/sqlite3
sqlite> .load /Users/simon/Downloads/lines0.dylib
Error: dlopen(/Users/simon/Downloads/lines0.dylib.dylib, 0x000A): tried: '/Users/simon/Downloads/lines0.dylib.dylib' (no such file), '/usr/local/lib/lines0.dylib.dylib' (no such file), '/usr/lib/lines0.dylib.dylib' (no such file)
```
macOS popped up up a helpful dialog box saing what went wrong:

<img src="https://static.simonwillison.net/static/2022/sqlite-lines-computer-says-no.png" width="300" alt="lines0.dylib cannot be opened because the developer cannot be verified. macOS cannot verify that this app is free from malware. Buttons: Move to Trash or Cancel">

This is because the code hasn't been signed. You can still open it though - the trick is to head over to the macOS Security tab in System Preferences:

![The security panel now has an extra line saying "lines0.dylib was blocked from use because it is not from an identified developer" - with a Allow Anyway button.](https://static.simonwillison.net/static/2022/security-lines0.png)

Click "Allow Anyway", then try running the `.load` command again. Click "Open" one more time in this dialog:

<img src="https://static.simonwillison.net/static/2022/lines0-allow.png" width="300" alt="Same dialog a before but now there is an Open button">

And the extension will load from now on!

## And for Python

See [Loading SQLite extensions in Python on macOS](https://til.simonwillison.net/sqlite/sqlite-extensions-python-macos).
