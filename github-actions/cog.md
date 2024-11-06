# Running cog automatically against GitHub pull requests

I really like [Cog](https://nedbatchelder.com/code/cog/) ([previously](https://til.simonwillison.net/python/cog-to-update-help-in-readme)) as a tool for automating aspects of my Python project documentation - things like the SQL schemas shown on the [LLM logging page](https://llm.datasette.io/en/latest/logging.html#sql-schema).

When using `cog` in this way it's important to remember to run `cog -r` to update those generated files before pushing a commit.

I've previously been enforcing this using GitHub Actions - as part of my tests I run `cog --check *.md` so that my test suite fails if the generated files are out of date.

This morning I switched to a friendlier version. I now run a GitHub Actions workflow against any created or modified pull requests and, if `cog` needs to be run, the workflow runs it and then helpfully commits the files back to that repo.

I [got Claude to write the initial workflow](https://gist.github.com/simonw/28a9e7438f3115c27dc5fbf0d5690ebf), and then iterated on it to get it working.

This goes in `.github/workflows/cog.yml`:

```yaml
name: Run Cog

on:
  pull_request:
    types: [opened, synchronize]

permissions:
  contents: write
  pull-requests: write

jobs:
  run-cog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.head_ref }}
      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -e '.[test]'
      - name: Run cog
        run: |
          cog -r docs/**/*.md docs/*.md
      - name: Check for changes
        id: check-changes
        run: |
          if [ -n "$(git diff)" ]; then
            echo "changes=true" >> $GITHUB_OUTPUT
          else
            echo "changes=false" >> $GITHUB_OUTPUT
          fi
      - name: Commit and push if changed
        if: steps.check-changes.outputs.changes == 'true'
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          git add -A
          git commit -m "Ran cog"
          git push
```
The `[opened, synchronize]` trigger means that the workflow will run whenever a pull request is either created or updated in some way.

Using that `user.email` and `user.name` causes the bot to get a nice icon of its own:

![List of commits on GitHub - the last one reads Ran cog and shows a GitHub avatar icon](https://github.com/user-attachments/assets/d4a59c91-8ad4-46a6-9e85-74a53badf766)

Squash-merging the PR causes the bot to be [credited as a co-author](https://github.com/simonw/llm/commit/febbc04fb6d847bd35ce5ba0156ef010f5894564).
