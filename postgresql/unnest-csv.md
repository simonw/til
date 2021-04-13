# Using unnest() to use a comma-separated string as the input to an IN query

[django-sql-dashboard](https://github.com/simonw/django-sql-dashboard) lets you define a SQL query plus one or more text inputs that the user can provide in order to execute the query.

I wanted the user to provide a comma-separated list of IDs which I would then use as input to a `WHERE column IN ...` query.

I figured out how to do that using the `unnest()` function and `regexp_split_to_array`:

```sql
select * from report where id in (select unnest(regexp_split_to_array(%(ids)s, ',')))
```

The `ids` string passed to this query is split on commas and used for the IN clause.

Here's a simple demo of how `unnest()` works:

```sql
select unnest(regexp_split_to_array('1,2,3', ','))
```
Output:

|unnest|
|------|
|1     |
|2     |
|3     |
