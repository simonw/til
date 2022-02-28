# Crawling Datasette with Datasette

I wanted to add the new tutorials on https://datasette.io/tutorials to the search index that is used by the https://datasette.io/-/beta search engine.

To do this, I needed the content of those tutorials in a SQLite database table. But the tutorials are implemented as static pages in [templates/pages/tutorials](https://github.com/simonw/datasette.io/tree/9dffe361b0210b9d8b1f2fb820a3f2193f0f2fc7/templates/pages/tutorials) - so I needed to crawl that content and insert it into a table.

I ended up using a combination of the `datasette.client` mechanism ([documented here](https://docs.datasette.io/en/stable/internals.html#internals-datasette-client)), [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) and [sqlite-utils](https://sqlite-utils.readthedocs.io/) - all wrapped up in [a Python script](https://github.com/simonw/datasette.io/blob/9dffe361b0210b9d8b1f2fb820a3f2193f0f2fc7/index_tutorials.py) that's now called as part of [the GitHub Actions build process](https://github.com/simonw/datasette.io/blob/9dffe361b0210b9d8b1f2fb820a3f2193f0f2fc7/scripts/build.sh#L35) for the site.

I'm also using [configuration directory mode](https://docs.datasette.io/en/stable/settings.html#config-dir).

Here's the annotated script:

```python
import asyncio
from bs4 import BeautifulSoup as Soup
from datasette.app import Datasette
import pathlib
import sqlite_utils

# This is an async def function because it needs to call await ds.client
async def main():
    db = sqlite_utils.Database("content.db")
    # We need to simulate the full https://datasette.io/ site - including all
    # of its custom templates and plugins. On the command-line we would do this
    # by running "datasette ." - using configuration directory mode. This is
    # the equivalent of that when constructing the Datasette object directly:
    ds = Datasette(config_dir=pathlib.Path("."))
    # Equivalent of fetching the HTML from https://datasette.io/tutorials
    index_response = await ds.client.get("/tutorials")
    index_soup = Soup(index_response.text, "html5lib")
    # We want to crawl the links inside <div class="content"><ul>...<a href="">
    tutorial_links = index_soup.select(".content ul a")
    for link in tutorial_links:
        # For each one fetch the HTML, e.g. from /tutorials/learn-sql
        tutorial_response = await ds.client.get(link["href"])
        # The script should fail loudly if it encounters a broken link
        assert tutorial_response.status_code == 200
        # Now we can parse the page and extract the <h1> and <div class="content">
        soup = Soup(tutorial_response.text, "html5lib")
        # Beautiful Soup makes extracting text easy:
        title = soup.select("h1")[0].text
        body = soup.select(".content")[0].text
        # Insert this into the "tutorials" table, creating it if it does not exist
        db["tutorials"].insert(
            {
                "path": link["href"],
                "title": title,
                "body": body.strip(),
            },
            # Treat path, e.g. /tutorials/learn-sql, as the primary key
            pk="path",
            # This will over-write any existing records with the same path
            replace=True,
        )


if __name__ == "__main__":
    # This idiom executes the async function in an event loop:
    asyncio.run(main())
```
It's then added to the search index by this [Dogsheep Beta](https://datasette.io/tools/dogsheep-beta) search configuration [fragment](https://github.com/simonw/datasette.io/blob/9dffe361b0210b9d8b1f2fb820a3f2193f0f2fc7/templates/dogsheep-beta.yml#L209-L229):
```yaml
content.db:
    tutorials:
        sql: |-
            select
              path as key,
              title,
              body as search_1,
              1 as is_public
            from
              tutorials
        display_sql: |-
            select
              highlight(
                body, :q
              ) as snippet
            from
              tutorials
            where
              tutorials.path = :key
        display: |-
            <h3>Tutorial: <a href="{{ key }}">{{ title }}</a></h3>
            <p>{{ display.snippet|safe }}</p>
```
See [Building a search engine for datasette.io](https://simonwillison.net/2020/Dec/19/dogsheep-beta/) for more details on exactly how this works.
