# Read the Docs Search API

I stumbled across this API today: https://docs.datasette.io/_/api/v2/docsearch/?q=startup&project=datasette&version=stable&language=en

It's used by the search feature at https://docs.datasette.io/en/stable/search.html?q=startup&check_keywords=yes&area=default - I had assumed that feature was implemented in JavaScript (as is common in Sphinx world), but Read the Docs have upgraded it with their own backend search index.

It's built on Elasticsearch - they have developer docs for it here: https://github.com/readthedocs/readthedocs.org/blob/master/docs/development/search.rst

It looks like the key bits of the server-side implementation live here:

- https://github.com/readthedocs/readthedocs.org/blob/master/readthedocs/search/api.py
- https://github.com/readthedocs/readthedocs.org/blob/master/readthedocs/search/faceted_search.py
