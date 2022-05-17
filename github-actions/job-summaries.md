# GitHub Actions job summaries

New feature [announced here](https://github.blog/2022-05-09-supercharging-github-actions-with-job-summaries/). Here's the [full documentation](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#adding-a-job-summary).

These are incredibly easy to use. GitHub creates a file in your workspace and puts the filename in `$GITHUB_STEP_SUMMARY`, so you can build the summary markdown over multiple steps like this:

```bash
echo "{markdown content}" >> $GITHUB_STEP_SUMMARY
```
I decided to try this out in my [simonw/pypi-datasette-packages](https://github.com/simonw/pypi-datasette-packages/) repo, which runs a daily Git scraper that records a copy of the PyPI JSON for packages within the Datasette ecosystem.

I ended up missing it with the Git commit code, so the step [now looks like this](https://github.com/simonw/pypi-datasette-packages/blob/54d43180a97d30011149d1e7ae3aaafed2ad7818/.github/workflows/fetch.yml#L20-L32):

```yaml
    - name: Commit and push
      run: |-
        git config user.name "Automated"
        git config user.email "actions@users.noreply.github.com"
        git add -A
        timestamp=$(date -u)
        git commit -m "${timestamp}" || exit 0
        echo '### Changed files' >> $GITHUB_STEP_SUMMARY
        echo '```' >> $GITHUB_STEP_SUMMARY
        git show --name-only --format=tformat: >> $GITHUB_STEP_SUMMARY
        echo '```' >> $GITHUB_STEP_SUMMARY
        git pull --rebase
        git push
```
This produces a summary that looks like this:

<img width="657" alt="Screenshot of the summary" src="https://user-images.githubusercontent.com/9599/168874059-b08afb20-c9f3-4c6d-9224-311f21696bfd.png">

Two things I had to figure out here. First, the backtick needs escaping if used in double quotes but does not in single quotes:

```bash
echo '```' >> $GITHUB_STEP_SUMMARY
```
I wanted to show just the list of affected filenames from the most recent Git commit. That's what this does:

    git show --name-only --format=tformat:

Without the `--format=tformat` bit this shows the full commit message and header in addition to the list of files.

I'm running this in the same block as the other `git` commands so that this line will terminate the step early without writing to the summary file if there are no changes to be committed:

```bash
git commit -m "${timestamp}" || exit 0
```
