# Enabling a gin index for faster LIKE queries

I tried using a gin index to speed up `LIKE '%term%'` queries against a column.

[PostgreSQL: More performance for LIKE and ILIKE statements](https://www.cybertec-postgresql.com/en/postgresql-more-performance-for-like-and-ilike-statements/) provided useful background. The raw-SQL way to do this is to install the extension like so:

```sql
CREATE EXTENSION pg_trgm;
```
And then create an index like this:
```sql
CREATE INDEX idx_gin ON mytable USING gin (mycolumn gin_trgm_ops);
```
This translates to two migrations in Django. The first, to enable the extension, looks like this:
```python
from django.contrib.postgres.operations import TrigramExtension
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0014_entry_custom_template"),
    ]

    operations = [TrigramExtension()]
```
Then to configure the index for a model you can add this to the model's `Meta` class:
```python
class Entry(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField()

    class Meta:
        indexes = [
            GinIndex(
                name="idx_blog_entry_body_gin",
                fields=["body"],
                opclasses=["gin_trgm_ops"],
            ),
        ]
```
The `opclasses=["gin_trgm_ops"]` line is necessary to have the same efect as the `CREATE INDEX` statement shown above. The `name=` option is required if you specify `opclasses`.

Run `./manage.py makemigrations` and Django will automatically create the correct migration to add the new index.

I ended up not shipping this for my blog because with less than 10,000 rows in the table it made no difference at all to my query performance.
