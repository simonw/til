# Using git-filter-repo to set commit dates to author dates

After rebasing a branch with 60+ commits onto `main` I was disappointed to see that the commit dates on the commits (which are a different thing from the author dates) had all been reset to the same time. This meant the GitHub default UI for commits implied everything had been written at the same moment.

I fixed this using [git-filter-repo](https://github.com/newren/git-filter-repo) and a force push.

The best place to see `git-filter-repo` docs is [this user manual](https://htmlpreview.github.io/?https://github.com/newren/git-filter-repo/blob/docs/html/git-filter-repo.html).


## --commit-callback

The `git-filter-repo` tool has a number of options for callbacks which accept Python code:

```bash
git filter-repo --commit-callback 'python code goes here'
```

The [CALLBACKS](https://htmlpreview.github.io/?https://github.com/newren/git-filter-repo/blob/docs/html/git-filter-repo.html#CALLBACKS) documentation section is useful here.

Here's a callback which doesn't make any changes - it just prints debug output information for every commit:
```bash
git filter-repo --commit-callback '
    from pprint import pprint
    pprint(commit.__dict__)
    print("----")
'
```
When I ran that against my repo, each commit looked something like this:
```python
{'author_date': b'1689003276 -0700',
 'author_email': b'...@gmail.com',
 'author_name': b'Simon Willison',
 'branch': b'refs/heads/backup',
 'committer_date': b'1689003276 -0700',
 'committer_email': b'...@gmail.com',
 'committer_name': b'Simon Willison',
 'dumped': 0,
 'encoding': None,
 'file_changes': [<__main__.FileChange object at 0x1037d6b00>],
 'id': 172,
 'message': b'Show error for --continue mode, remove deleted code\n',
 'old_id': 172,
 'original_id': b'6cdbc7a27030f3235bda88cde122231f79ecf946',
 'parents': [171],
 'type': 'commit'}
```

## Fixing the commit dates

From those logs I figured out the date I didn't like was `b"1689003540 -0700"` - so I ran the following to update just those commits to have their commit date match their author date:

```bash
git filter-repo --commit-callback '
    if commit.committer_date == b"1689003540 -0700":
        commit.committer_date = commit.author_date
' --force
```
I needed the `--force` option because it complained about running against a not-completely-fresh-clone otherwise.

Having run this, the following command confirmed that the commit dates had now been updated on those commits:

```bash
git log --pretty=format:"%h - %an, %ad : Committer Date: %cd"
```
```
6cdbc7a - Simon Willison, Mon Jul 10 08:34:36 2023 -0700 : Committer Date: Mon Jul 10 08:34:36 2023 -0700
02a930d - Simon Willison, Mon Jul 10 08:31:50 2023 -0700 : Committer Date: Mon Jul 10 08:31:50 2023 -0700
a421aab - Simon Willison, Mon Jul 10 08:27:28 2023 -0700 : Committer Date: Mon Jul 10 08:27:28 2023 -0700
...
```
