# Commit a file if it changed

Tthis recipe runs a Python script to update a README, then commits it back to the parent repo but only if it has changed:

```yaml
on:
  push:
    branches:
    - master
    # We don't want to run this action in a loop - where
    # push of README triggers yet another run:
    paths-ignore:
    - README.md
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
