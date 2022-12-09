# Finding uses of an API with the new GitHub Code Search

The [GitHub Code Search beta](https://docs.github.com/en/search-github/github-code-search) is really powerful - it allows advanced search - including regular expression matches - against every public repo on GitHub.

It's still in a preview (December 2022) - you can [request access here](https://github.com/features/code-search-code-view/signup).

Today I used it to figure out who was using a specific internal API from Datasette that I'm considering changing for Datasette 1.0.

The API is the `permission_allowed(self, actor, action, resource=None, default=False)` method - it's intended to be used by plugins that need to check if a user has permission to perform a specific action.

I use it a lot in my own plugins, but I wanted to see if anyone else was using it for theirs.

After some [perusing of their documentation](https://docs.github.com/en/search-github/github-code-search/understanding-github-code-search-syntax) I came up with this:

`datasette permission_allowed -user:simonw -path:datasette/** -path:docs/** -path:tests/** language:python`

- `datasette permission_allowed` searches for files that use both of those terms. I could also have used `".permission_allowed("` to find things that are definitely method calls - or crafted a regular expression - but for this search just the keywords worked fine.
- `-user:simonw` filters out everything from my own repos - I write a lot of plugins that use this, but I didn't want to see those in the search results
- `-path:datasette/**` filters out anything in a file within a `datasette/` parent folder. Without this my search was returning results from forks of my own [simonw/datasette](https://github.com/simonw/datasette) repository, which I didn't want to see. I was hoping I could exclude `-repo:*/datasette` or similar but that's not currently supported.
- `-path:docs/** -path:tests/**` do the same thing but for mentions in `docs/` or `tests/` root dirctories.
- `language:python` restricts the results to Python files (presumably `.py` and `.ipynb` and similar).

If you have access to the beta you can [try that search here](https://cs.github.com/?scopeName=All+repos&scope=&q=datasette+permission_allowed+-user%3Asimonw+-path%3Adatasette%2F**+-path%3Adocs%2F**+-path%3Atests%2F**+language%3Apython).

See also my research notes [in this issue](https://github.com/simonw/datasette/issues/1939#issuecomment-1343734812).
