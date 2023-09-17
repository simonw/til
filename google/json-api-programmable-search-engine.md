# Limited JSON API for Google searches using Programmable Search Engine

I figured out how to use a JSON API to run a very limited Google search today in a legit, non-screen-scraper way.

Google offer a product called [Programmable Search Engine](https://programmablesearchengine.google.com/), which used to be called [Google Custom Search](https://en.wikipedia.org/wiki/Google_Programmable_Search_Engine).

It's intended for creating a search engine for your own site, by restricting results to specific domains - but when you create one you can opt to search the whole web instead.

You can then use their [JSON API](https://developers.google.com/custom-search/v1/overview) to run searches.

It's quite limited:

- Maximum of 10 results per page, and you can only paginate up to 10 times so 100 results total
- 100 search queries per day for free, then $5 per 1000 queries up to 10,000 a day, then you have to switch to [a separate product](https://developers.google.com/custom-search/v1/site_restricted_api) that only works for up to 10 domains.

But it works! And it's pretty easy to get running.

First, create a new Programmable Search Engine [from the dashboard](https://programmablesearchengine.google.com/controlpanel/all). The [create page](https://programmablesearchengine.google.com/controlpanel/create) is pretty straight-forward:

<img width="637" alt="Screenshot of the create form - you basically just need to give it a name and solve a captcha" src="https://github.com/simonw/til/assets/9599/c6da044a-9b70-4cf0-845a-bcc7350d3bd4">

Now get an API key - I used the button in the middle [of the API documentation](https://developers.google.com/custom-search/v1/overview):

<img width="663" alt="A nice blue button for creating an API key" src="https://github.com/simonw/til/assets/9599/abb28f91-9e16-42b5-b087-cbd343dbc1cc">

You need the "Search engine ID" from the dashboard - mine was `84ec3c54dca9646ff`.

And that's it! You can combine the API key and search engine ID to run searches:

```
https://www.googleapis.com/customsearch/v1?key=API-KEY
  &cx=84ec3c54dca9646ff
  &q=SEARCH-TERM
``````

It seems to support a lot of the same search filters as Google. I tried using this, URL-encoded, and seemed to get the results I wanted:

    "powered by datasette" -site:github.com -site:simonwillison.net -site:datasette.io -site:pypi.org

The results come back as JSON that looks like this (truncated after the first result):

```json
{
  "kind": "customsearch#search",
  "url": {
    "type": "application/json",
    "template": "https://www.googleapis.com/customsearch/v1?q={searchTerms}&num={count?}&start={startIndex?}&lr={language?}&safe={safe?}&cx={cx?}&sort={sort?}&filter={filter?}&gl={gl?}&cr={cr?}&googlehost={googleHost?}&c2coff={disableCnTwTranslation?}&hq={hq?}&hl={hl?}&siteSearch={siteSearch?}&siteSearchFilter={siteSearchFilter?}&exactTerms={exactTerms?}&excludeTerms={excludeTerms?}&linkSite={linkSite?}&orTerms={orTerms?}&relatedSite={relatedSite?}&dateRestrict={dateRestrict?}&lowRange={lowRange?}&highRange={highRange?}&searchType={searchType}&fileType={fileType?}&rights={rights?}&imgSize={imgSize?}&imgType={imgType?}&imgColorType={imgColorType?}&imgDominantColor={imgDominantColor?}&alt=json"
  },
  "queries": {
    "request": [
      {
        "title": "Google Custom Search - \"powered by datasette\" -site:github.com -site:simonwillison.net -site:datasette.io -site:pypi.org",
        "totalResults": "65200",
        "searchTerms": "\"powered by datasette\" -site:github.com -site:simonwillison.net -site:datasette.io -site:pypi.org",
        "count": 10,
        "startIndex": 1,
        "inputEncoding": "utf8",
        "outputEncoding": "utf8",
        "safe": "off",
        "cx": "84ec3c54dca9646ff"
      }
    ],
    "nextPage": [
      {
        "title": "Google Custom Search - \"powered by datasette\" -site:github.com -site:simonwillison.net -site:datasette.io -site:pypi.org",
        "totalResults": "65200",
        "searchTerms": "\"powered by datasette\" -site:github.com -site:simonwillison.net -site:datasette.io -site:pypi.org",
        "count": 10,
        "startIndex": 11,
        "inputEncoding": "utf8",
        "outputEncoding": "utf8",
        "safe": "off",
        "cx": "84ec3c54dca9646ff"
      }
    ]
  },
  "context": {
    "title": "The whole web"
  },
  "searchInformation": {
    "searchTime": 0.25516,
    "formattedSearchTime": "0.26",
    "totalResults": "65200",
    "formattedTotalResults": "65,200"
  },
  "items": [
    {
      "kind": "customsearch#result",
      "title": "hhs",
      "htmlTitle": "hhs",
      "link": "https://hhscovid.publicaccountability.org/hhs",
      "displayLink": "hhscovid.publicaccountability.org",
      "snippet": "Powered by Datasette · Queries took 5.536ms · Data source: U.S. Department of Health & Human Services · Home · Name Search · Dataset Search · Browse Datasets.",
      "htmlSnippet": "<b>Powered by Datasette</b> · Queries took 5.536ms · Data source: U.S. Department of Health &amp; Human Services &middot; Home &middot; Name Search &middot; Dataset Search &middot; Browse Datasets.",
      "cacheId": "QbpCTHbMliYJ",
      "formattedUrl": "https://hhscovid.publicaccountability.org/hhs",
      "htmlFormattedUrl": "https://hhscovid.publicaccountability.org/hhs",
      "pagemap": {
        "metatags": [
          {
            "viewport": "width=device-width, initial-scale=1, shrink-to-fit=no"
          }
        ]
      }
    }
```

As a bonus, you can pipe results into a SQLite database using [sqlite-utils](https://sqlite-utils.datasette.io/) like this:

```bash
curl 'https://www.googleapis.com/customsearch...' | \
  jq .items | sqlite-utils insert /tmp/search.db search -   
```
