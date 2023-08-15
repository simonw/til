# Storing and serving related documents with openai-to-sqlite and embeddings

I decide to upgrade the related articles feature on my TILs site. Previously I calculated these [using full-text search](https://til.simonwillison.net/sqlite/related-content), but I wanted to try out a new trick using OpenAI embeddings for document similarity instead.

My [openai-to-sqlite](https://github.com/simonw/openai-to-sqlite) CLI tool already provides a mechanism for calculating embeddings against text and storing them in a SQLite database.

I was going to add a command for calculating similarity based on those embeddings... and then I saw that Benoit Delbosc had [opened a pull request](https://github.com/simonw/openai-to-sqlite/pull/9) implementing that feature already!

I took Benoit's work and [expanded it](https://github.com/simonw/openai-to-sqlite/issues/14). In particular, I added an option for saving the resulting calculations to a database table.

This meant I could find and then save related articles for my TILs by running the following:
```bash
wget https://s3.amazonaws.com/til.simonwillison.net/tils.db                                              
```
This grabs the latest `tils.db` used to serve my TIL website.
```bash
openai-to-sqlite embeddings tils.db \
  --sql 'select path, title, topic, body from til'
```
This retrieves and stores embeddings from the OpenAI API for every row in [my til table](https://til.simonwillison.net/tils/til) - embedding the `title`, `topic` and `body` columns concatenated together, then keying them against the `path` column (the primary key for that table).

The command output this:
```
Fetching embeddings  [####################################]  100%          
Total tokens used: 402500
```
402,500 tokens at [$0.0001 / 1K tokens](https://openai.com/pricing) comes to $0.04 - 4 cents!

Now that I've embedded everything, I can search for the most similar articles to a particular article like this:
```bash
openai-to-sqlite similar tils.db observable-plot_wider-tooltip-areas.md
```
Here are the results for that search for articles similar to <https://til.simonwillison.net/observable-plot/wider-tooltip-areas>:

```
observable-plot_wider-tooltip-areas.md
  0.860 observable-plot_histogram-with-tooltips.md
  0.792 svg_dynamic-line-chart.md
  0.791 javascript_copy-rich-text-to-clipboard.md
  0.780 javascript_dropdown-menu-with-details-summary.md
  0.772 vega_bar-chart-ordering.md
  0.770 javascript_working-around-nodevalue-size-limit.md
  0.769 presenting_stickies-for-workshop-links.md
  0.768 observable_jq-in-observable.md
  0.766 javascript_copy-button.md
  0.765 django_django-admin-horizontal-scroll.md
```
Or the top five as links:

- https://til.simonwillison.net/observable-plot/histogram-with-tooltips
- https://til.simonwillison.net/svg/dynamic-line-chart
- https://til.simonwillison.net/javascript/copy-rich-text-to-clipboard
- https://til.simonwillison.net/javascript/dropdown-menu-with-details-summary
- https://til.simonwillison.net/vega/bar-chart-ordering

These are pretty good matches!

## Calculating and storing the similarities

In order to build the related feature on my site, I wanted to store the calculations of the top ten articles most similar to each one.

The following command can do that:

```bash
time openai-to-sqlite similar tils.db --all --save
```
This runs against `--all` of the records in the embeddings table, and `--save` causes the results to be saved to the `similarities` table in the database.

The `time` command shows this took 27s! It has to run a LOT of cosine similarity calculations here - 446 * 446 = 198,916 calculations, and each of those is comparing two 1,536 dimension vectors.

Running `sqlite-utils schema tils.db` shows me the schema of the newly added tables:
```sql
CREATE TABLE [embeddings] (
   [id] TEXT PRIMARY KEY,
   [embedding] BLOB
);
CREATE TABLE [similarities] (
   [id] TEXT,
   [other_id] TEXT,
   [score] FLOAT,
   PRIMARY KEY ([id], [other_id])
);
```
Here's what that `similarities` table looks like:
```bash
sqlite-utils rows tils.db similarities --limit 5 -t --fmt github
```
| id                        | other_id                                   |    score |
|---------------------------|--------------------------------------------|----------|
| svg_dynamic-line-chart.md | observable-plot_wider-tooltip-areas.md     | 0.792374 |
| svg_dynamic-line-chart.md | observable-plot_histogram-with-tooltips.md | 0.771501 |
| svg_dynamic-line-chart.md | overture-maps_overture-maps-parquet.md     | 0.762345 |
| svg_dynamic-line-chart.md | javascript_openseadragon.md                | 0.762247 |
| svg_dynamic-line-chart.md | python_json-floating-point.md              | 0.7589   |

That's good enough to build the new feature!

## Automating this with GitHub Actions

My `tils.db` datase is built [by this workflow](https://github.com/simonw/til/blob/main/.github/workflows/build.yml).

I needed that workflow to embed all of the content, then run the similarity calculations and save them to the database.

The `openai-to-sqlite embeddings` command is smart enough not to run embeddings against content that has already been calculated, otherwise every time my GitHub Actions workflow runs I would be charged another 4 cents in OpenAI fees.

The catch is that `openai-to-sqlite similar tils.db --all --save` command. It takes 27s now, and will just get slower as my database continues to grow.

I added one more feature to `openai-to-sqlite` to help address this: the `recalculate-for-matches` option.

This lets you do the following:

```bash
openai-to-sqlite similar tils.db \
  svg_dynamic-line-chart.md \
  python_json-floating-point.md \
  --save --recalculate-for-matches
```
Here we are passing two specific IDs. The `--recalculate-for-matches` option means that the command will recalculate the similarity scores for those IDs, and then for every other row in the database that is a top-ten match for one of those IDs.

This should result in a lot less calculations than running against `--all`.

One more problem: how do I run against just the most recently modified articles in my workflow?

I decided to solve that with a bit of `git` magic, courtesy of some ChatGPT questions:

```bash
git diff --name-only HEAD~10
```
This outputs the names of the files that have changed in the last 10 commits:
```
README.md
cosmopolitan/ecosystem.md
github/django-postgresql-codespaces.md
jq/combined-github-release-notes.md
python/pyproject.md
```
I only care about the ones that are `something/something.md` - I can filter those using `grep`:
```bash
git diff --name-only HEAD~10 | grep '/.*\.md$'
```
Finally, my IDs are of the format `category_title.md` - so I can use `sed` to convert the filenames into IDs:
```bash
git diff --name-only HEAD~10 HEAD | grep '/.*\.md$' | sed 's/\//_/g'
```
Which outputs:
```
cosmopolitan_ecosystem.md
github_django-postgresql-codespaces.md
jq_combined-github-release-notes.md
python_pyproject.md
```
I can pass that to my `openai-to-sqlite similar --save` command like this:
```bash
openai-to-sqlite similar tils.db \
  $(git diff --name-only HEAD~10 HEAD | grep '/.*\.md$' | sed 's/\//_/g') \
  --save --recalculate-for-matches --print
```
The `--print` there causes the output to be shown too, for debugging purposes.

That's everything I need. Time to add it to the workflow.

## The GitHub Actions workflow

I needed to set my `OPENAI_API_KEY` as a repository secret in [simonw/til](https://github.com/simonw/til).

Here's the code I added to the workflow:
```yaml
- name: Calculate embeddings and document similarity
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: |-
    # Fetch embeddings for documents that need them
    openai-to-sqlite embeddings main/tils.db \
      --sql 'select path, title, topic, body from til'
    # Now calculate and save similarities
    if sqlite-utils rows main/tils.db similarities --limit 1; then
      # Table exists already, so only calculate new similarities
      openai-to-sqlite similar main/tils.db \
        $(git diff --name-only HEAD~10 HEAD | grep '/.*\.md$' | sed 's/\//_/g') \
        --save --recalculate-for-matches --print
    else
      # Table does not exist, calculate for everything
      openai-to-sqlite similar main/tils.db --all --save
    fi
```
A neat trick here is that it checks to see if the `similarities` table exists yet by running the `sqlite-utils rows tils.db similarities --limit 1` command and checking the exit code, which will be a failure if the table does not exist.

This workflow ran... and created the new tables in my database:

- <https://til.simonwillison.net/tils/similarities>
- <https://til.simonwillison.net/tils/embeddings>

## Hooking those into the templates

I figured out [the SQL query](https://til.simonwillison.net/tils?sql=select%0D%0A++til.topic%2C+til.slug%2C+til.title%2C+til.created%0D%0Afrom+til%0D%0Ajoin+similarities+on+til.path+%3D+similarities.other_id%0D%0Awhere+similarities.id+%3D+%27python_pyproject.md%27%0D%0Aorder+by+similarities.score+desc+limit+10) for returning the top related items for a story:
```sql
select
  til.topic, til.slug, til.title, til.created
from til
  join similarities on til.path = similarities.other_id
where similarities.id = 'python_pyproject.md'
order by similarities.score desc limit 10
```
Then I updated the existing `async def related_tils(til)` Python function in my code to use that:
```python
async def related_tils(til):
    path = til["path"]
    sql = """
    select
      til.topic, til.slug, til.title, til.created
    from til
      join similarities on til.path = similarities.other_id
    where similarities.id = :path
    order by similarities.score desc limit 10
    """
    result = await datasette.get_database().execute(
        sql,
        {"path": til["path"]},
    )
    return result.rows
```
... and it worked! All of my TILs now feature related articles powered by OpenAI embeddings.

Here's [my issue](https://github.com/simonw/til/issues/79) for this - though most of the notes are already in this TIL.
