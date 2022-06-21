# Ordered group_concat() in SQLite

I was trying to use `group_concat()` to glue together some column values into a stiched together Markdown document. My first attempt looked like this:

```sql
select group_concat('## ' || chapter || '
                    
> ' || quote, '
                    
') from highlights order by timestamp
```

This attempt didn't work, because the order of the elements combined by a `group_concat()` [is undefined](https://www.sqlite.org/lang_aggfunc.html#group_concat):

> The group_concat() function returns a string which is the concatenation of all non-NULL values of X. If parameter Y is present then it is used as the separator between instances of X. A comma (",") is used as the separator if Y is omitted. **The order of the concatenated elements is arbitrary.**

It turns out you can fix this using a subselect:

```sql
select group_concat('## ' || chapter || '
                    
> ' || quote, '
                    
') from (select chapter, quote from highlights order by timestamp)
```
See [this explanation](https://sqlite.org/forum/forumpost/228bb96e12a746ce) by Keith Medcalf on the SQLite forum.

I think it may also be possible to solve this using Window functions. I tried doing this:
```sql
select group_concat('## ' || chapter || '
                    
> ' || quote, '
                    
') OVER (ORDER BY timestamp) from highlights
```
Which almost worked... but it returned one row for each row in `highlights`, each one with a growing combined result - the result I wanted was in the last returned row.
