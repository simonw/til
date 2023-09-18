# Embedding paragraphs from my blog with E5-large-v2

Xeophon [suggested](https://twitter.com/TheXeophon/status/1700203810545680542) that [E5-large-v2](https://huggingface.co/intfloat/e5-large-v2) as an embedding model that was worth a closer look.

It's an interesting model. It's trained to match queries against passages of text. You can generate embeddings for strings that look like this:

```
passage: As a general guideline, the CDC's average requirement of protein for women ages 19 to 70 is 46 grams per day. But, as you can see from this chart, you'll need to increase that if you're expecting or training for a marathon. Check out the chart below to see how much protein you should be eating each day.
passage: Definition of summit for English Language Learners. : 1  the highest point of a mountain : the top of a mountain. : 2  the highest level. : 3  a meeting or series of meetings between the leaders of two or more governments.
```
And then run an embedding on a query string like this:
```
query: how much protein should a female eat
```
And get back vectors from the `passage` embeddings that should help answer that query.

It's available in [sentence-transformers](https://www.sbert.net/) which means it should be easy to try out using my [llm-sentence-transformers](https://github.com/simonw/llm-sentence-transformers) plugin, described in [LLM now provides tools for working with embeddings](https://simonwillison.net/2023/Sep/4/llm-embeddings/).

## Setting up LLM

First, ensure LLM is installed:

```bash
brew install llm # or pip install llm / pipx install llm
```
Install my plugin:
```bash
llm install llm-sentence-transformers
```
Now we need the model. The `llm sentence-transformers register` command can both download it and register it with an alias for us:
```bash
llm sentence-transformers register intfloat/e5-large-v2 -a lv2
```
This downloaded a 2.5GB of model files and stored them in `~/.cache/torch/sentence_transformers/intfloat_e5-large-v`.

## Generating an embedding

To demonstrate that the model is working, run this:
```bash
llm embed -m lv2 -c 'passage: hello world'
```
This outputs a JSON array of 1024 floating point numbers - as counted like this:
```
llm embed -m lv2 -c 'passage: hello world' | jq length
```

## Embedding every paragraph on my blog

I decided to jump straight to something ambitious: generating `passage` embeddings for every paragraph on [my blog](https://simonwillison.net/).

The model truncates text at 512 tokens, so paragraphs sounded like they would be about the right length.

All of my blog content is stored as valid XHTML, which makes extracting paragraph content using a regular expression pretty simple.

I'm running [Django SQL Dashboard](https://django-sql-dashboard.datasette.io/) there, which makes it easy to run ad-hoc PostgreSQL queries and export the results as CSV.

I [fired up GPT-4](https://chat.openai.com/share/f1e34d52-0a20-4d29-bc05-a07a137f8f77) and used it to iterate my way to this SQL query:

```sql
-- This produces a row for every paragraph in every entry of my blog
WITH paragraphs AS (
    SELECT
        id,
        (regexp_matches(body, '<p>(.*?)<\/p>', 'gi'))[1] AS paragraph
    FROM
        blog_entry
),
-- Use row_number() to add a 0-based index to each paragraph, and
-- filter out any paragraphs that are empty after stripping out HTML tags
numbered_paragraphs AS (
    SELECT
        id,
        paragraph,
        row_number() OVER (PARTITION BY id) - 1 AS paragraphIndex
    FROM
        paragraphs
    WHERE
        LENGTH(TRIM(regexp_replace(paragraph, '<[^>]+>', '', 'gi'))) > 0
)
-- Compose the id-index IDs and strip any remaining HTML tags
SELECT
    id || '-' || paragraphIndex AS new_id,
    regexp_replace(paragraph, '<[^>]+>', '', 'gi') AS clean_paragraph
FROM
    numbered_paragraphs;
```

The `id` column has the ID of the blog entry, a hyphen, then the 0-based index of the paragraph within the entry. The `clean_paragraph` column has the paragraph text with HTML tags stripped out.

The output of that query looks like this:

id | clean_paragraph
-- | --
`1-0` | passage: The Web Standards project has launched Phase II.
`2-0` | passage: Blogging isn't nearly as easy as it looks. After several days hacking around in PHP (I'm far too proud to use an off the shelf solution) I find myself confronted with a blank slate, and writers block has taken hold. The toughest thing is working out what style to use in blog entries - my previous writing for the web has been primarily on forums (where posts do not have to stand on their own) or news sites where a formal, unopinionated tone is required. A blog should be informal but informative, with each post hopefully adding a new angle to the topic in hand. I'm sure it will get easier as I go along...
`4-0` | passage: Netscape 4 hit 5 years old yesterday. Scott Andrew celebrated this monumental occasion with a poetic tombstone tribute, entitled "1997 - 2002". The challenge now is to make this dream a reality - NS4 still has a stronghold in many corporate and institutional IT departments, as Zeldman bemoans in the first "opinion" of the new Web Standards project. An opinion that is notable in its absence of a permalink ;)
`5-0` | passage: One useful resource that did come out of the discussion was a link to Matthew Haughey's excellent tutorial on writing effective mailing list emails, which pays particular attention to the best way of quoting other posts.
`5-1` | passage: The Webdesign-L mailing list is ablaze with a huge, rambling, flamey thread about the relaunched Web Standards project. As with so many flames it has become quite difficut to work out what is being argued over and why (an issue compounded by the emergence of sub threads on everything from US law to how to upset a Canadian). I would provide links, but the list does not maintain a web accessible archive.
`5-2` | passage: I've been running my own campaign for web standards over on the WPWM forums with relatively unimpressive results.  This advocacy thing is harder than it looks.

I exported the whole result set as [this 4MB CSV file](https://gist.github.com/simonw/6b76f8780bcbb8f6ad7b8c9f0dce5392).

## Embedding and storing the paragraphs

The [llm embed-multi](https://llm.datasette.io/en/stable/embeddings/cli.html#embedding-data-from-a-csv-tsv-or-json-file) command is designed for ingesting exactly this kind of data. It wants a unique `id` column followed by one or more text columns, hence my SQL query above.

I ran it like this:
```bash
llm embed-multi blog-paragraphs -m lv2 \
  ~/Downloads/blog-paragraphs.csv --format csv --store
```
This creates a new collection of embeddings called `blog-paragraphs` using the E5-large-v2 embedding model. Then it reads through the CSV file and generates embeddings for each line. The `--store` line causes it to store the original text content in the database as well.

This took about 25 minutes to run (on an M2 Macbook Pro with 64GB of RAM). The result was an embeddings collection containing 18,918 rows.

Here's a query to preview three rows from that collection:
```bash
sqlite-utils "$(llm embed-db path)" '
  select id, content, length(embedding)
  from embeddings where collection_id = (
    select id from collections where name = "blog-paragraphs"
  ) limit 3
' --fmt github
```
| id   | content                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | length(embedding) |
|------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------|
| 1-0  | passage: The Web Standards project has launched Phase II.                                                                                                                                                                                                                                                                                                                                                                                                                                          |              4096 |
| 10-0 | passage: Some of his points seem overly picky, in particular the content-type issue. I checked a site Hixie mentions as sending the correct text/xml content-type header in NS4 and, as I suspected, NS4 popped up a "download" box and failed to render the page. I also checked out the W3's XHTML home page  - XHTML1.0 strict and a content-type header of text/html. His other points seem worth thinking about, but I would not consider any of them to significantly dilute WaSP's message. |              4096 |
| 10-1 | passage: So respect to Hixie for taking on the mantle of the ultimate standards advocate, but you can take a good thing too far.                                                                                                                                                                                                                                                                                                                                                                   |              4096 |

## Running similarity queries

The [llm similar](https://llm.datasette.io/en/stable/embeddings/cli.html#llm-similar) command runs a brute-force similarity calculation between the embedding of an input string and everything in the collection.

Remember, queries should start with `query:`.

Here's an example. I'm piping through `jq` because the default output format is newline-delimited JSON:

```bash
llm similar blog-paragraphs -c 'query: what is LLM?' | jq
```
I think the results are _really good_.
```json
{
  "id": "8287-18",
  "score": 0.8677400212244796,
  "content": "passage: LLM is my Python library and command-line tool for working with language models. I just released LLM 0.9 with a new set of features that extend LLM to provide tools for working with embeddings.",
  "metadata": null
}
{
  "id": "8276-12",
  "score": 0.8634046269968569,
  "content": "passage: LLM is my command-line utility and Python library for working with large language models such as GPT-4. I just released version 0.5 with a huge new feature: you can now install plugins that add support for additional models to the tool, including models that can run on your own hardware.",
  "metadata": null
}
{
  "id": "8246-1",
  "score": 0.855425605900991,
  "content": "passage: I built the first version of llm, a command-line tool for running prompts against large language model (currently just ChatGPT and GPT-4), getting the results back on the command-line and also storing the prompt and response in a SQLite database.",
  "metadata": null
}
{
  "id": "8254-28",
  "score": 0.8475920130027222,
  "content": "passage: Web LLM is a project from the same team as Web Stable Diffusion which runs the vicuna-7b-delta-v0 model in a browser, taking advantage of the brand new WebGPU API that just arrived in Chrome in beta.",
  "metadata": null
}
{
  "id": "8258-31",
  "score": 0.8371016271013721,
  "content": "passage: The Privileged LLM is the core of the AI assistant. It accepts input from trusted sources - primarily the user themselves - and acts on that input in various ways.",
  "metadata": null
}
{
  "id": "8244-3",
  "score": 0.8362997013999712,
  "content": "passage: If you ask an LLM a question, it will answer it - no matter what the question! Using them as an alternative to a search engine such as Google is one of the most obvious applications - and for a lot of queries this works just fine.",
  "metadata": null
}
{
  "id": "8281-194",
  "score": 0.8358538708058489,
  "content": "passage: LLMs are very good at returning format like JSON, which is really useful for writing code that uses them.",
  "metadata": null
}
{
  "id": "8263-48",
  "score": 0.8351871931158887,
  "content": "passage: The other LLM is the quarantined LLM, which is the one that's expected to go rogue. It's the one that reads emails, and it summarizes web pages, and all sorts of nastiness can get into it.",
  "metadata": null
}
{
  "id": "8281-180",
  "score": 0.8344018700424964,
  "content": "passage: LLM is a project I've been working on for a few months as a way of interacting with models.",
  "metadata": null
}
{
  "id": "8284-14",
  "score": 0.8333063676031358,
  "content": "passage: My LLM tool provides a CLI utility and Python library for running prompts through Large Language Models. I added plugin support to it a few weeks ago, so now it can support additional models through plugins - including a variety of models that can run directly on your own device.",
  "metadata": null
}
```

## Answering a question

I want to make this smoother, but for now here's a pipeline that can use this context to answer a question using Llama 2 13B run with my [llm-mlc](https://github.com/simonw/llm-mlc) plugin:
```bash
llm similar blog-paragraphs -c 'query: What is LLM?' \
  | jq .content \
  | llm -m mlc-chat-Llama-2-7b-chat-hf-q4f16_1 \
  'What is LLM?' -s 'You answer questions'
```
On my computer just now that output:

> Based on the given passages, LLM appears to be a tool or library for working with Large Language Models (LLMs) in Python. Here are some key points about LLM:
>
> 1. LLM is a Python library and command-line tool for working with LLMs.
> 2. The latest version of LLM (0.9) includes new features that extend its capabilities to work with embeddings.
> 3. LLM can install plugins that add support for additional models, including models that can run on your own hardware.
> 4. The first version of LLM was built as a command-line tool for running prompts against LLMs and storing the results in a SQLite database.
> 5. Web LLM is a project that runs the vicuna-7b-delta-v0 model in a browser, taking advantage of the new WebGPU API.
> 6. The Privileged LLM is the core of an AI assistant that accepts input from trusted sources and acts on that input.
> 7. LLMs are good at returning format like JSON, which is useful for writing code that uses them.
> 8. There are two types of LLMs: the regular LLM and the quarantined LLM, which is the one that's expected to go rogue.
> 9. LLM is a project that the author has been working on for a few months as a way of interacting with models.
> 10. The latest version of LLM (0.5) includes a huge new feature: the ability to install plugins that add support for additional models.

I turned that into a Bash script saved as `blog-answer.sh` (and added 'as a single paragraph') to the prompt):
```bash
#!/bin/bash

# Check if a query was provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 'Your query'"
    exit 1
fi

llm similar blog-paragraphs -c "query: $1" \
  | jq '.content | sub("passage: "; "")' -r \
  | llm -m mlc-chat-Llama-2-7b-chat-hf-q4f16_1 \
  "$1" -s 'You answer questions as a single paragraph'
```
Then:
```bash
./blog-answer.sh 'What is shot-scraper?'
```
Output:

> Shot-scraper is a Python utility that wraps Playwright, providing both a command line interface and a YAML-driven configuration flow for automating the process of taking screenshots of web pages and scraping data from them using JavaScript. It can be used to take one-off screenshots or take multiple screenshots in a repeatable way by defining them in a YAML file. Additionally, it can be used to execute JavaScript on a page and return the resulting value.

The `jq` expression I'm using looks like this:
```bash
jq '.content | sub("passage: "; "")' -r
```
The `-r` causes it not to include double quotes in the output - it just produces the raw strings.

The `sub("passage: "; "")` bit removes just the first occurence of the string `passage:` from the string, as demonstrated by:
```bash
echo '"passage: this is a passage: of text"' | jq 'sub("passage: "; "")'
```
Which outputs:
```json
"this is a passage: of text"
```
