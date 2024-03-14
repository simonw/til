# SQLite timestamps with floating point seconds

Today I learned about this:

```sql
select strftime('%Y-%m-%dT%H:%M:%f')
```
Which outputs:
```
2024-03-14T04:23:25.087Z
```
Note the seconds component which reads `25.087` - that's what you get from the `%f` format string.

This is useful because it provides a string which captures timestamp information at the millisecond level but can still be sorted alphabetically to sort by date.

I spotted this in [the SQL schema](https://github.com/maragudk/goqite/blob/main/schema.sql) for [goqite](https://github.com/maragudk/goqite) by Markus Wüstenberg, who uses it for recording `created` and `updated` timestamps:
```sql
create table goqite (
  id text primary key default ('m_' || lower(hex(randomblob(16)))),
  created text not null default (strftime('%Y-%m-%dT%H:%M:%fZ')),
  updated text not null default (strftime('%Y-%m-%dT%H:%M:%fZ')),
  queue text not null,
  body blob not null,
  timeout text not null default (strftime('%Y-%m-%dT%H:%M:%fZ')),
  received integer not null default 0
) strict;

create trigger goqite_updated_timestamp after update on goqite begin
  update goqite set updated = strftime('%Y-%m-%dT%H:%M:%fZ') where id = old.id;
end;
```
Another neat trick in that schema:
```sql
select lower(hex(randomblob(16)))
```
Which returns random strings like this one, suitable for use as IDs:
```
b4496695399120dfa999bff9981467b1
```
