# How to almost get facet counts in the Django admin

For a tantalizing moment today I thought I'd found a recipe for adding facet counts to the Django admin.

I love faceted browsing. I've implemented it at least a dozen times in my career, using everything from Solr and Elasticsearch to PostgreSQL (see [Implementing faceted search with Django and PostgreSQL](https://simonwillison.net/2017/Oct/5/django-postgresql-faceted-search/)) or SQLite (see [Datasette Facets](https://simonwillison.net/2018/May/20/datasette-facets/)).

The Django admin almost has facets out of the box, thanks to the `list_filter` interface. But they're missing the all-imprtant count values! Those are the thing that makes faceted search so valuable to me. Today I decided to try and add them.

## Almost facet counts

Here's my first attempt. This assumes a model has a `State` foreign key, and adds faceting by state:

```python
class StateCountFilter(admin.SimpleListFilter):
    title = 'State count'
    parameter_name = 'state_count'

    def lookups(self, request, model_admin):
        qs = model_admin.get_queryset(request)
        states_and_counts = qs.values_list(
            "state__abbreviation", "state__name"
        ).annotate(n = Count('state__abbreviation'))
        for abbreviation, name, count in states_and_counts:
            yield abbreviation, '{}: {:,}'.format(name, count)

    def queryset(self, request, queryset):
        state = self.value()
        if state:
            return queryset.filter(
                state__abbreviation=state
            )

# Then add this to the ModelAdmin:

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_filter = (
        StateCountFilter,
    )
```
I tried this out, and for a glorious moment I thought I had solved it! I added it to another column too, and started trying it out.

<img width="1217" alt="110856792-eda4a000-826c-11eb-8f99-2676c1030423" src="https://user-images.githubusercontent.com/9599/110865748-f4391480-8278-11eb-90b4-a12b42f3c5de.png">

Then I attempted to apply one of the filters:

<img width="1190" alt="broken" src="https://user-images.githubusercontent.com/9599/110865785-074be480-8279-11eb-8d8f-b87cb3ba025a.png">

This is broken. The whole point of facet counts is that they show you counts for your existing selection - so you can filter down to the state of Oregon and see how many locations of type Pharmacy you have in that state.

But that wasn't happening here, because I was calculating the counts using `model_admin.get_queryset(request)` - which returns the unfiltered root queryset.

## Trying to get filtered counts

The challenge here is to get access to the currently filtered selection from within that `lookups()` method.

Here's the closest I got:

```python
    def lookups(self, request, model_admin):
        changelist = model_admin.get_changelist_instance(request)
        qs = changelist.get_queryset(request)
        states_and_counts = qs.values_list(
            "state__abbreviation", "state__name"
        ).annotate(n = Count('state__abbreviation'))
```
I tried this out... and hit a `RecursionError`! It turns out that `.get_changelist_instance()` method itself calls the `.lookups()` method, presumably because it needs those lookups in order to construct the current filtered selection (or to validate the request arguments perhaps).

I added `traceback.print_stack(limit=10)` to my `lookups()` method to confirm that I was right about this - here's the traceback:

```
  File "../site-packages/django/contrib/admin/sites.py", line 233, in inner
    return view(request, *args, **kwargs)
  File "../site-packages/django/utils/decorators.py", line 43, in _wrapper
    return bound_method(*args, **kwargs)
  File "../site-packages/django/utils/decorators.py", line 130, in _wrapped_view
    response = view_func(request, *args, **kwargs)
  File "../site-packages/django/contrib/admin/options.py", line 1693, in changelist_view
    cl = self.get_changelist_instance(request)
  File "../site-packages/django/contrib/admin/options.py", line 735, in get_changelist_instance
    return ChangeList(
  File "../site-packages/django/contrib/admin/views/main.py", line 99, in __init__
    self.queryset = self.get_queryset(request)
  File "../site-packages/django/contrib/admin/views/main.py", line 450, in get_queryset
    ) = self.get_filters(request)
  File "../site-packages/django/contrib/admin/views/main.py", line 137, in get_filters
    spec = list_filter(request, lookup_params, self.model, self.model_admin)
  File "../site-packages/django/contrib/admin/filters.py", line 79, in __init__
    self.lookup_choices = list(lookup_choices)
  File "core/admin.py", line 104, in lookups
    traceback.print_stack(limit=10)
```
I tried searching around to see if anyone else had solved this problem, but the best I could find was [this StackOverflow comment](https://stackoverflow.com/questions/28257979/how-to-access-the-filtered-queryset-in-django-admin-simplelistfilter#comment113524600_28258062) which hit the same recursion blocker that I found.

So as far as I can tell it isn't currently possible to implement facet counts correctly in a Django `SimpleListFilter.lookups()` method.

## Possible alternative: do it in JavaScript

I _really_ want facet counts. One workaround I'm considering is to do it in JavaScript: load the standard admin page, then have some custom JavaScript that hits a custom API endpoint with the current set of querystring parameters, fetches back filter and facet counts and injects them into the correct place on the page.

I really wish Django could handle this for me natively though!
