# Compile a new sqlite3 binary on Ubuntu

I wanted to try the `vacuum into` backup command that was released in SQLite3 3.27.0 [on 2019-02-07](https://www.sqlite.org/changes.html#version_3_27_0).

Ubuntu 18.04.4 LTS has SQLite 3.22.0 from 2018-01-22.

Thankfully it's really easy to compile a new `sqlite3` binary on Ubuntu, using the amalgamation release.

```
cd /tmp
wget https://www.sqlite.org/2020/sqlite-amalgamation-3310100.zip
unzip sqlite-amalgamation-3310100.zip
cd sqlite-amalgamation-3310100
gcc shell.c sqlite3.c -lpthread -ldl
./a.out --version
3.31.1 2020-01-27 19:55:54 3bfa9cc97da10598521b342961df8f5f68c7388fa117345eeb516eaa837bb4d6
```
Now you can move the `a.out` file somewhere else:
```
mkdir ~/bin
mv ./a.out ~/bin/sqlite3
```
I used the backup command like this:
```
/home/simon/bin/sqlite3 data.db "vacuum into '/tmp/backup.db'"
```
