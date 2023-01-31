# Calculating embeddings with gtr-t5-large in Python

I've long wanted to run some kind of large language model on my own computer. Now that I have a M2 MacBook Pro I'm even more keen to find interesting ways to keep all of those CPU cores busy.

I got a tip from [this Twitter thread](https://twitter.com/john_lam/status/1620209726024978433) by John Lam that pointed me in the direction of the [gtr-t5-large](https://huggingface.co/sentence-transformers/gtr-t5-large) embeddings model:

> This is a sentence-transformers model: It maps sentences & paragraphs to a 768 dimensional dense vector space. The model was specifically trained for the task of sematic search.

I wrote about embeddings models like this in detail in [How to implement Q&A against your documentation with GPT3, embeddings and Datasette](https://simonwillison.net/2023/Jan/13/semantic-search-answers/).

My previous explorations of embeddings have used the [OpenAI embeddings API](https://platform.openai.com/docs/guides/embeddings). I'm pleased to report that the `gt5-t5-large` model runs on my laptop, and seems to provide solid usable results, at least for the task of finding similar content!

Here's how I used it:

## Install sentence-transformers

I ran this in a fresh Python 3.10 virtual environment:

    pip install sentence-transformers

I used [HTTPX](https://www.python-httpx.org/) and [FAISS](https://github.com/facebookresearch/faiss) later on, so let's get them now as well:

    pip install httpx faiss-cpu

## Download some data to embed

I decided to calculate embeddings against all of my blogmarks - short form bookmark entries I've posted to my blog. I've posted [6,465 of those](https://datasette.simonwillison.net/simonwillisonblog/blog_blogmark) dating back to November 2003.

I used the following script to fetch them as JSON from Datasette:

```python
import httpx

def get_blogmarks():
    url = "https://datasette.simonwillison.net/simonwillisonblog/blog_blogmark.json?_size=max&_shape=objects"
    while url:
        data = httpx.get(url, timeout=10).json()
        yield from data["rows"]
        url = data.get("next_url")
        print(url)

blogmarks = list(get_blogmarks())
```
For each one I need some text - I decided to concatenate the `link_title` and `commentary` fields together:
```python
texts = [
    bm["link_title"] + " " + bm["commentary"]
    for bm in blogmarks
]
```
And I need the IDs too, to look things up later:
```python
ids = [bm["id"] for bm in blogmarks]
```

## Load the model

The model can be loaded by name using the `SentenceTransformer` class:

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/gtr-t5-large")
```

The first time this runs takes a while because it has to download and cache the model.

Here's how to find the location of the cache:

```pycon
>>> from torch.hub import _get_torch_home
>>> _get_torch_home()
'/Users/simon/.cache/torch'
```
It's a 639MB file:
```zsh
% ls -lh /Users/simon/.cache/torch/sentence_transformers/sentence-transformers_gtr-t5-large \
  | awk '{print $5 "\t" $9}'

96B	1_Pooling
128B	2_Dense
1.9K	README.md
1.4K	config.json
122B	config_sentence_transformers.json
461B	modules.json
639M	pytorch_model.bin
53B	sentence_bert_config.json
1.7K	special_tokens_map.json
773K	spiece.model
1.3M	tokenizer.json
1.9K	tokenizer_config.json
```
With the model loaded, you can calculate embeddings like this:
```python
print(datetime.datetime.now().isoformat())
embeddings = model.encode(texts)
print(datetime.datetime.now().isoformat())
```
This took just over 3 minutes on my laptop, and I spotted it using up to 350% CPU in Activity Monitor (the machine has 12 CPUs so I didn't even notice it running).

I saved the embeddings to a file using this code - definitely not the most efficient way of saving them, the result was 105MB of JSON!

```python
with open("embeddings.json", "w") as fp:
    json.dump(
        {
            "ids": ids,
            "embeddings": [list(map(float, e)) for e in embeddings]
        },
        fp,
    )
```

## Finding similar content

The next step was to load those embeddings into a FAISS vector index. I copied code over from my [datasette-faiss plugin](https://datasette.io/plugins/datasette-faiss) for this.
```python
import faiss
import json
import numpy as np

data = json.load(open("embeddings.json"))

ids = data["ids"]

index = faiss.IndexFlatL2(len(data["embeddings"][0]))
index.add(np.array(data["embeddings"]))

def find_similar_for_id(id, k=10):
    idx = ids.index(id)
    embedding = data["embeddings"][idx]
    _, I = index.search(np.array([embedding]), k)
    # Now find the content IDs for the results
    return [ids[ix] for ix in I[0]]

# Example using id=6832
print(find_similar_for_id(6832))
```
This output:
```
[6832, 5545, 6843, 6838, 5573, 6510, 6985, 6957, 5714, 6840]
```
As expected, the first result was the blogmark itself.

Since I wanted to see the results in Datasette, I wrote this code to turn the above into a SQL query:
```python
def id_list_to_sql(ids):
    values = []
    for sort, id in enumerate(ids):
        values.append(f"({sort}, {id})")
    sql = """
    with results(sort, id) as (
    values
        {}
    )
    select
        results.sort,
        blog_blogmark.link_title,
        blog_blogmark.commentary
    from
        results
    join blog_blogmark on results.id = blog_blogmark.id
    """.format(", ".join(values))
    return sql
```
And now:
```pycon
>>> print(id_list_to_sql(find_similar_for_id(6832)))

    with results(sort, id) as (
    values
        (0, 6832), (1, 5545), (2, 6843), (3, 6838), (4, 5573), (5, 6510), (6, 6985), (7, 6957), (8, 5714), (9, 6840)
    )
    select
        results.sort,
        blog_blogmark.link_title,
        blog_blogmark.commentary
    from
        results
    join blog_blogmark on results.id = blog_blogmark.id
```
Here's [the result of running that SQL query](https://datasette.simonwillison.net/simonwillisonblog?sql=with+results%28sort%2C+id%29+as+%28%0D%0A++++values%0D%0A++++++++%280%2C+6832%29%2C+%281%2C+5545%29%2C+%282%2C+6843%29%2C+%283%2C+6838%29%2C+%284%2C+5573%29%2C+%285%2C+6510%29%2C+%286%2C+6985%29%2C+%287%2C+6957%29%2C+%288%2C+5714%29%2C+%289%2C+6840%29%0D%0A++++%29%0D%0A++++select%0D%0A++++++++results.sort%2C%0D%0A++++++++blog_blogmark.link_title%2C%0D%0A++++++++blog_blogmark.commentary%0D%0A++++from%0D%0A++++++++results%0D%0A++++join+blog_blogmark+on+results.id+%3D+blog_blogmark.id):

| sort | link_title | commentary |
| --- | --- | --- |
| 0 | Introducing sqlite-lines - a SQLite extension for reading files line-by-line | Alex Garcia wrote a brilliant C module for SQLIte which adds functions (and a table-valued function) for efficiently reading newline-delimited text into SQLite. When combined with SQLite's built-in JSON features this means you can read a huge newline-delimited JSON file into SQLite in a streaming fashion so it doesn't exhaust memory for a large file. Alex also compiled the extension to WebAssembly, and his post here is an Observable notebook post that lets you exercise the code directly. |
| 1 | How to compile and run the SQLite JSON1 extension on OS X | Thanks, Stack Overflow! I've been battling this one for a while - it turns out you can download the SQLite source bundle, compile just the json1.c file using gcc and load that extension in Python's sqlite3 module (or with Datasette's --load-extension= option) to gain access to the full suite of SQLite JSON functions - json(), json_extract() etc. |
| 2 | Introducing sqlite-http: A SQLite extension for making HTTP requests | Characteristically thoughtful SQLite extension from Alex, following his sqlite-html extension from a few days ago. sqlite-http lets you make HTTP requests from SQLite - both as a SQL function that returns a string, and as a table-valued SQL function that lets you independently access the body, headers and even the timing data for the request. This write-up is excellent: it provides interactive demos but also shows how additional SQLite extensions such as the new-to-me "define" extension can be combined with sqlite-http to create custom functions for parsing and processing HTML. |
| 3 | Introducing sqlite-html: query, parse, and generate HTML in SQLite | Another brilliant SQLite extension module from Alex Garcia, this time written in Go. sqlite-html adds a whole family of functions to SQLite for parsing and constructing HTML strings, built on the Go goquery and cascadia libraries. Once again, Alex uses an Observable notebook to describe the new features, with embedded interactive examples that are backed by a Datasette instance running in Fly. |
| 4 | How I made a Who's On First subset database | Inspired by Paul Ford on Twitter, I tried out a new trick with SQLite: connect to a database containing JSON, attach a brand new empty database file using "attach database", then populate it using INSERT INTO ... SELECT plus the json_extract() function to extract out a subset of the JSON properties into a new table in the new database. |

Pretty good results!
