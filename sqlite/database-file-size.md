# Calculating the size of a SQLite database file using SQL

I learned this trick today while [browsing the code](https://github.com/tersesystems/blacklite/blob/main/blacklite-core/src/main/resources/com/tersesystems/blacklite/resources.properties) of [Blacklite](https://tersesystems.com/blog/2020/11/26/queryable-logging-with-blacklite/), a neat Java library for writing diagnostic logs to a SQLite database.

To calculate the size in bytes of a SQLite database file using a SQL query, run this:
```sql
select page_size * page_count from pragma_page_count(), pragma_page_size();
```
I ran this against my `content.db` database and it returned:
```
21086208
```
And sure enough, `ls -l` confirms it:
```bash
ls -l content.db 
```
```
-rw-r--r--@ 1 simon  staff  21086208 Aug 15 09:24 content.db
```
It works using two [pragma function](https://www.sqlite.org/pragma.html). Explored using the `sqlite3 content.db` tool:

```
sqlite> .headers on
sqlite> select * from pragma_page_count();
page_count
5148
sqlite> select * from pragma_page_size();
page_size
4096
```
The `page_size` defaults to 4096 for most databases, but can be changed.

The `page_count` is the number of pages in the current file.

It turns out SQLiite databases are always an exact multiple of the `page_size`. So multiplying that by the page count gives the size of the database in bytes!

## Confirming that with awk

I got GPT-4 [to write me a shell script](https://chat.openai.com/share/9a123418-fdc1-4440-ba37-bd424436f947) to confirm that all of my `.db` files were a multiple of 4096:

```bash
find . \
  -name "*.db" \
  -exec stat -f "%z %N" {} \; | \
awk '{
  if ($1 % 4096 == 0) {
    print $2 " has size " $1 " which is a multiple of 4096"
  } else {
    print $2 " has size " $1 " which is NOT a multiple of 4096"
  }
}'
```
The output, truncated, looked like this:
```
./datasette-extract/content.db has size 21086208 which is a multiple of 4096
./sf-tree-history/tree-history-ord.db has size 288354304 which is a multiple of 4096
./sf-tree-history/tree-history.db has size 619749376 which is a multiple of 4096
./ca-fires-history/ca-fires.db has size 8364032 which is a multiple of 4096
./webvid-datasette/webvid.db has size 2692648960 which is a multiple of 4096
./cbsa-datasette/core.db has size 112439296 which is a multiple of 4096
./nicar-2023/nicar2023.db has size 978944 which is a multiple of 4096
...
./wedding/weddingsite/data.db has size 37888 which is NOT a multiple of 4096
```
And sure enough:
```
$ sqlite3 wedding/weddingsite/data.db
SQLite version 3.41.1 2023-03-10 12:13:52
Enter ".help" for usage hints.
sqlite> select * from pragma_page_size();
1024
```
That's a SQLite file created November 8th 2009, so presumably the default page size was smaller back then!
