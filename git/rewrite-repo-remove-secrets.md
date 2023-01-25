# Rewriting a Git repo to remove secrets from the history

I decided to make a GitHub repository public today that had previously been private. Unfortunately the revision history of that repository included some secret values, one of which I could not figure out a way to revoke.

I found a way to rewrite the entire repository from scratch to omit those values, using [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/) by Roberto Tyley. It's a tool that is recommended on the [GitHub help page](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository).

## Installing the tool

BFG is a Java app. My Mac had Java installed, so installing it was just a case of downloading the latest `.jar` file from the download link [on the website](https://rtyley.github.io/bfg-repo-cleaner/).

Running `java -jar bfg-1.14.0.jar` confirmed that this worked:

```
% java -jar bfg-1.14.0.jar   
bfg 1.14.0
Usage: bfg [options] [<repo>]
...
```

## Removing the secrets

I made a list of secret strings that I wanted to remove and saved them in a file called `secrets.txt`.

Then I followed the BFG instructions to create a fresh clone of my repository:

```
cd /tmp
git clone ~/Dropbox/Development/my-repo --mirror
```
This gave me a `/tmp/my-repo.git` folder containing the git history but not any actually checked out files.

Then I ran this:

```
cd /tmp/my-repo.git
java -jar /tmp/bfg-1.14.0.jar --replace-text /tmp/secrets.txt
```
I got the following output:
```
Using repo : /private/tmp/my-repo.git

Found 11 objects to protect
Found 3 commit-pointing refs : HEAD, refs/heads/main, refs/remotes/origin/main

Protected commits
-----------------

These are your protected commits, and so their contents will NOT be altered:

 * commit 6badd000 (protected by 'HEAD')

Cleaning
--------

Found 11 commits
Cleaning commits:       100% (11/11)
Cleaning commits completed in 98 ms.

Updating 2 Refs
---------------

	Ref                        Before     After   
	----------------------------------------------
	refs/heads/main          | 6badd000 | 15881e3b
	refs/remotes/origin/main | 4af64070 | d404ebd0

Updating references:    100% (2/2)
...Ref update completed in 35 ms.

Commit Tree-Dirt History
------------------------

	Earliest      Latest
	|                  |
	D D D D DD D D D D m

	D = dirty commits (file tree fixed)
	m = modified commits (commit message or parents changed)
	. = clean commits (no changes to file tree)

	                        Before     After   
	-------------------------------------------
	First modified commit | ff14c49c | be204284
	Last dirty commit     | 4af64070 | d404ebd0

Changed files
-------------

	Filename      Before & After                               
	-----------------------------------------------------------
	__init__.py | d5936659 ⇒ 121d236c, d96951be ⇒ ac125def, ...


In total, 30 object ids were changed. Full details are logged here:

	/private/tmp/my-repo.git.bfg-report/2023-01-24/17-11-55

BFG run is complete! When ready, run: git reflog expire --expire=now --all && git gc --prune=now --aggressive
```
And this had done the trick!

All of my commit hashes had changed, which was expected for a rewrite of the repository.

I knew that my first commit to the repo had a secret in it - so I ran `git log --pretty=oneline | tail -n 1` to find that first commit hash, then ran `git show be20428438bf42452f1a783d7b00dad84effc002` to see the commit... and sure enough it had this in it:

```diff
+            <p><label>JWT: <input name="jwt" value="***REMOVED***"></label></p>
```
That `***REMOVED***` used to be one of the secrets that I had wanted to removed.

## Final steps

As suggested in the output from the command, I ran this:

    git reflog expire --expire=now --all && git gc --prune=now

I didn't want to risk anything persisting on GitHub, so I deleted the entire repository and then created a new one with the same name. Then I pushed my repo to that:
```
git remote remove origin
git remote add origin git@github.com:simonw/my-repo.git
git push -u origin main
```
This was likely unnecessary: the GitHub documentation says that a force push should remove all traces of the old commits.
