# Django data migration using a PostgreSQL CTE

I figured out how to use a PostgreSQL CTE as part of an update statement in a Django data migration. The trick here is mainly understanding how to combine CTEs with a PostgreSQL update - here's the pattern for that:

```sql
with something as (
  select id, created_at from ...
)
update mytable
  set
    created_at = something.created_at
  from
    something
  where
    mytable.id = something.id
```
Here's the full migration I wrote:
```python
from django.db import migrations

SQL = """
with created_at_by_reversion as (
  select
    location.id as id, min(date_created) as created_at
  from location
    join reversion_version on (location.id = reversion_version.object_id::integer and reversion_version.content_type_id = 18)
    join reversion_revision on reversion_revision.id = reversion_version.revision_id
  group by location.id
),
created_at_by_source_location as (
  select
    location.id as id, min(source_location.created_at) as created_at
  from source_location
    join location on source_location.matched_location_id = location.id
  group by location.id
),
new_created_at_for_locations as (
  select
    location.id,
    created_at_by_reversion.created_at as created_at_by_reversion,
    created_at_by_source_location.created_at as created_at_by_source_location,
    coalesce(created_at_by_reversion.created_at, created_at_by_source_location.created_at) as new_created_at
  from location
    left join created_at_by_source_location on created_at_by_source_location.id = location.id
    left join created_at_by_reversion on created_at_by_reversion.id = location.id
)
update location
  set
    created_at = new_created_at_for_locations.new_created_at
  from
    new_created_at_for_locations
  where
    location.id = new_created_at_for_locations.id
"""


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0132_location_created_at_created_by"),
    ]

    operations = [
        migrations.RunSQL(
            sql=SQL,
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
```
