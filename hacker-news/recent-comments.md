# How to read Hacker News threads with most recent comments first

[Hacker News](https://news.ycombinator.com/) displays comments in a tree. This can be frustrating if you want to keep track of a particular conversation, as you constantly have to seek through the tree to find the latest comment.

I solved this problem in three different ways today. I'll detail them in increasing orders of complexity (which frustratingly is the reverse order to how I figured them out!)

## The easiest way: Algolia search

The official Hacker News search uses Algolia, with a constantly updated index.

If you search for `story:35111646`, filter for comments and then order by date you'll get the comments for that particular story, most recent at the top. Problem solved!

Here's the URL - edit the story ID in that URL (or on the page) to view comments for a different story.

https://hn.algolia.com/?dateRange=all&page=0&prefix=false&query=story:35111646&sort=byDate&type=comment

<img width="1168" alt="Screenshot of those search results" src="https://user-images.githubusercontent.com/9599/224572085-d1e57f95-427c-4c62-9a2e-d2e8c4ab8f90.png">

## The Algolia search_by_date API

The Algolia Hacker News API is documented here: https://hn.algolia.com/api

Note that this is a separate system from the official Hacker News API, which is powered by Firebase, doesn't provide any search or filtering endpoints and is documented at https://github.com/HackerNews/API

To retrieve all comments on a specific story ordered by date, most recent first as JSON you can hit this endpoint:

https://hn.algolia.com/api/v1/search_by_date?tags=comment,story_35111646&hitsPerPage=1000

The `tags=` parameter does all of the work here - we're asking it for items of type `comment` that have been tagged with `story_35111646`.

This returns 20 results by default. I've added `&hitsPerPage=1000` to get back the maximum of 1,000.

This gives you back JSON, but how can we turn that into something that's more readable in our browser?

## Loading that into Datasette Lite

I'm going to use [Datasette Lite](https://lite.datasette.io/), my build of Datasette running directly in the browser using Python compiled to WebAssembly. More on [how that works here](https://simonwillison.net/2022/May/4/datasette-lite/).

This is possible because the Algolia API returns JSON with a `access-control-allow-origin: *` CORS header, allowing that data to be loaded by other web applications running on different domains.

If you pass Datasette Lite a `?json=` parameter with the URL to a JSON file that returns a list of objects, it will use [sqlite-utils](https://sqlite-utils.datasette.io/) to load that JSON into a SQLite table with a column for each of the keys in those objects.

This URL loads that data:

[https://lite.datasette.io/?json=https://hn.algolia.com/api/v1/search_by_date?tags=comment%2Cstory_35111646](https://lite.datasette.io/?json=https://hn.algolia.com/api/v1/search_by_date?tags=comment%2Cstory_35111646)

We can navigate to the `search_by_date` table to browse and filter the comments.

<img width="1168" alt="The search_by_date table in Datasette Lite" src="https://user-images.githubusercontent.com/9599/224572148-0088593f-45a0-4456-83c8-5294d391ce87.png">

Let's make some improvements to how it's displayed using a custom SQL query and some Datasette plugins.

Datasette Lite supports some Datasette plugins - you can add `?install=name-of-plugin` to the URL to install them directly from PyPI.

I'm going to load two plugins:

- [datasette-simple-html](https://datasette.io/plugins/datasette-simple-html) adds SQL functions for escaping and unescaping HTML text and stripping tags
- [datasette-json-html](https://datasette.io/plugins/datasette-json-html) provides a mechanism for outputting custom links in column results

Here's a URL that loads those two plugins:

https://lite.datasette.io/?install=datasette-simple-html&install=datasette-json-html&json=https://hn.algolia.com/api/v1/search_by_date?tags=comment%2Cstory_35111646%26hitsPerPage=1000

Now here's a custom SQL query that makes the comments a bit nicer to read when they are displayed by Datasette:

```sql
select
  created_at,
  author,
  html_unescape(
    html_strip_tags(comment_text)
  ) as text,
  parent_id,
  _tags
from
  search_by_date
order by
  created_at desc
```
[This link](https://lite.datasette.io/?install=datasette-simple-html&install=datasette-json-html&json=https://hn.algolia.com/api/v1/search_by_date?tags=comment%2Cstory_35111646%26hitsPerPage=100#/data?sql=select%0A++created_at%2C%0A++author%2C%0A++html_unescape%28%0A++++html_strip_tags%28comment_text%29%0A++%29+as+text%2C%0A++parent_id%2C%0A++_tags%0Afrom%0A++search_by_date%0Aorder+by%0A++created_at+desc) will execute that SQL query against the data in Datasette Lite.

One last trick: it would be neat if we could click through from the results to the comment on Hacker News. Here's how to add that, using a trick enabled by `datasette-json-html`:

```sql
select
  json_object(
    'label', objectID,
    'href', 'https://news.ycombinator.com/item?id=' || objectID
  ) as link,
  created_at,
  author,
  html_unescape(
    html_strip_tags(comment_text)
  ) as text,
  parent_id,
  _tags
from
  search_by_date
order by
  created_at desc
```
[See the results of that here](https://lite.datasette.io/?install=datasette-simple-html&install=datasette-json-html&json=https://hn.algolia.com/api/v1/search_by_date?tags=comment%2Cstory_35111646%26hitsPerPage=100#/data?sql=select%0A++json_object%28%0A++++%27label%27%2C+objectID%2C%0A++++%27href%27%2C+%27https%3A%2F%2Fnews.ycombinator.com%2Fitem%3Fid%3D%27+%7C%7C+objectID%0A++%29+as+link%2C%0A++created_at%2C%0A++author%2C%0A++html_unescape%28%0A++++html_strip_tags%28comment_text%29%0A++%29+as+text%2C%0A++parent_id%2C%0A++_tags%0Afrom%0A++search_by_date%0Aorder+by%0A++created_at+desc).

This adds link to each comment as the first column in the table.

It works by building a JSON string `{"label": "35123521", "href": "https://news.ycombinator.com/item?id=35123521"}` - the plugin then renders that as a link when the table is displayed, using Datasette's [render_cell()](https://docs.datasette.io/en/stable/plugin_hooks.html#render-cell-row-value-column-table-database-datasette) plugin hook.

<img width="1159" alt="SQL query results with a link in the first column" src="https://user-images.githubusercontent.com/9599/224572235-34986893-eafe-4e4b-9281-4abadee1b4f2.png">

## The most complicated solution, with json_tree()

My first attempt at solving this was by far the most complex.

Before I explored the `search_by_date` API I spotted that Algolia offers a `items` API, which returns ALL of the content for a thread in a giant nested JSON object:

https://hn.algolia.com/api/v1/items/35111646

Try that now and you'll see that the top level object has this shape `{"id": ..., "children": [...]}` - with that `"children" array containing a further nested array of objects representing the whole thread.

Datasette Lite's `?json=` parameter expects an array of objects. But... if you give it a top-level object which has a key that is itself an array of objects, it will load the objects from that array instead.

Which means passing it the above URL results in a table with a row for each of the top-level comments on that item... plus a `children` column with the JSON string of each of their descendents.

You can try that here:

https://lite.datasette.io/?json=https://hn.algolia.com/api/v1/items/35111646

SQLite has a [robust suite of JSON functions](https://www.sqlite.org/json1.html), plus the ability to execute recursive CTEs - surely it would be possible to write a query that flattens that nested structure into a table with a row for each comment?

I spent quite a bit of time on this. Eventually I realized that you don't even need a recursive CTE for this - you can use the `json_tree()` function provided by SQLite instead.

Here's the query I came up with:

```sql
with items as (select * from [35111646]),
results as (
select
  json_extract(value, '$.id') as id,
  json_extract(value, '$.created_at') as created_at,
  json_extract(value, '$.author') as author,
  html_strip_tags(html_unescape(json_extract(value, '$.text'))) as text,
  json_extract(value, '$.parent_id') as parent_id
from
  items, json_tree(items.children) tree
where
  tree.type = 'object'
union all
select id, created_at, author, html_strip_tags(html_unescape(text)) as text, parent_id
from items
)
select
  json_object('label', id, 'href', 'https://news.ycombinator.com/item?id=' || id) as link,
  *
from results order by created_at desc
```
[Try that out here](https://lite.datasette.io/?install=datasette-simple-html&install=datasette-json-html&json=https://hn.algolia.com/api/v1/items/35111646#/data?sql=with+items+as+%28select+*+from+%5B35111646%5D%29%2C%0Aresults+as+%28%0Aselect%0A++json_extract%28value%2C+%27%24.id%27%29+as+id%2C%0A++json_extract%28value%2C+%27%24.created_at%27%29+as+created_at%2C%0A++json_extract%28value%2C+%27%24.author%27%29+as+author%2C%0A++html_strip_tags%28html_unescape%28json_extract%28value%2C+%27%24.text%27%29%29%29+as+text%2C%0A++json_extract%28value%2C+%27%24.parent_id%27%29+as+parent_id%0Afrom%0A++items%2C+json_tree%28items.children%29+tree%0Awhere%0A++tree.type+%3D+%27object%27%0Aunion+all%0Aselect+id%2C+created_at%2C+author%2C+html_strip_tags%28html_unescape%28text%29%29+as+text%2C+parent_id%0Afrom+items%0A%29%0Aselect%0A++json_object%28%27label%27%2C+id%2C+%27href%27%2C+%27https%3A%2F%2Fnews.ycombinator.com%2Fitem%3Fid%3D%27+%7C%7C+id%29+as+link%2C%0A++*%0Afrom+results+order+by+created_at+desc).

<img width="1159" alt="That SQL query in Datasette Lite, returning a table of recent comments" src="https://user-images.githubusercontent.com/9599/224572313-6416fe2f-5260-4271-9f2b-fe9cb1724006.png">

The key to understanding the above is to understand how `json_tree()` works. Given a JSON value it returns a huge virtual table representing every node in that tree as a flat list.

Here's a simple example:

```sql
select * from json_tree('[
  {
    "id": 1,
    "name": "A",
    "children": [
      {
        "id": 2,
        "name": "B"
      }
    ]
  },
  {
    "id": 3,
    "name": "C"
  }
]')
```
[Try that against Datasette](https://latest.datasette.io/_memory?sql=select+*+from+json_tree(%27[%0D%0A++{%0D%0A++++%22id%22%3A+1%2C%0D%0A++++%22name%22%3A+%22A%22%2C%0D%0A++++%22children%22%3A+[%0D%0A++++++{%0D%0A++++++++%22id%22%3A+2%2C%0D%0A++++++++%22name%22%3A+%22B%22%0D%0A++++++}%0D%0A++++]%0D%0A++}%2C%0D%0A++{%0D%0A++++%22id%22%3A+3%2C%0D%0A++++%22name%22%3A+%22C%22%0D%0A++}%0D%0A]%27)). The output looks like this:

| key      | value                                                                                | type    | atom   |   id |   parent | fullkey               | path             |
|----------|--------------------------------------------------------------------------------------|---------|--------|------|----------|-----------------------|------------------|
|          | [{"id":1,"name":"A","children":[{"id":2,"name":"B"}]},{"id":3,"name":"C"}] | array   |        |    0 |          | $                     | $                |
| 0        | {"id":1,"name":"A","children":[{"id":2,"name":"B"}]}                           | object  |        |    1 |        0 | $[0]                  | $                |
| id       | 1                                                                                    | integer | 1      |    3 |        1 | $[0].id               | $[0]             |
| name     | A                                                                                | text    | A  |    5 |        1 | $[0].name             | $[0]             |
| children | [{"id":2,"name":"B"}]                                                              | array   |        |    7 |        1 | $[0].children         | $[0]             |
| 0        | {"id":2,"name":"B"}                                                                | object  |        |    8 |        7 | $[0].children[0]      | $[0].children    |
| id       | 2                                                                                    | integer | 2      |   10 |        8 | $[0].children[0].id   | $[0].children[0] |
| name     | B                                                                                  | text    | B    |   12 |        8 | $[0].children[0].name | $[0].children[0] |
| 1        | {"id":3,"name":"C"}                                                              | object  |        |   13 |        0 | $[1]                  | $                |
| id       | 3                                                                                    | integer | 3      |   15 |       13 | $[1].id               | $[1]             |
| name     | C                                                                                | text    | C  |   17 |       13 | $[1].name             | $[1]             |

This is pretty useful! The complex nested object has been flattened for us. Most of these rows aren't relevant... but if we filter for `type = 'object'` we can get hold of just the nested items within that structure that are complete JSON objects.

So that's what my bigger query does. I call `json_tree()` on the `children` column for each of those top level objects, then filter for `object` within that to get out the nested comments.

Then at the end I do a `union all` against the top level rows, to ensure they are included in the resulting table.

I was really happy with this query! And then I read a bit more of the Algolia API documentation and realized that it was entirely unneccessary for solving this problem. But I did at least get to learn how to use `json_tree()`.

## My original solution: hacker-news-to-sqlite

Prior to today I've solved this problem using my [hacker-news-to-sqlite](https://datasette.io/tools/hacker-news-to-sqlite) CLI tool instead.

This can suck all of the comments for a thread into a SQLite database, so you can sort them chronologically using [Datasette](https://datasette.io).

To run that command:

```
pipx install hacker-news-to-sqlite
hacker-news-to-sqlite trees comments.db 35111646
```
Then open it in Datasette (or [Datasette Desktop](https://datasette.io/desktop)):

```
datasette comments.db
```
`hacker-news-to-sqlite` uses the original Hacker News API, which means it has to fetch each comment in turn and then fetch any child comments as separate requests - so it takes a while to run!

I'm going to stick with the Algolia solution in the future.

