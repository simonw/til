# PostgreSQL full-text search in the Django Admin

Django 3.1 introduces PostgreSQL `search_type="websearch"` - which gives you search with advanced operators like `"phrase search" -excluding`. James Turk [wrote about this here](https://jamesturk.net/posts/websearch-in-django-31/), and it's also in [my weeknotes](https://simonwillison.net/2020/Jul/23/datasette-copyable-datasette-insert-api/).

I decided to add it to my Django Admin interface. It was _really easy_ using the `get_search_results()` model admin method, [documented here](https://docs.djangoproject.com/en/3.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin.get_search_results).

My models already have a `search_document` full-text search column, as described in [Implementing faceted search with Django and PostgreSQL](https://simonwillison.net/2017/Oct/5/django-postgresql-faceted-search/). So all I needed to add to my `ModelAdmin` subclasses was this:

```python
    def get_search_results(self, request, queryset, search_term):
        if not search_term:
            return super().get_search_results(
                request, queryset, search_term
            )
        query = SearchQuery(search_term, search_type="websearch")
        rank = SearchRank(F("search_document"), query)
        queryset = (
            queryset
            .annotate(rank=rank)
            .filter(search_document=query)
            .order_by("-rank")
        )
        return queryset, False
```
Here's [the full implementation](https://github.com/simonw/simonwillisonblog/blob/6c0de9f9976ef831fe92106be662d77dfe80b32a/blog/admin.py) for my personal blog.
