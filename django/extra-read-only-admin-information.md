# Adding extra read-only information to a Django change page

I figured out this pattern today for adding templated extra blocks of information to the Django admin change page for an object.

It's really simply and incredibly useful. I can see myself using this a lot in the future.

```python
from django.contrib import admin
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from .models import Reporter


@admin.register(Reporter)
class ReporterAdmin(admin.ModelAdmin):
    # ...
    readonly_fields = ("recent_calls",)

    def recent_calls(self, instance):
        return mark_safe(
            render_to_string(
                "admin/_reporter_recent_calls.html",
                {
                    "reporter": instance,
                    "recent_calls": instance.call_reports.order_by("-created_at")[:20],
                    "call_count": instance.call_reports.count(),
                },
            )
        )
```

That's it! `recent_calls` is marked as a read-only field, then implemented as a method which returns HTML. That method passes the instance to a template using `render_to_string`. That template looks like this:

```html+jinja
<h2>{{ reporter }} has made {{ call_count }} call{{ call_count|pluralize }}</h2>

<p><strong>Recent calls</strong> (<a href="/admin/core/callreport/?reported_by__exact={{ reporter.id }}">view all</a>)</p>

{% for call in recent_calls %}
    <p><a href="/admin/core/location/{{ call.location.id }}/change/">{{ call.location }}</a> on {{ call.created_at }}</p>
{% endfor %}
```
