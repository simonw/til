# Using json_extract_path in PostgreSQL

The `json_extract_path()` function in PostgreSQL can be used to extract specific items from JSON - but I couldn't find documentation for the path language it uses.

It turns out it's a variadic functions - it takes multiple arguments, so the path you want is split into separate arguments.

I had data that looks like this (from [django-reversion](https://github.com/etianen/django-reversion)) in a column called `serialized_data`:

```json
[
    {
        "model": "core.location",
        "pk": 119,
        "fields": {
            "name": "Vista Community Clinic- The Gary Center, S. Harbour Blvd",
            "full_address": "201 S. Harbor Boulevard, \nLa Habra, CA 90631"
        }
    }
]
```
I wanted just that `full_address` value. Here's how I got it:
```sql
select
  object_id,
  content_type_id,
  json_extract_path(
    serialized_data::json,
    '0',
    'fields',
    'full_address'
  ) as full_address
from
  reversion_version
```
That's a path of `0`, `fields`, `full_address` - note that arrays are accessed by passing a string integer.

The `::json` casting operater is required here because my JSON isn't stored in a PostgreSQL `jsonb` column, it's stored in a regular text column.

Without the `::json` I got the following error:

> function json_extract_path(text, unknown, unknown, unknown) does not exist LINE 7: json_extract_path( ^ HINT: No function matches the given name and argument types. You might need to add explicit type casts. 
