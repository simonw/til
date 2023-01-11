# Upgrading a pipx application to an alpha version

I wanted to upgrade my [git-history](https://datasette.io/tools/git-history) installation to a new alpha version.

`pipx upgrade git-history` doesn't work for that, because it upgrades to the most recent stable version - but I wanted the alpha.

This recipe did what I wanted:

    pipx inject git-history git-history==0.7a0

`pipx inject` provides a way to manipulate the packages installed in a specific `pipx` managed virtual environment.

The above command runs the equivalent of `pip install git-history==0.7a0` inside the virtual environment that `pipx` is already managing for `git-history`.

I confirmed that it worked like this:
```
~ % git-history --version                     
git-history, version 0.7a0
```
