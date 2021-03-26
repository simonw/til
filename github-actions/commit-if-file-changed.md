# Commit a file if it changed

This recipe runs a Python script to update a README, then commits it back to the parent repo but only if it has changed:

```yaml
on:
  push:
    branches:
    - master
# ...
    - name: Update README
      run: python update_readme.py --rewrite
    - name: Commit README back to the repo
      run: |-
        git config --global user.email "readme-bot@example.com"
        git config --global user.name "README-bot"
        git diff --quiet || (git add README.md && git commit -m "Updated README")
        git push
```
My first attempt threw an error if I tried o run `git commit -m ...` and the README had not changed.

It turns out `git diff --quiet` exits with a 1 exit code if anything has changed, so this recipe adds the file and commits it only if something differs:

```bash
git diff --quiet || (git add README.md && git commit -m "Updated README")
```

Mikeal Rogers has a [publish-to-github-action](https://github.com/mikeal/publish-to-github-action) which uses a [slightly different pattern](https://github.com/mikeal/publish-to-github-action/blob/000c8a4f43e2a7dd4aab81e3fdf8be36d4457ed8/entrypoint.sh#L21-L27):

```bash
# publish any new files
git checkout master
git add -A
timestamp=$(date -u)
git commit -m "Automated publish: ${timestamp} ${GITHUB_SHA}" || exit 0
git pull --rebase publisher master
git push publisher master
```

Cleanest example yet: https://github.com/simonw/coronavirus-data-gov-archive/blob/master/.github/workflows/scheduled.yml

```yaml
name: Fetch latest data

on:
  push:
  repository_dispatch:
  schedule:
    - cron:  '25 * * * *'

jobs:
  scheduled:
    runs-on: ubuntu-latest
    steps:
    - name: Check out this repo
      uses: actions/checkout@v2
    - name: Fetch latest data
      run: |-
        curl https://c19downloads.azureedge.net/downloads/data/data_latest.json | jq . > data_latest.json
        curl https://c19pub.azureedge.net/utlas.geojson | gunzip | jq . > utlas.geojson
        curl https://c19pub.azureedge.net/countries.geojson | gunzip | jq . > countries.geojson
        curl https://c19pub.azureedge.net/regions.geojson | gunzip | jq . > regions.geojson
    - name: Commit and push if it changed
      run: |-
        git config user.name "Automated"
        git config user.email "actions@users.noreply.github.com"
        git add -A
        timestamp=$(date -u)
        git commit -m "Latest data: ${timestamp}" || exit 0
        git push
```
