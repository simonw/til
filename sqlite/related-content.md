# Related content with SQLite FTS and a Datasette template function

Today I added "related TILs" to this TIL website - so each TIL now shows five related TILs at the bottom of the page.

I'm generating the related content using a SQLite full-text search query.

## The related content query

I take the title and body text of an entry, strip out any non-alphanumeric characters, de-dupe the words, and then combine them to form a big OR search query.

I built an initial prototype of this using [an Observable notebook](https://observablehq.com/@simonw/turn-pasted-text-into-a-big-sqlite-fts-or-query) that generated these queries from pasted text. See also [my research issue](https://github.com/simonw/til/issues/50).

Here's a simple version of that query, using some example words pulled from [this entry](https://til.simonwillison.net/github-actions/postgresq-service-container). It executes against `til_fts` which is a SQLite FTS table [created](https://github.com/simonw/til/blob/cb62b8ab4c7b26ec7a895adea7f2d405b48686ba/build_database.py#L98-L100) using the `.enable_fts()` method of the [sqlite-utils Python library](https://sqlite-utils.datasette.io/en/stable/python-api.html#python-api-fts).
```sql
select title, rank from til_fts where til_fts match '
  i OR wanted OR to OR run OR some OR django OR tests OR using OR
  pytestdjango OR and OR with OR configured OR pick OR up OR the
  OR databaseurl OR environment OR variable OR via OR djdatabaseurl
  OR against OR a OR postgresql OR server OR running OR in OR
  github OR actions OR it OR took OR while OR figure OR out OR
  right OR pattern OR trick OR was OR define OR postgres OR service'
order by rank limit 5
```

Here are the results from [that query](https://til.simonwillison.net/tils?sql=select+title%2C+rank+from+til_fts+where+til_fts+match+%27%0D%0A++i+OR+wanted+OR+to+OR+run+OR+some+OR+django+OR+tests+OR+using+OR%0D%0A++pytestdjango+OR+and+OR+with+OR+configured+OR+pick+OR+up+OR+the%0D%0A++OR+databaseurl+OR+environment+OR+variable+OR+via+OR+djdatabaseurl%0D%0A++OR+against+OR+a+OR+postgresql+OR+server+OR+running+OR+in+OR%0D%0A++github+OR+actions+OR+it+OR+took+OR+while+OR+figure+OR+out+OR%0D%0A++right+OR+pattern+OR+trick+OR+was+OR+define+OR+postgres+OR+service%27%0D%0Aorder+by+rank+limit+5). Unsurprisingly the entry itself shows up first, but the other items look relevant enough to me:

title | rank
-- | --
Running tests against PostgreSQL in a service container | -61.04335068286244
Talking to a PostgreSQL service container from inside a Docker container | -37.54518907167069
Allowing a container in Docker Desktop for Mac to talk to a PostgreSQL server on the host machine | -29.712660785491842
Installing different PostgreSQL server versions in GitHub Actions | -27.738649522063493
Docker Compose for Django development | -25.027695483498224

The key trick here is the `order by rank` - SQLite FTS has a robust scoring mechanism built in, and it turns out it's good enough that simply feeding in all of the words from the entry and sorting by that rank provides good-enough related content results on its own.

## Improving the query

In order to display related content I need to do two additional things: I need to filter out the current entry, and I need to join against the `til` table in order to retrieve the information I want to display.

Here's the finished query:

```sql
select
  til.topic, til.slug, til.title, til.created
from
  til
  join til_fts on til.rowid = til_fts.rowid
where
  til_fts match :words
  and not (
    til.slug = :slug
    and til.topic = :topic
  )
order by
  til_fts.rank
limit
  5
```
And [an example of it running](https://til.simonwillison.net/tils?sql=select%0D%0A++til.topic%2C+til.slug%2C+til.title%2C+til.created%0D%0Afrom%0D%0A++til%0D%0A++join+til_fts+on+til.rowid+%3D+til_fts.rowid%0D%0Awhere%0D%0A++til_fts+match+%3Awords%0D%0A++and+not+(%0D%0A++++til.slug+%3D+%3Aslug%0D%0A++++and+til.topic+%3D+%3Atopic%0D%0A++)%0D%0Aorder+by%0D%0A++til_fts.rank%0D%0Alimit%0D%0A++5&words=i+OR+wanted+OR+to+OR+run+OR+some+OR+django+OR+tests+OR+using+OR+++pytestdjango+OR+and+OR+with+OR+configured+OR+pick+OR+up+OR+the+++OR+databaseurl+OR+environment+OR+variable+OR+via+OR+djdatabaseurl+++OR+against+OR+a+OR+postgresql+OR+server+OR+running+OR+in+OR+++github+OR+actions+OR+it+OR+took+OR+while+OR+figure+OR+out+OR+++right+OR+pattern+OR+trick+OR+was+OR+define+OR+postgres+OR+service&slug=postgresq-service-container&topic=github-actions), which returns the following:

topic | slug | title | created
-- | -- | -- | --
github-actions | service-containers-docker | Talking to a PostgreSQL service container from inside a Docker container | 2020-09-18T11:43:19-07:00
docker | docker-for-mac-container-to-postgresql-on-host | Allowing a container in Docker Desktop for Mac to talk to a PostgreSQL server on the host machine | 2022-03-31T22:48:17-07:00
github-actions | different-postgresql-versions | Installing different PostgreSQL server versions in GitHub Actions | 2021-07-05T17:43:13-07:00
docker | docker-compose-for-django-development | Docker Compose for Django development | 2021-05-24T22:08:23-07:00
django | just-with-django | Using just with Django | 2022-06-06T14:24:37-07:00

## Implementing this as a Datasette template function

I decided to implement this using a custom Jinja template function, added using a Datasette [one-off plugin](https://docs.datasette.io/en/stable/writing_plugins.html#writing-one-off-plugins).

The custom function is called `related_tils()`, and is called from the template [like this](https://github.com/simonw/til/blob/cb62b8ab4c7b26ec7a895adea7f2d405b48686ba/templates/pages/%7Btopic%7D/%7Bslug%7D.html#L37-L45):

```html+jinja
{% set related = related_tils(til) %}
{% if related %}
  <h3>Related</h3>
  <ul class="related">
    {% for til in related %}
    <li><span class="topic">{{ til.topic }}</span> <a href="/{{ til.topic }}/{{ til.slug }}">{{ til.title }}</a> - {{ til.created[:10] }}</li>
    {% endfor %}
  </ul>
{% endif %}
```
Here's the implementation of that custom template function. It's registered using the `extra_template_vars` Datasette plugin hook (described [here](https://docs.datasette.io/en/stable/plugin_hooks.html#extra-template-vars-template-database-table-columns-view-name-request-datasette)).

The function itself is an inner `async def` function, because it needs to be able to use `await` in order to execute its SQL query.

Jinja automatically awaits this kind of function when the template is rendered (see `enable_async=True` in [the Jinja documentation](https://jinja.palletsprojects.com/en/3.0.x/api/?highlight=enable_async#jinja2.Environment)).

So this function takes a TIL entry, creates a de-duped list of words from the title and body, uses that to construct and execute the SQL query and returns the results:

```python
@hookimpl
def extra_template_vars(request, datasette):
    async def related_tils(til):
        text = til["title"] + " " + til["body"]
        text = non_alphanumeric.sub(" ", text)
        text = multi_spaces.sub(" ", text)
        words = list(set(text.lower().strip().split()))
        sql = """
        select
          til.topic, til.slug, til.title, til.created
        from
          til
          join til_fts on til.rowid = til_fts.rowid
        where
          til_fts match :words
          and not (
            til.slug = :slug
            and til.topic = :topic
          )
        order by
          til_fts.rank
        limit
          5
        """
        result = await datasette.get_database().execute(
            sql,
            {"words": " OR ".join(words), "slug": til["slug"], "topic": til["topic"]},
        )
        return result.rows

    return {
        "related_tils": related_tils,
    }
```
Here's [the full code](https://github.com/simonw/til/blob/cb62b8ab4c7b26ec7a895adea7f2d405b48686ba/plugins/template_vars.py) for that plugin, which also registers some other template functions.
