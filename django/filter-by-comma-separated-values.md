# Filter by comma-separated values in the Django admin

I have a text column which contains comma-separated values - inherited from an older database schema.

I should refactor this into a many-to-many field (or maybe even a PostgreSQL array field), but I haven't done that yet. And I wanted to be able to filter by those values in the Django admin.

Since I'm using PostgreSQL, I decided to figure out how to do this using the PostgreSQL `regexp_split_to_array()` function.

There are two necessary SQL queries here: one to figure out all of the unique distinct values that are represented across all of those comma-separated lists, and one to filter for rows that include a specific value.

Here's what I came up with for the first:

```sql
select distinct unnest(
  regexp_split_to_array(my_column, ',\s*')
) from my_table
```
This uses `unnest()`, see [this TIL](https://til.simonwillison.net/postgresql/unnest-csv).

For filtering down to rows that contain a specific value in their comma-separated list, I figured out this:

```sql
select
  *
from
  my_table
where
  array_position(
    regexp_split_to_array(
      my_column, ',\s*'
    ),
    'MyValue'
  ) is not null
```
That second one, translated into the Django ORM, looks like this:
```python
from django.contrib.postgres.fields import ArrayField
from django.db.models import F, IntegerField, TextField, Value
from django.db.models.expressions import Func

queryset.annotate(
    value_array_position=Func(
        Func(
            F(my_column),
            Value(",\\s*"),
            function="regexp_split_to_array",
            output_field=ArrayField(TextField()),
        ),
        Value(my_value),
        function="array_position",
        output_field=IntegerField()
    )
).filter(value_array_position__isnull=False)
```
I didn't bother figuring out the ORM equivalent of that first `unnest()` SQL.

Here's the reusable admin filter factory I came up with using these:

```python
from django.contrib.admin import SimpleListFilter
from django.contrib.postgres.fields import ArrayField
from django.db import connection
from django.db.models import F, TextField, Value
from django.db.models.expressions import Func


def make_csv_filter(filter_title, filter_parameter_name, table, column):
    class CommaSeparatedValuesFilter(SimpleListFilter):
        title = filter_title
        parameter_name = filter_parameter_name

        def lookups(self, request, model_admin):
            sql = """
                select distinct unnest(
                    regexp_split_to_array({}, ',\\s*')
                ) from {}
            """.format(
                column, table
            )
            with connection.cursor() as cursor:
                cursor.execute(sql)
                values = [r[0] for r in cursor.fetchall() if r[0]]
            return zip(values, values)

        def queryset(self, request, queryset):
            value = self.value()
            if not value:
                return queryset
            else:
                return queryset.annotate(
                    value_array_position=Func(
                        Func(
                            F(column),
                            Value(",\\s*"),
                            function="regexp_split_to_array",
                            output_field=ArrayField(TextField()),
                        ),
                        Value(value),
                        function="array_position",
                        output_field=IntegerField()
                    )
                ).filter(value_array_position__isnull=False)

    return CommaSeparatedValuesFilter
```
Then you use it in a `ModelAdmin` subclass like this:
```python
@admin.register(Reporter)
class ReporterAdmin(admin.ModelAdmin):
    list_filter = (
        make_csv_filter(
            filter_title="Roles",
            filter_parameter_name="role",
            table="reporter",
            column="role_names",
        ),
    )
```
