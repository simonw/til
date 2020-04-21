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
