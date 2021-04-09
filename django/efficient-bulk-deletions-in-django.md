# Efficient bulk deletions in Django

I needed to bulk-delete a large number of objects today. Django deletions are relatively inefficent by default, because Django implements its own version of cascading deletions and fires signals for each deleted object.

I knew that I wanted to avoid both of these and run a bulk `DELETE` SQL operation.

Django has an undocumented `queryset._raw_delete(db_connection)` method that can do this:

```python
reports_qs = Report.objects.filter(public_id__in=report_ids)
reports_qs._raw_delete(reports_qs.db)
```
But this failed for me, because my `Report` object has a many-to-many relationship with another table - and those records were not deleted.

I could have hand-crafted a PostgreSQL cascading delete here, but I instead decided to manually delete those many-to-many records first. Here's what that looked like:

```python
report_availability_tag_qs = (
    Report.availability_tags.through.objects.filter(
        report__public_id__in=report_ids
    )
)
report_availability_tag_qs._raw_delete(report_availability_tag_qs.db)
```
This didn't quite work either, because I have another model `Location` with foreign key references to those reports. So I added this:
```python
Location.objects.filter(latest_report__public_id__in=report_ids).update(
    latest_report=None
)
```
That combination worked! The Django debug toolbar confirmed that this executed one `UPDATE` followed by two efficient bulk `DELETE` operations.
