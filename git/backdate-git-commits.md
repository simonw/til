# Back-dating Git commits based on file modification dates

I fell down a bit of a rabbit hole this morning. In trying to figure out [where the idea of celebrating World Wide Web Day on August 1st](https://simonwillison.net/2024/Aug/1/august-1st-world-wide-web-day/) came from I ran across Tim Berner-Lee's original code for the WorldWideWeb application for NeXT on the W3C's website:

https://www.w3.org/History/1991-WWW-NeXT/Implementation/

It's served up as a browseable Apache directory listing, but that's not the most delightful way to browse code - clicking a link to a `.m` file triggers a download, for example.

I decided to copy the code over to a GitHub repository, in order to browse it more easily with syntax highlighting and the like.

My end result is here: https://github.com/simonw/1991-WWW-NeXT-Implementation

![File system listing with 5 entries: folder 'Test' from 1990-12-20 (34 years ago), folder 'WorldWideWeb.app' from 1995-02-01 (30 years ago), file ',Features.html' from 1993-12-01 (31 years ago), files 'Anchor.h' and 'Anchor.m' both from 1991-09-04 (33 years ago); each row shows icon, name, 'Adding files from [DATE]'](https://github.com/user-attachments/assets/71a6c5d0-7ddf-48e7-8fb2-0e4032f3baf3)


## Fetching the code with wget

I started by using `wget` to grab the the code:

```bash
wget \
  --recursive \
  --no-parent \
  --no-host-directories \
  https://www.w3.org/History/1991-WWW-NeXT/Implementation/
```

This gave me a directory full of files... and to my delight they included the correct last modified dates, according to `ls -lah`:
```
-rw-r--r--   1 simon  wheel   1.5K Sep  4  1991 Anchor.h
-rw-r--r--   1 simon  wheel   8.1K Sep  4  1991 Anchor.m
-rw-r--r--   1 simon  wheel   3.6K Dec  1  1993 Bugs.html
-rw-r--r--   1 simon  wheel   7.7K Jun  2  1994 Features.html
```
I decided to attempt to mirror those dates in my new GitHub repository.

## Writing a script to back-date Git commits

Short version: to back-date Git commits you need to set the following environment variables before running `git commit`:

- `GIT_AUTHOR_DATE` - to a format like `2004-01-25 00:00:00`
- `GIT_COMMITTER_DATE` - same
- `GIT_AUTHOR_NAME`
- `GIT_AUTHOR_EMAIL`
- `GIT_COMMITTER_NAME`
- `GIT_COMMITTER_EMAIL`

I figured this out through asking [Claude](https://claude.ai/) to write me a script to rebuild my repo based on those last modified dates:

> I want to create a GitHub repository where I back-date files to when they were first created
>
> I have the files on my local disk like this:
>
> ```
> -rw-r--r--   1 simon  wheel   1.5K Sep  4  1991 Anchor.h
> -rw-r--r--   1 simon  wheel   8.1K Sep  4  1991 Anchor.m
> -rw-r--r--   1 simon  wheel   3.6K Dec  1  1993 Bugs.html
> ```
> Write me a Python script I can run which will group files by date and then do one grouped commit for each of those dates, backdated to the date (at 00:00), with an author that I pass to the script like this:
>
> `populate-git-repo-historically . --author "Simon Blah"`
>
> It should assume a .git repo is already there with nothing in it, it should print out the commit hash and backdated date for everything it commits

It gave me [this](https://claude.site/artifacts/6c4bb4e1-6bae-4d1e-8270-640c3b06f645), and I followed-up with:

> Problem: the script you wrote sets the commit date to now - I want the commit date to be backdated to the author date

Which got [this v2](https://claude.site/artifacts/6546a006-9e39-485b-9fde-7b98bf67420e) - almost right, but I made one more tweak:

> Set the committer to the same as the author

And that produced [a v3](https://claude.site/artifacts/d51a8003-a39b-48fb-99f0-8603c8cd1ed4) which ran correctly, but made a weird editorial choice to use `@example.com` in the commit messages. I fixed that and ended up with this script - all comments are by me:

```python
import os
import sys
import argparse
from datetime import datetime
from collections import defaultdict
import subprocess


def get_file_date(file_path):
    return datetime.fromtimestamp(os.path.getmtime(file_path)).date()


def group_files_by_date(directory):
    # I decided to group files edited on the same day in a single commit:
    grouped_files = defaultdict(list)
    for root, _, files in os.walk(directory):
        for file in files:
            if file.startswith("."):
                continue
            file_path = os.path.join(root, file)
            # I added this hack to skip the .git directory
            if ".git" in file_path:
                continue
            file_date = get_file_date(file_path)
            grouped_files[file_date].append(file_path)
    return grouped_files


def commit_files(files, date, author, author_email):
    print(files)
    for file in files:
        subprocess.run(["git", "add", file], check=True)

    commit_date = date.strftime("%Y-%m-%d 00:00:00")
    commit_message = f"Adding files from {date}"

    env = os.environ.copy()
    # Here'This is the most important bit: these environment variables are used
    # by Git to set the author and committer dates and names
    env["GIT_AUTHOR_DATE"] = commit_date
    env["GIT_COMMITTER_DATE"] = commit_date
    env["GIT_AUTHOR_NAME"] = author
    env["GIT_AUTHOR_EMAIL"] = author_email
    env["GIT_COMMITTER_NAME"] = author
    env["GIT_COMMITTER_EMAIL"] = author_email

    result = subprocess.run(
        ["git", "commit", "-m", commit_message],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )

    commit_hash = result.stdout.split()[1]
    return commit_hash


def main():
    parser = argparse.ArgumentParser(
        description="Populate Git repo with historical commits"
    )
    parser.add_argument("directory", help="Directory containing the files")
    parser.add_argument("--author", required=True, help="Author of the commits")
    # I added this option by hand:
    parser.add_argument("--email", required=True, help="Email of author")
    args = parser.parse_args()

    os.chdir(args.directory)

    if not os.path.exists(".git"):
        print(
            "Error: No .git directory found. Please initialize a Git repository first."
        )
        sys.exit(1)

    grouped_files = group_files_by_date(args.directory)

    for date, files in sorted(grouped_files.items()):
        commit_hash = commit_files(files, date, args.author, args.email)
        print(f"Commit: {commit_hash}, Date: {date}")


if __name__ == "__main__":
    main()
```
Then I saved it in `/tmp/populate.py` and ran it like this:
```bash
git init
python /tmp/populate.py . --author 'Tim Berners-Lee' --email 'tbl@none'
```
I iterated on this a bunch of times, each time running `rm -rf .git && git init` first to reset state.

## Pushing the result to GitHub

Once I was happy with the result (checked using `git log`) I pushed it to my repository on GitHub like this:
```bash
git remote add origin https://github.com/simonw/1991-WWW-NeXT-Implementation.git     
git branch -M main
git push -u origin main --force
```
The `--force` there replaces the existing `main` branch on GitHub entirely - useful for iterating on the script and then replacing the results.

Finally, I added the `README.md` file using the GitHub web interface.
