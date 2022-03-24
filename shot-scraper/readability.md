# Extracting web page content using Readability.js and shot-scraper

[Readability.js](https://github.com/mozilla/readability) is "A standalone version of the readability library used for Firefox Reader View".

My [shot-scraper](https://datasette.io/tools/shot-scraper) tool has a `shot-scraper javascript` command which can load a web page in a headless browser (via [Playwright](https://playwright.dev/)), execute JavaScript against that page and return the result to the console as JSON - see [Scraping web pages from the command line with shot-scraper](https://simonwillison.net/2022/Mar/14/scraping-web-pages-shot-scraper/).

I figured out how to use the two of these together to extract the core content from a web page using the command line.

Here's the recipe:

    shot-scraper javascript https://simonwillison.net/2022/Mar/24/datasette-061/ "
    async () => {
      const readability = await import('https://cdn.skypack.dev/@mozilla/readability');
      return (new readability.Readability(document)).parse();
    }"

It's using Skypack to [load the module](https://www.skypack.dev/view/@mozilla/readability). Playwright (the tech that powers `shot-scarper`) knows how to execute `async ()` functions and return their results.

This outputs the JSON structure created by Readability directly to the console.
```
% shot-scraper javascript https://simonwillison.net/2022/Mar/24/datasette-061/ "
    async () => {
      const readability = await import('https://cdn.skypack.dev/@mozilla/readability');
      return (new readability.Readability(document)).parse();
    }"
{
    "title": "Datasette 0.61: The annotated release notes",
    "byline": null,
    "dir": null,
    "lang": "en-gb",
    "content": "<div id=\"readability-page-1\" cla...
```
Piping to `jq keys` shows the keys in the returned object:
```
% shot-scraper javascript https://simonwillison.net/2022/Mar/24/datasette-061/ "
    async () => {
      const readability = await import('https://cdn.skypack.dev/@mozilla/readability');
      return (new readability.Readability(document)).parse();
    }" | jq keys
[
  "byline",
  "content",
  "dir",
  "excerpt",
  "lang",
  "length",
  "siteName",
  "textContent",
  "title"
]
```

To get just the text content, use `jq .textContent -r` (the `-r` returns the raw string, without the surrounding double quotes):
```
% shot-scraper javascript https://simonwillison.net/2022/Mar/24/datasette-061/ "
    async () => {
      const readability = await import('https://cdn.skypack.dev/@mozilla/readability');
      return (new readability.Readability(document)).parse();
    }" | jq .textContent -r
I released Datasette 0.61 this morning—closely followed by 0.61.1 to fix a minor bug.
Here are the annotated release notes.

In preparation for Datasette 1.0, this release includes ...
```
I can even pipe it directly into `sqlite-utils` to insert it into a SQLite database table:

```
% shot-scraper javascript https://simonwillison.net/2021/Oct/19/datasette-059/ "
async () => {    
  const readability = await import('https://cdn.skypack.dev/@mozilla/readability');
  return (new readability.Readability(document)).parse();
}" | sqlite-utils insert articles.db articles -
```

## Saving the script to a file

If you want to run this a lot, you can avoid copying-and-pasting it by saving it to a file called `readability.js`:

```javascript
async () => {    
  const readability = await import('https://cdn.skypack.dev/@mozilla/readability');
  return (new readability.Readability(document)).parse();
}
```

And then running:

    shot-scraper javascript https://til.simonwillison.net/shot-scraper/readability -i readability.js

Or even set that up as an alias, by adding the following to `~/.zshrc`:

    alias readability="shot-scraper javascript -i ~/readability.js"

Then restart a terminal window and run:

    readability https://til.simonwillison.net/shot-scraper/readability

## A note on safety

The [Readability.js README says](https://github.com/mozilla/readability/blob/0.4.1/README.md#security):

> If you're going to use Readability with untrusted input (whether in HTML or DOM form), we **strongly** recommend you use a sanitizer library like [DOMPurify](https://github.com/cure53/DOMPurify) to avoid script injection when you use the output of Readability.

It looks like DOMPurify could be executed against the output of Readability using the same import mechanism shown above.
