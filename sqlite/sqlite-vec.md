# Using sqlite-vec with embeddings in sqlite-utils and Datasette

Alex Garcia's [sqlite-vec](https://github.com/asg017/sqlite-vec) SQLite extension provides a bunch of useful functions for working with vectors inside SQLite.

My LLM tool has features for [storing text embeddings in SQLite](https://llm.datasette.io/en/stable/embeddings/index.html).

It turns out `sqlite-vec` can work directly with the binary format that LLM uses to store embeddings ([described here](https://llm.datasette.io/en/stable/embeddings/storage.html)). That same format is also used by my slightly older [openai-to-sqlite](https://datasette.io/tools/openai-to-sqlite) tool.

## Installing sqlite-vec

A neat thing about `sqlite-vec` (and many of Alex's [other extensions](https://github.com/asg017/sqlite-ecosystem)) is that it's packaged as both a raw SQLite extension and as packages for various different platforms.

Alex makes Python plugins available for both [Datasette](https://datasette.io/) and [sqlite-utils](https://sqlite-utils.datasette.io/) which bundle that extension and register it with those tools such that the functions become available to SQL queries.

For Datasette:

```bash
datasette install datasette-sqlite-vec
```
For `sqlite-utils`:

```bash
sqlite-utils install sqlite-utils-sqlite-vec
```
Both of these commands will make the various `sqlite-vec` functions available within those tools. Test it like this:

```bash
sqlite-utils memory 'select vec_version()'
```
For me that outputs:
```json
[{"vec_version()": "v0.1.1"}]
```

For Datasette you can run that query using the Datasette web interface, or from the command-line like this:
```bash
datasette --get '/_memory.json?sql=select+vec_version()'
```
Or in Datasette 1.0a14 or higher:
```bash
datasette --get '/_memory/-/query.json?sql=select+vec_version()'
```
Returning:
```json
{"ok": true, "rows": [{"vec_version()": "v0.1.1"}], "truncated": false}
```
## Some example queries

My TIL website has an `embeddings` table that stores embeddings for each of the TILs. It has two columns: `id` is the text ID for the TIL, and `embedding` is the binary LLM embedding for that text.

Here's how to use the `sqlite-vec` `vec_distance_cosine()` function to find similar documents based on their embeddings:

```sql
with document_embedding as (
  select embedding as first_embedding from embeddings where id = :id
)
select
  id,
  vec_distance_cosine(embedding, first_embedding) as distance
from
  embeddings, document_embedding
order by distance limit 10
```
This accepts the `id` of a TIL and returns the 10 most similar TILs based on their embeddings. [Try it out here](
https://til.simonwillison.net/tils?sql=with+document_embedding+as+%28%0D%0A++select+embedding+as+first_embedding+from+embeddings+where+id+%3D+%3Aid%0D%0A%29%0D%0Aselect%0D%0A++id%2C%0D%0A++vec_distance_cosine%28embedding%2C+first_embedding%29+as+distance%0D%0Afrom%0D%0A++embeddings%2C+document_embedding%0D%0Aorder+by+distance+limit+10&id=observable-plot_histogram-with-tooltips.md).

Here's a more fun query that also explores the `vec_to_json()` function - which turns that binary format into a readable JSON array of floats - the `vec_slice()` function for returning a shorter slice of that array and the `vec_quantize_binary()` function for quantizing a vector to binary - returning a 1 for values >0 and a -1 for <0.

```sql
with document_embedding as (
  select embedding as first_embedding from embeddings where id = :id
)
select
  id,
  vec_distance_cosine(embedding, first_embedding) as distance,
  vec_to_json(vec_slice(embedding, 0, 3)) as first_3,
  vec_to_json(vec_quantize_binary(vec_slice(embedding, 0, 8))) as binary_8
from
  embeddings, document_embedding
order by distance limit 5
```
[Run that here](https://til.simonwillison.net/tils?sql=with+document_embedding+as+%28%0D%0A++select+embedding+as+first_embedding+from+embeddings+where+id+%3D+%3Aid%0D%0A%29%0D%0Aselect%0D%0A++id%2C%0D%0A++vec_distance_cosine%28embedding%2C+first_embedding%29+as+distance%2C%0D%0A++vec_to_json%28vec_slice%28embedding%2C+0%2C+3%29%29+as+first_3%2C%0D%0A++vec_to_json%28vec_quantize_binary%28vec_slice%28embedding%2C+0%2C+8%29%29%29+as+binary_8%0D%0Afrom%0D%0A++embeddings%2C+document_embedding%0D%0Aorder+by+distance+limit+5&id=observable-plot_histogram-with-tooltips.md). I get back these results:

id | distance | first_3 | binary_8
-- | -- | -- | --
observable-plot_histogram-with-tooltips.md | 0.0 | [-0.016882,-0.000301,0.009767] | [0,0,1,0,0,1,1,0]
observable-plot_wider-tooltip-areas.md | 0.14028826355934143 | [-0.000047,-0.005976,-0.007012] | [0,0,0,0,0,1,1,0]
vega_bar-chart-ordering.md | 0.22134298086166382 | [-0.004891,-0.006509,-0.005039] | [0,0,0,0,0,1,0,0]
svg_dynamic-line-chart.md | 0.2285003513097763 | [0.001713,-0.004975,0.010736] | [1,0,1,0,0,1,0,0]
javascript_copy-rich-text-to-clipboard.md | 0.2285047024488449 | [-0.022232,0.008316,-0.000267] | [0,1,0,0,0,1,0,0]


## Creating an index

`sqlite-vec` also includes the ability to create an index for a collection of vectors.

Here's how I created an index for my TILs. First, I created a virtual table using the `vec0` mechanism provided by `sqlite-vec` - I told it to store an `embedding` column that was an array of 1536 floats (the size of the OpenAI embeddings I've been using for my TILs):

```sql
create virtual table vec_tils using vec0(
  embedding float[1536]
);
```
Then I populated it like this:
```sql
insert into vec_tils(rowid, embedding)
  select rowid, embedding from embeddings;
```
`vec0` tables require an integer ID, so I used the `rowid` of the `embeddings` table. If I had my own numeric ID on that table I would use that instead.

Now I can run queries against this index like so:

```sql
with document_embedding as (
  select embedding as first_embedding from embeddings where id = :id
)
select
  (select id from embeddings where embeddings.rowid = vec_tils.rowid) as id,
  distance
from vec_tils, document_embedding
where embedding match first_embedding
and k = 5
order by distance;
```
[Try it here](https://til.simonwillison.net/tils?sql=with+document_embedding+as+%28%0D%0A++select+embedding+as+first_embedding+from+embeddings+where+id+%3D+%3Aid%0D%0A%29%0D%0Aselect%0D%0A++%28select+id+from+embeddings+where+embeddings.rowid+%3D+vec_tils.rowid%29+as+id%2C%0D%0A++distance%0D%0Afrom+vec_tils%2C+document_embedding%0D%0Awhere+embedding+match+first_embedding%0D%0Aand+k+%3D+5%0D%0Aorder+by+distance%3B&id=observable-plot_histogram-with-tooltips.md). I get back:


id | distance
-- | --
observable-plot_histogram-with-tooltips.md | 0.0
observable-plot_wider-tooltip-areas.md | 0.5296944379806519
vega_bar-chart-ordering.md | 0.6653465032577515
svg_dynamic-line-chart.md | 0.6760170459747314
javascript_copy-rich-text-to-clipboard.md | 0.6760244369506836

The `where embedding match first_embedding and k = 5` clause hooks into the magic of the underlying virtual table to run an efficient k-nearest-neighbors query against the index.

I'm using that `(select id from embeddings where embeddings.rowid = vec_tils.rowid) as id` trick to convert the numeric `rowid` into a human-readable `id` value by running a subquery against the `embeddings` table.

The `vec_tils` table is created for my TIL site by [this step](https://github.com/simonw/til/blob/e0dc31efcb41c9472681a8b1bb7a19993d4cb3f2/.github/workflows/build.yml#L82-L91) in my GitHub Actions workflow that deploys the application.
