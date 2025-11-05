# Updating stable docs in ReadTheDocs without pushing a release

I use [ReadTheDocs](https://readthedocs.org/) for several of my projects. It's fantastic: among other things, it makes it easy to publish the documentation for my latest `main` branch at `/latest/` and the documentation for my latest release at `/stable/` (as well as maintain archived tag URLs for every prior release). 

I can then configure the main page of my project's documentation to redirect to `/stable/` by default.

I'm using ReadTheDocs for the following documentation sites:

- https://docs.datasette.io/
- https://sqlite-utils.datasette.io/
- https://llm.datasette.io/
- https://shot-scraper.datasette.io/

And quite a few more.

## The problem: typo fixes, project news and plugins

There's a catch: by default, the only way to update the `/stable/` documentation is to ship a new release.

In the past, I've shipped `x.x.1` version bumps just to get new documentation published to ReadTheDocs!

This isn't great though, especially now I have some of my packages in Homebrew. Shipping a release of Datasette or `sqlite-utils` or LLM means the Homebrew formula has to be updated by someone too, which feels like a waste of time and effort if the only change was to the documentation.

Another challenge is that there are things I want to include in my documentation that aren't actually coupled to releases. Project news is one example, but a better one is plugin listings: when a new plugin is released I'd like to include it in the official documentation, but it's not a code change that justifies pushing a new release.

## The shape of the solution

What I really want is a way to trigger and publish a new build of the `/stable/` documentation on ReadTheDocs without having to ship a new release.

After some [extensive experimentation](https://github.com/simonw/simonw-readthedocs-experiments/issues/1) (that's an issue thread with 43 comments, all by me) I've found a solution.

The basic shape is this: rather than having ReadTheDocs serve `/stable/` from the latest tagged release of my project, I instead maintain a `stable` branch in the GitHub repository. It's this branch that becomes the default documentation on my documentation sites.

Then I use GitHub Actions to automate the process of updating that branch. In particular:

- Any time I tag and push a new release, the `stable` branch is entirely updated to reflect the content of that release. Any changes in that branch are discarded.
- But... I can make edits to that branch myself in between releases. Those edits will be wiped out at the next release, so I need to be sure to apply them to the `main` branch as well.
- I also have a shortcut: any time I commit to `main` I can include the text `!stable-docs` in my commit message. If I do that, GitHub Actions will copy the exact content of any files in the `docs/` directory that were modified in that commit and use them to update the `stable` branch, then publish that branch with those new changes.

For general usage I only have to do two things: continue to ship releases, and occasionally include `!stable-docs` in a commit that updates a document which I'd like to be reflected instantly on the documentation site (a typo fix, project news or new plugin for example).

## The GitHub Actions workflow

Here's the full `.github/workflows/stable-docs.yml` workflow file I built to implement this process:

```yaml
name: Update Stable Docs

on:
  release:
    types: [published]
  push:
    branches:
    - main

permissions:
  contents: write

jobs:
  update_stable_docs:
    runs-on: ubuntu-latest
    steps:
    - name: Checkout repository
      uses: actions/checkout@v3
      with:
        fetch-depth: 0  # We need all commits to find docs/ changes
    - name: Set up Git user
      run: |
        git config user.name "Automated"
        git config user.email "actions@users.noreply.github.com"
    - name: Create stable branch if it does not yet exist
      run: |
        if ! git ls-remote --heads origin stable | grep stable; then
          git checkout -b stable
          # If there are any releases, copy docs/ in from most recent
          LATEST_RELEASE=$(git tag | sort -Vr | head -n1)
          if [ -n "$LATEST_RELEASE" ]; then
            rm -rf docs/
            git checkout $LATEST_RELEASE -- docs/
          fi
          git commit -m "Populate docs/ from $LATEST_RELEASE" || echo "No changes"
          git push -u origin stable
        fi
    - name: Handle Release
      if: github.event_name == 'release'
      run: |
        git fetch --all
        git checkout stable
        git reset --hard ${GITHUB_REF#refs/tags/}
        git push origin stable --force
    - name: Handle Commit to Main
      if: contains(github.event.head_commit.message, '!stable-docs')
      run: |
        git fetch origin
        git checkout -b stable origin/stable
        # Get the list of modified files in docs/ from the current commit
        FILES=$(git diff-tree --no-commit-id --name-only -r ${{ github.sha }} -- docs/)
        # Check if the list of files is non-empty
        if [[ -n "$FILES" ]]; then
          # Checkout those files to the stable branch to over-write with their contents
          for FILE in $FILES; do
            git checkout ${{ github.sha }} -- $FILE
          done
          git add docs/
          git commit -m "Doc changes from ${{ github.sha }}"
          git push origin stable
        else
          echo "No changes to docs/ in this commit."
          exit 0
        fi
```
There are three interesting step blocks here.

### Creating the stable branch

The first block is there purely to create that `stable` branch if it does not exist yet. This means I can drop the above workflow into a new project without having to do any additional setup against the repo:

```yaml
    - name: Create stable branch if it does not yet exist
      run: |
        if ! git ls-remote --heads origin stable | grep stable; then
          git checkout -b stable
          # If there are any releases, copy docs/ in from most recent
          LATEST_RELEASE=$(git tag | sort -Vr | head -n1)
          if [ -n "$LATEST_RELEASE" ]; then
            rm -rf docs/
            git checkout $LATEST_RELEASE -- docs/
          fi
          git commit -m "Populate docs/ from $LATEST_RELEASE" || echo "No changes"
          git push -u origin stable
        fi
```
There's another trick in there though. When I add this workflow to a new repository I'm fine for that `stable` branch to start off directly reflecting `main`.

But... if I add it to a repository that already has releases, I need the `stable` branch to start out reflecting the documentation in that most recent release.

That's what the `LATEST_RELEASE` variable is for. `git tag` outputs the list of tags as a newline-separated list. Piping them through `sort` and `head -n1` gives the highest release tag:

```bash
git tag | sort -Vr | head -n1
```
`sort -Vr` causes `sort` to sort the tags using [version sort](https://www.gnu.org/software/coreutils/manual/html_node/sort-invocation.html#sort-invocation) in reverse. Here's how that `-V` option is described:

>  It behaves like a standard sort, except that each sequence of decimal digits is treated numerically as an index/version number.

Getting the commit that creates the new branch to work was [surprisingly tricky](https://github.com/simonw/simonw-readthedocs-experiments/issues/2)!

The problem is that GitHub Actions has a rule that a workflow is not allowed to modify its own YAML configuration and then push those changes back up to GitHub.

My first version of this worked by creating the new `stable` branch from the most recent tagged release. But... this carries the risk of that tagged version including a change to the workflow YAML, which results in an error.

Eventually I realized that I only care about the contents of that `docs/` directory, so instead of creating the branch from the release `tag` I could instead create the branch from `main` and then copy in the `docs/` directory from that tag.

This avoids any chance of a file in `.github/workflows` being updated in a way that would break the Actions run.

### Resetting stable for every release

The next block is the block that fires only when I publish a new release to GitHub:

```yaml
    - name: Handle Release
      if: github.event_name == 'release'
      run: |
        git fetch --all
        git checkout stable
        git reset --hard ${GITHUB_REF#refs/tags/}
        git push origin stable --force
```
It does a hard reset to reset the content of the `stable` branch to the exact content of the tag that is being released, then does a force push to update the remote branch.

For some reason this doesn't seem to trigger that error I head earlier about the YAML workflow being updated. I'm not sure why - maybe it's because resetting to a tag is seen as a "safe" operation somehow?

ReadTheDocs watches for changes pushed to the `stable` branch, so this is enough to trigger a new build of the `/stable/` documentation.

### Copying in docs/ changes from commits marked !stable-docs

The last piece is the most complex. It handles that `!stable-docs` tag and, when it sees it, copies any files in `docs/` that were modified in the commit over to the `stable` branch:

```yaml
    - name: Handle Commit to Main
      if: contains(github.event.head_commit.message, '!stable-docs')
      run: |
        git fetch origin
        git checkout -b stable origin/stable
        # Get the list of modified files in docs/ from the current commit
        FILES=$(git diff-tree --no-commit-id --name-only -r ${{ github.sha }} -- docs/)
        # Check if the list of files is non-empty
        if [[ -n "$FILES" ]]; then
          # Checkout those files to the stable branch to over-write with their contents
          for FILE in $FILES; do
            git checkout ${{ github.sha }} -- $FILE
          done
          git add docs/
          git commit -m "Doc changes from ${{ github.sha }}"
          git push origin stable
        else
          echo "No changes to docs/ in this commit."
          exit 0
        fi
```
I got GPT-4 assistance with all of these (the [issue thread](https://github.com/simonw/simonw-readthedocs-experiments/issues/1) links to some of my prompts) but this was the one that took the most iteration. Let's break it down:

The first question we need to answer is what files in `docs/` were edited by the current commit:
```bash
FILES=$(git diff-tree --no-commit-id --name-only -r ${{ github.sha }} -- docs/)
```
If you run this command in a repo, you'll see a list of the names of the files that were modified in the most recent commit:
```bash
git diff-tree --no-commit-id --name-only -r main
```
Output is something like this:
```
docs/cli-reference.rst
docs/cli.rst
sqlite_utils/cli.py
tests/test_cli.py
```

If you add `-- docs/` at the end it will filter that down to just the files that match that path:
```bash
git diff-tree --no-commit-id --name-only -r main -- docs/
```
```
docs/cli-reference.rst
docs/cli.rst
```
The workflow assigns that to the `FILES` variable, then checks if it is empty:
```bash
if [[ -n "$FILES" ]]; then
```
If it's not empty, it loops through it and uses `git checkout` to checkout the exact copy of that file from the current commit, which will over-write the file in the current working directory:
```bash
for FILE in $FILES; do
  git checkout ${{ github.sha }} -- $FILE
done
```
Finally, it adds those files, commits them and pushes them to the `stable` branch:
```bash
git add docs/
git commit -m "Doc changes from ${{ github.sha }}"
git push origin stable
```
Here's [an example commit](https://github.com/simonw/llm/commit/b3949f10257943dccce0d6295e5d3c485014136c) that was created by this workflow.

## Configuring ReadTheDocs

There's one last step to putting this into action: reconfiguring ReadTheDocs to both build this new `stable` branch and to treat it as the default version for the project.

Here's the sequence of steps.

- Go to the project's admin page, click advanced settings and switch the default version from "stable" to "latest" - then scroll to the very bottom of the page to find the save button. This step is necessary because you can't delete the "stable" version if it is set as the default.
- Visit the Versions tab, edit the "stable" version and uncheck the "active" box. This is the same thing as deleting it.
- Find the "stable" branch on that page and activate that instead. This will trigger a build of your `stable` branch and cause it to be hosted at `/stable/` on ReadTheDocs.
- Go back to the advanced settings page and switch the default version back to "stable".

Here's a GIF illustrating those steps:

![Animated GIF illustrating the sequence of steps](https://static.simonwillison.net/static/2023/readthedocs-config.gif)

### What this gives you

And that should be it! With this workflow in place and ReadTheDocs configured the following things should now be possible:

- Any time you ship a new release on GitHub, your `/stable/` documentation will be updated to the docs for that release.
- You can fix typos in the `stable` branch and they will be quickly reflected in that `/stable/` documentation. Apply them to `main` too though or they'll be lost the next time you publish a release.
- In any commit that updates a page of documentation where you want that entire page to be updated in the `/stable/` documentation, add `!stable-docs` to the commit message. The workflow will copy the full page content into the `stable` branch and trigger a new build.

I'm using this pattern for my [simonw/llm](https://github.com/simonw/llm) repository now, and I expect to upgrade other repositories to it soon.
