# Django Admin action for exporting selected rows as CSV

I wanted to add an action option to the Django Admin for exporting the currently selected set of rows (or every row in the table) as a CSV file.

I ended up using a pattern inspired by [this Django Snippet](https://djangosnippets.org/snippets/10767/), but with an added touch for more efficient exports. In order to avoid using up too much memory for the export, I use keyset pagination to fetch 500 rows at a time.

The `keyset_pagination_iterator()` helper function accepts any queryset, orders it by the primary key and then repeatedly fetches 500 items. It then modifies the queryset to add a `WHERE id > $last_seen_id` clause. This is a relatively inexpensive way to paginate, so having an endpoint perform that query dozens or even hundreds of times should hopefully avoid adding too much load to the database.

The action itself uses a pattern that combines `StringIO` and `csv.writer()` to stream out the results as a CSV file.

Django's `StreamingHttpResponse` mechanism is really neat: it accepts a Python iterator or generator and returns a streaming response derived from that sequence.

The Django documentation says "Streaming responses will tie a worker process for the entire duration of the response. This may result in poor performance" - this particular project runs on Google Cloud Run so I'm less concerned about tying up a worker than I would be normally, plus the export option is only available to trusted staff users with access to the Django Admin interface.

To add the CSV export option to a `ModelAdmin` subclass, do the following:

```python
from .admin_actions import export_as_csv_action

@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    actions = [export_as_csv_action()]
```
Here's `admin_actions.py`:
```python
import csv
from io import StringIO

from django.http import StreamingHttpResponse


def keyset_pagination_iterator(input_queryset, batch_size=500):
    all_queryset = input_queryset.order_by("pk")
    last_pk = None
    while True:
        queryset = all_queryset
        if last_pk is not None:
            queryset = all_queryset.filter(pk__gt=last_pk)
        queryset = queryset[:batch_size]
        for row in queryset:
            last_pk = row.pk
            yield row
        if not queryset:
            break


def export_as_csv_action(description="Export selected rows to CSV"):
    def export_as_csv(modeladmin, request, queryset):
        def rows(queryset):

            csvfile = StringIO()
            csvwriter = csv.writer(csvfile)
            columns = [field.name for field in modeladmin.model._meta.fields]

            def read_and_flush():
                csvfile.seek(0)
                data = csvfile.read()
                csvfile.seek(0)
                csvfile.truncate()
                return data

            header = False

            if not header:
                header = True
                csvwriter.writerow(columns)
                yield read_and_flush()

            for row in keyset_pagination_iterator(queryset):
                csvwriter.writerow(getattr(row, column) for column in columns)
                yield read_and_flush()

        response = StreamingHttpResponse(rows(queryset), content_type="text/csv")
        response["Content-Disposition"] = (
            "attachment; filename=%s.csv" % modeladmin.model.__name__
        )

        return response

    export_as_csv.short_description = description
    return export_as_csv
```
