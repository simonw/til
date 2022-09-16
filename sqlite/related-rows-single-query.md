# Returning related rows in a single SQL query using JSON

When building database-backed applications you'll often find yourself wanting to return a row from the database along with its related rows.

A few examples:

- Retrieving a list of congressional legislators and their terms, following a foreign key relationship
- Return blog entries and their tags in one go, via a many-to-many table

You can do this in SQLite using the [json_group_array() aggregation function](https://sqlite.org/json1.html#jgrouparray). A couple of examples.

## Legislators and their terms, via a foreign key

Simplified schema for [this database](https://congress-legislators.datasettes.com/legislators):

```sql
CREATE TABLE [legislators] (
   [id] TEXT PRIMARY KEY,
   [name] TEXT,
   [bio_birthday] TEXT
);
CREATE TABLE [legislator_terms] (
   [legislator_id] TEXT REFERENCES [legislators]([id]),
   [type] TEXT,
   [state] TEXT,
   [start] TEXT,
   [end] TEXT,
   [party] TEXT
);
```
Here's a query that returns each legislator along with a JSON array of their terms:
```sql
select
  legislators.id,
  legislators.name,
  json_group_array(json_object(
    'type', legislator_terms.type,
    'state', legislator_terms.state,
    'start', legislator_terms.start,
    'end', legislator_terms.end,
    'party', legislator_terms.party
   )) as terms,
   count(*) as num_terms
from
  legislators join legislator_terms on legislator_terms.legislator_id = legislators.id
  group by legislators.id
order by
  id
limit
  10
```
And [the result](https://congress-legislators.datasettes.com/legislators?sql=select%0D%0A++legislators.id%2C%0D%0A++legislators.name%2C%0D%0A++json_group_array(json_object(%0D%0A++++%27type%27%2C+legislator_terms.type%2C%0D%0A++++%27state%27%2C+legislator_terms.state%2C%0D%0A++++%27start%27%2C+legislator_terms.start%2C%0D%0A++++%27end%27%2C+legislator_terms.end%2C%0D%0A++++%27party%27%2C+legislator_terms.party%0D%0A+++))+as+terms%2C%0D%0A+++count(*)+as+num_terms%0D%0Afrom%0D%0A++legislators+join+legislator_terms+on+legislator_terms.legislator_id+%3D+legislators.id%0D%0A++group+by+legislators.id%0D%0Aorder+by%0D%0A++id%0D%0Alimit%0D%0A++10):

<img width="593" alt="Screenshot of a query result. There is a terms column containing a JSON list of terms." src="https://user-images.githubusercontent.com/9599/190714817-4959daca-2450-4d28-9601-c7d59c02aa6e.png">

Note that this query does `group by legislators.id` which is allowed in SQLite but may not work in other databases, which might require `group by legislators.id, legislators.name` instead.

## Tags on blog entries, via a many-to-many table

Simplified schema:
```sql
CREATE TABLE [blog_entry] (
   [id] INTEGER PRIMARY KEY,
   [title] TEXT
);

CREATE TABLE [blog_tag] (
   [id] INTEGER PRIMARY KEY,
   [tag] TEXT
);

CREATE TABLE [blog_entry_tags] (
   [id] INTEGER PRIMARY KEY,
   [entry_id] INTEGER,
   [tag_id] INTEGER,
   FOREIGN KEY([entry_id]) REFERENCES [blog_entry]([id]),
   FOREIGN KEY([tag_id]) REFERENCES [blog_tag]([id])
);
```
Query to retrieve entries with their tags:
```sql
select
  blog_entry.id,
  blog_entry.title,
  json_group_array(json_object('tag', blog_tag.tag)) as tags
from
  blog_entry
  join blog_entry_tags on blog_entry.id = blog_entry_tags.entry_id
  join blog_tag on blog_tag.id = blog_entry_tags.tag_id
group by
  blog_entry.id
order by
  blog_entry.id desc
```
[Result](https://datasette.simonwillison.net/simonwillisonblog?sql=select+blog_entry.id%2C+blog_entry.title%2C+json_group_array(json_object(%27tag%27%2C+blog_tag.tag))+as+tags%0D%0Afrom+blog_entry+join+blog_entry_tags+on+blog_entry.id+%3D+blog_entry_tags.entry_id%0D%0Ajoin+blog_tag+on+blog_tag.id+%3D+blog_entry_tags.tag_id%0D%0Agroup+by+blog_entry.id%0D%0Aorder+by+blog_entry.id+desc):

| id | title | tags |
| --- | --- | --- |
| 8191 | I don't know how to solve prompt injection | [{"tag":"ai"},{"tag":"security"},{"tag":"openai"}] |
| 8190 | Weeknotes: Datasette Lite, s3-credentials, shot-scraper, datasette-edit-templates and more | [{"tag":"shotscraper"},{"tag":"datasette"},{"tag":"plugins"},{"tag":"datasettelite"},{"tag":"projects"},{"tag":"s3credentials"},{"tag":"weeknotes"}] |
| 8189 | Prompt injection attacks against GPT-3 | [{"tag":"ai"},{"tag":"gpt3"},{"tag":"security"},{"tag":"openai"}] |

There's a subtle bug in the above: if an entry has no tags at all it will be excluded from the query results entirely.

You can fix that using left joins like this:

```sql
select
  blog_entry.id,
  blog_entry.title,
  json_group_array(json_object('tag', blog_tag.tag)) as tags
from
  blog_entry
  left join blog_entry_tags on blog_entry.id = blog_entry_tags.entry_id
  left join blog_tag on blog_tag.id = blog_entry_tags.tag_id
where blog_entry.id < 4
group by
  blog_entry.id
order by
  blog_entry.id desc
```
This [outputs the following though](https://datasette.simonwillison.net/simonwillisonblog?sql=select%0D%0A++blog_entry.id%2C%0D%0A++blog_entry.title%2C%0D%0A++json_group_array(json_object(%27tag%27%2C+blog_tag.tag))+as+tags%0D%0Afrom%0D%0A++blog_entry%0D%0A++left+join+blog_entry_tags+on+blog_entry.id+%3D+blog_entry_tags.entry_id%0D%0A++left+join+blog_tag+on+blog_tag.id+%3D+blog_entry_tags.tag_id%0D%0Awhere+blog_entry.id+%3C+4%0D%0Agroup+by%0D%0A++blog_entry.id%0D%0Aorder+by%0D%0A++blog_entry.id+desc) - I have not yet figured out a good pattern to replace those `{"tag": null}` entries with an empty array:

| id | title | tags |
| --- | --- | --- |
| 3 | Todo list | [{"tag":null}] |
| 2 | Blogging aint easy | [{"tag":null}] |
| 1 | WaSP Phase II | [{"tag":null}] |

## Other databases

Other databases are capable of the same thing, but using different functions. PostgreSQL has [json_agg()](https://www.postgresql.org/docs/9.5/functions-aggregate.html) for example, which is also available in Django as [JSONBAgg](https://docs.djangoproject.com/en/4.1/ref/contrib/postgres/aggregates/#jsonbagg).
