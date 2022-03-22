# Rewriting a repo to contain the history of just specific files

I wanted to start a new git repository containing just the history of two specific files from my [help-scraper repository](https://github.com/simonw/help-scraper).

I started out planning to use `git filter-branch` for this, but got put off when [this StackOverflow thread](https://stackoverflow.com/questions/2982055/detach-many-subdirectories-into-a-new-separate-git-repository) started talking about the need to understand the differences between macOS `sed` and regular GNU `sed`.

That thread also pointed me to [git-filter-repo](https://github.com/newren/git-filter-repo), a really neat Python script that makes this *so much easier*.

## Installing git-filter-repo

`git-filter-repo` is written in Python but has zero dependencies on anything else - all you need to do is place the script somewhere on your path.

I ran `echo $PATH` to check which directories were on my path - one of them is `.local/bin` - so I decided to put it there:

    cd ~/.local/bin
    wget https://raw.githubusercontent.com/newren/git-filter-repo/main/git-filter-repo
    chmod 755 git-filter-repo

It didn't work until I ran `chmod 755` on it.

Now I can run this:

    % git filter-repo
    No arguments specified.

Confirming the new command is installed!

## Rewriting my repository

The `--path` option can be used to preserve just the history of specified paths. I ran this:

    cd /tmp
    git clone https://github.com/simonw/help-scraper
    cd help-scraper
    git filter-repo --path flyctl/fly.graphql --path github/github.graphql

The command output was:

    Parsed 132 commits
    New history written in 0.33 seconds; now repacking/cleaning...
    Repacking your repo and cleaning out old unneeded objects
    HEAD is now at 828a1efc GitHub: Tue Mar 22 15:09:04 UTC 2022
    Enumerating objects: 144, done.
    Counting objects: 100% (144/144), done.
    Delta compression using up to 12 threads
    Compressing objects: 100% (69/69), done.
    Writing objects: 100% (144/144), done.
    Total 144 (delta 34), reused 55 (delta 34), pack-reused 0
    Completely finished after 1.33 seconds.

And sure enough, my repo now only contains those two files:
```
% find . | grep -v .git
.
./flyctl
./flyctl/fly.graphql
```
And the commit history for those files:
```
% git log --stat --pretty=oneline | head -n 10
828a1efc4307cca6cd378c394c2d33eac2eceb52 GitHub: Tue Mar 22 15:09:04 UTC 2022
 github/github.graphql | 27 +++++++++++++++++++++++++++
 1 file changed, 27 insertions(+)
44fc9ebb49a255ad1c90f7761ab2ab1267135ff9 GitHub: Fri Mar 18 15:08:38 UTC 2022
 github/github.graphql | 1 +
 1 file changed, 1 insertion(+)
dae52d5b94761145333867bc6641e8210409c3b7 GitHub: Thu Mar 17 16:58:45 UTC 2022
 github/github.graphql | 3 +++
 1 file changed, 3 insertions(+)
33e0691bc579bb1e26ea6d05556cf047f5c120da GitHub: Wed Mar 16 15:05:35 UTC 2022
help-scraper % git log --stat --pretty=oneline | head -n 20
828a1efc4307cca6cd378c394c2d33eac2eceb52 GitHub: Tue Mar 22 15:09:04 UTC 2022
 github/github.graphql | 27 +++++++++++++++++++++++++++
 1 file changed, 27 insertions(+)
44fc9ebb49a255ad1c90f7761ab2ab1267135ff9 GitHub: Fri Mar 18 15:08:38 UTC 2022
 github/github.graphql | 1 +
 1 file changed, 1 insertion(+)
dae52d5b94761145333867bc6641e8210409c3b7 GitHub: Thu Mar 17 16:58:45 UTC 2022
 github/github.graphql | 3 +++
 1 file changed, 3 insertions(+)
33e0691bc579bb1e26ea6d05556cf047f5c120da GitHub: Wed Mar 16 15:05:35 UTC 2022
 github/github.graphql | 54 ++++++++++++++++++++++++++++++++++++++++++++++++---
 1 file changed, 51 insertions(+), 3 deletions(-)
3dae87045436c3a8c6c84409f9e7ec5ae3bfae74 GitHub: Tue Mar 15 15:08:59 UTC 2022
 github/github.graphql | 18 ++++++++++++++++++
 1 file changed, 18 insertions(+)
74a3f34c254f789948ee0257981f5d30a094d19f Fly: Tue Mar 15 06:23:03 UTC 2022
 flyctl/fly.graphql | 16 ++++++++++++++++
 1 file changed, 16 insertions(+)
63c92c60285b08a898b874b9296b28935f0e7ea8 GitHub: Mon Mar 14 15:09:42 UTC 2022
 github/github.graphql | 5 ++++-
```
