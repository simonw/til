# git bisect

I extracted and enhanced this TIL from [my April 8th 2020 weeknotes](https://simonwillison.net/2020/Apr/8/weeknotes-zeit-now-v2/#git-bisect) to make it easier to find.

I fixed two bugs in Datasette using `git bisect run` - a tool which lets you run an automated binary search against a commit log to find the source of a bug.

Since I was figuring out a new tool, I fired up another GitHub issue self-conversation: in [issue #716](https://github.com/simonw/datasette/issues/716) I document my process of both learning to use `git bisect run` and using it to find a solution to that particular bug.

It worked great, so I used the same trick on [issue #689](https://github.com/simonw/datasette/issues/689) as well.

Watching `git bisect run` churn through 32 revisions in a few seconds and pinpoint the exact moment a bug was introduced is pretty delightful.

The first step is to tell it the range of commits that you want to search in, using `git bisect start`:
```
$ git bisect start main 0.34
Bisecting: 32 revisions left to test after this (roughly 5 steps)
[dc80e779a2e708b2685fc641df99e6aae9ad6f97] Handle scope path if it is a string
```
Then you provide a script that will return an error if the bug is present.

Usually you would use `pytest` or similar for this, but for the bug I was investigating here I wrote this custom script and saved it as `check_templates_considered.py`:

```python
import asyncio
import pathlib
from datasette.app import Datasette
import httpx

async def run_check():
    ds = Datasette([])
    async with httpx.AsyncClient(app=ds.app()) as client:
        response = await client.get("http://localhost/")
        assert 200 == response.status_code
        assert "Templates considered" in response.text

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_check())
```
This script will fail with an assertion error if `Templates considered` is not included in the HTML for the homepage.

To run the bisection, use `git bisect run <script goes here>`:
```
$ git bisect run python check_templates_considered.py
running python check_templates_considered.py
Traceback (most recent call last):
...
AssertionError
Bisecting: 15 revisions left to test after this (roughly 4 steps)
[7c6a9c35299f251f9abfb03fd8e85143e4361709] Better tests for prepare_connection() plugin hook, refs #678
running python check_templates_considered.py
Traceback (most recent call last):
...
AssertionError
Bisecting: 7 revisions left to test after this (roughly 3 steps)
[0091dfe3e5a3db94af8881038d3f1b8312bb857d] More reliable tie-break ordering for facet results
running python check_templates_considered.py
Traceback (most recent call last):
...
AssertionError
Bisecting: 3 revisions left to test after this (roughly 2 steps)
[ce12244037b60ba0202c814871218c1dab38d729] Release notes for 0.35
running python check_templates_considered.py
Traceback (most recent call last):
...
AssertionError
Bisecting: 1 revision left to test after this (roughly 1 step)
[70b915fb4bc214f9d064179f87671f8a378aa127] Datasette.render_template() method, closes #577
running python check_templates_considered.py
Traceback (most recent call last):
...
AssertionError
Bisecting: 0 revisions left to test after this (roughly 0 steps)
[286ed286b68793532c2a38436a08343b45cfbc91] geojson-to-sqlite
running python check_templates_considered.py
70b915fb4bc214f9d064179f87671f8a378aa127 is the first bad commit
commit 70b915fb4bc214f9d064179f87671f8a378aa127
Author: Simon Willison
Date:   Tue Feb 4 12:26:17 2020 -0800

    Datasette.render_template() method, closes #577

    Pull request #664.

:040000 040000 def9e31252e056845609de36c66d4320dd0c47f8 da19b7f8c26d50a4c05e5a7f05220b968429725c M	datasette
bisect run success
```
The final output shows exactly which commit introduced the bug. In this case it was [70b915fb4bc214f9d064179f87671f8a378aa127](https://github.com/simonw/datasette/commit/70b915fb4bc214f9d064179f87671f8a378aa127) (the "first bad commit").
