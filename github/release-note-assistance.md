# Assistance with release notes using GitHub Issues

I like to write the release notes for my projects by hand, but sometimes it can be useful to have some help along the way.

Today I figured out this recipe. First, find the last release tag and the commit hash of the most recent commit to `main`. For Datasette today that's:

- `1.0a13`
- `2ad51baa31bfba7940c739e99d4270f563a77290`

## Turning commits into a useful GitHub issues comment

Run the following command:
```bash
git log --pretty=format:"- %ad: %s %h" --reverse --date=short \
  1.0a13...2ad51baa31bfba7940c739e99d4270f563a77290
```
I added `| pbcopy` at the end to paste the result to my clipboard.

That gave me:

```
- 2024-03-12: Added two things I left out of the 1.0a13 release notes 8b6f155b
- 2024-03-15: Fix httpx warning about app=self.app, refs #2307 5af68377
- 2024-03-15: Fixed cookies= httpx warning, refs #2307 54f5604c
- 2024-03-15: Refactor duplicate code in DatasetteClient, closes #2307 eb8545c1
- 2024-03-15: Fix datetime.utcnow deprecation warning 261fc8d8
- 2024-03-17: Add ETag header for static responses (#2306) 67e66f36
- 2024-03-17: datasette-enrichments is example of row_actions da686627
- 2024-03-19: Docs for 100 max rows in an insert, closes #2310 1edb24f1
- 2024-03-21: z-index: 10000 on dropdown menu, closes #2311 19b6a373
- 2024-04-10: Typo fix triggera -> triggers d32176c5
- 2024-04-10: Fixed some typos spotted by Gemini Pro 1.5, closes #2318 63714cb2
- 2024-04-11: Async example for track_event hook 2a08ffed
- 2024-04-11: Include actor in track_event async example, refs #2319 7d6d471d
- 2024-04-22: datasette, not self.ds, in internals documentation 8f9509f0
- 2024-06-11: Move Metadata to `--internal` database e1bfab3f
- 2024-06-11: Only test first wheel, fixes surprise bug c698d008
- 2024-06-11: Fix for pyodide test failure, refs #2351 9a3c3bfc
- 2024-06-11: <html lang="en">, closes #2348 7437d40e
- 2024-06-11: Workaround for #2353 2b6bfdda
- 2024-06-12: Reminder about how to deploy a release branch 780deaa2
- 2024-06-12: Copy across release notes from 0.64.7 b39b01a8
- 2024-06-12: named_parameters(sql) sync function, refs #2354 d118d5c5
- 2024-06-12: Removed unnecessary comments, refs #2354 64a125b8
- 2024-06-13: Test against multiple SQLite versions (#2352) 8f86d2af
- 2024-06-13: xfail two flaky tests, #2355, #2356 45c27603
- 2024-06-13: Show response.text on test_upsert failure, refs #2356 93534fd3
- 2024-06-21: Do not show database name in Database Not Found error, refs #2359 62686114
- 2024-06-21: Fix for TableNotFound, refs #2359 7316dd4a
- 2024-06-21: Fix for RowNotFound, refs #2359 26378890
- 2024-06-21: Release notes for 0.64.8 on main c2e8e508
- 2024-07-02: Bump the python-packages group across 1 directory with 4 updates (#2362) 56adfff8
- 2024-07-15: Introduce new `/$DB/-/query` endpoint, soft replaces `/$DB?sql=...` (#2363) a23c2aee
- 2024-07-16: Use isolation_level=IMMEDIATE, refs #2358 2edf45b1
- 2024-07-25: Bump the python-packages group across 1 directory with 2 updates (#2371) feccfa2a
- 2024-07-26: /-/auth-token as root redirects to /, closes #2375 81b68a14
- 2024-08-05: Initial upgrade guide for v0.XX to v1 169ee5d7
- 2024-08-05: Tweaks and improvements to upgrade guide, refs ##2374 bd7d3bb7
- 2024-08-05: Move /db?sql= redirect to top of changes 2ad51baa
```
Because these are Markdown list items, pasting them into a comment on GitHub Issues causes them to render with the issue references AND the commits both expanded and converted into links, [like this](https://github.com/simonw/datasette/issues/2381#issuecomment-2269759462):

![ 2024-03-12: Added two things I left out of the 1.0a13 release notes 8b6f155 2024-03-15: Fix httpx warning about app=self.app, refs Fix httpx deprecation warnings #2307 5af6837 2024-03-15: Fixed cookies= httpx warning, refs Fix httpx deprecation warnings #2307 54f5604 2024-03-15: Refactor duplicate code in DatasetteClient, closes Fix httpx deprecation warnings #2307 eb8545c 2024-03-15: Fix datetime.utcnow deprecation warning 261fc8d 2024-03-17: Add ETag header for static responses (Add ETag header for static responses #2306) 67e66f3 2024-03-17: datasette-enrichments is example of row_actions da68662 2024-03-19: Docs for 100 max rows in an insert, closes Document maximum rows allowed per batch in JSON Write API #2310 1edb24f](https://github.com/user-attachments/assets/7b2d7403-c405-484b-a1f9-ea36ee99c2a7)

## LLM summary of the diff

Another trick I use is to take advantage of this GitHub URL that returns a list of commits between two points:

- https://github.com/simonw/datasette/compare/1.0a13...2ad51baa31bfba7940c739e99d4270f563a77290

Add `.diff` to that URL to get back a plain text diff representing all of those changes:

- https://github.com/simonw/datasette/compare/1.0a13...2ad51baa31bfba7940c739e99d4270f563a77290.diff

I then use my [LLM](https://llm.datasette.io/) tool to pipe that to a model such as Claude 3.5 Sonnet to generate a summary of the changes:

```bash
curl 'https://github.com/simonw/datasette/compare/1.0a13...2ad51baa31bfba7940c739e99d4270f563a77290.diff' \
  | llm -m claude-3.5-sonnet --system \
  'generate a short summary of these changes, then a bullet point list of detailed release notes'
```
I ran that just now and got the following:

> Here's a summary of the key changes in this diff:
> 
> 1. Removed metadata-related functionality and APIs, including the `/metadata.json` endpoint and `get_metadata()` plugin hook
> 2. Added new methods for getting and setting metadata at different levels (instance, database, resource, column)
> 3. Changed SQL query URL from `/database?sql=...` to `/database/-/query?sql=...`
> 4. Updated tests and internal logic to use the new metadata and query APIs
> 5. Added ETag support for static files
> 6. Minor UI and template updates
> 
> Detailed release notes:
> 
> - Removed `metadata.json` endpoint and related functionality
> - Added new async methods for getting/setting metadata:
>   - `get_instance_metadata()`, `set_instance_metadata()`
>   - `get_database_metadata()`, `set_database_metadata()`
>   - `get_resource_metadata()`, `set_resource_metadata()`
>   - `get_column_metadata()`, `set_column_metadata()`
> - Changed SQL query URL format to `/database/-/query?sql=...`
> - Removed `get_metadata()` plugin hook
> - Updated `derive_named_parameters()` to use regex instead of EXPLAIN
> - Added ETag support for static files to improve caching
> - Updated various tests to use new metadata and query APIs
> - Fixed CSRF protection for custom endpoints
> - Improved error messages for database/table not found errors
> - Added `lang="en"` attribute to HTML template
> - Updated Python and dependency versions in setup.py
> - Various minor bug fixes and code cleanup

I don't think this is good enough to publish, but it's a useful aid to help spot if I missed anything that wasn't captured by the earlier list of commit messages and issue references.

There's also at least one mistake in there: "Fixed CSRF protection for custom endpoints" isn't true, there were no changes made to CSRF protection in this set of commits, though one of them included documentation that was adjacent to a section about CSRF protection and hence was partially included in the diff.
