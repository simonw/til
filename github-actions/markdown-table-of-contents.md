# Updating a Markdown table of contents with a GitHub Action

[markdown-toc](https://github.com/jonschlinkert/markdown-toc) is a Node script that parses a Markdown file and generates a table of contents for it, based on the headings.

You can run it (without installing anything first thanks to the magic of [npx](https://medium.com/@maybekatz/introducing-npx-an-npm-package-runner-55f7d4bd282b)) like so:

    npx markdown-toc README.md

This will output the table of contents to standard out.

You can add the following comment to a markdown file:
  
    <!-- toc -->
    <!-- tocstop -->

And then run the command like this to update a table of contents in place:

    npx markdown-toc -i README.md

I wrote this GitHub Action to apply this command every time the README is updated, then commit the results back to the repository.

Save this as `.github/workflows/readme-toc.yml`:

```yaml
name: Update README table of contents

on:
  workflow_dispatch:
  push:
    branches:
    - main
    - master
    paths:
    - README.md

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - name: Check out repo
      uses: actions/checkout@v2
    - name: Update TOC
      run: npx markdown-toc README.md -i
    - name: Commit and push if README changed
      run: |-
        git diff
        git config --global user.email "readme-bot@example.com"
        git config --global user.name "README-bot"
        git diff --quiet || (git add README.md && git commit -m "Updated README")
        git push
```
You can see this running on the [dogsheep/twitter-to-sqlite](https://github.com/dogsheep/twitter-to-sqlite) repository.

Unfortunately these links don't work on READMEs that are rendered by PyPI yet, e.g. [twitter-to-sqlite](https://pypi.org/project/twitter-to-sqlite/). There's an open issue for that [here](https://github.com/pypa/readme_renderer/issues/169).
