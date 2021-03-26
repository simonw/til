# macOS Catalina sort-of includes Python 3

Once you have installed the "command line tools" for Catalina using the following terminal command:

    xcode-select --install

`python3` will run Python 3.7.3:

    % which python3
    /usr/bin/python3
    % python3
    Python 3.7.3 (default, Apr  7 2020, 14:06:47) 
    [Clang 11.0.3 (clang-1103.0.32.59)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>> 

`pip` isn't there as a standalone tool on the command-line, but `python3 -mpip install x` will work:

```
python3 -mpip install github-to-sqlite
Collecting github-to-sqlite
  Downloading https://files.pythonhosted.org/packages/18/d2/8a622d3fdbe161517df6941be257d0ed4590108593c3aff9a35578fa381e/github_to_sqlite-1.1-py3-none-any.whl
...
Could not install packages due to an EnvironmentError: [Errno 13] Permission denied: '/Library/Python/3.7'
Consider using the `--user` option or check the permissions.
```
I don't like running `pip` as root, so I try the `--user` option:

```
% python3 -mpip install github-to-sqlite --user
Collecting github-to-sqlite
  Using cached https://files.pythonhosted.org/packages/18/d2/8a622d3fdbe161517df6941be257d0ed4590108593c3aff9a35578fa381e/github_to_sqlite-1.1-py3-none-any.whl
Requirement already satisfied: requests in ./Library/Python/3.7/lib/python/site-packages (from github-to-sqlite) (2.23.0)
Collecting sqlite-utils>=2.7 (from github-to-sqlite)
  Using cached https://files.pythonhosted.org/packages/26/af/91237b71616a3c63bbb921ba8f0039fc784d0d33e3f908c727c1d39c757a/sqlite_utils-2.7-py3-none-any.whl
Requirement already satisfied: chardet<4,>=3.0.2 in ./Library/Python/3.7/lib/python/site-packages (from requests->github-to-sqlite) (3.0.4)
Requirement already satisfied: idna<3,>=2.5 in ./Library/Python/3.7/lib/python/site-packages (from requests->github-to-sqlite) (2.9)
Requirement already satisfied: urllib3!=1.25.0,!=1.25.1,<1.26,>=1.21.1 in ./Library/Python/3.7/lib/python/site-packages (from requests->github-to-sqlite) (1.25.9)
Requirement already satisfied: certifi>=2017.4.17 in ./Library/Python/3.7/lib/python/site-packages (from requests->github-to-sqlite) (2020.4.5.1)
Requirement already satisfied: tabulate in ./Library/Python/3.7/lib/python/site-packages (from sqlite-utils>=2.7->github-to-sqlite) (0.8.7)
Requirement already satisfied: click in ./Library/Python/3.7/lib/python/site-packages (from sqlite-utils>=2.7->github-to-sqlite) (7.1.1)
Requirement already satisfied: click-default-group in ./Library/Python/3.7/lib/python/site-packages (from sqlite-utils>=2.7->github-to-sqlite) (1.2.2)
pocket-to-sqlite 0.2 has requirement sqlite-utils~=2.4.4, but you'll have sqlite-utils 2.7 which is incompatible.
Installing collected packages: sqlite-utils, github-to-sqlite
  Found existing installation: sqlite-utils 2.4.4
    Uninstalling sqlite-utils-2.4.4:
      Successfully uninstalled sqlite-utils-2.4.4
  The script sqlite-utils is installed in '/Users/simon/Library/Python/3.7/bin' which is not on PATH.
  Consider adding this directory to PATH or, if you prefer to suppress this warning, use --no-warn-script-location.
  The script github-to-sqlite is installed in '/Users/simon/Library/Python/3.7/bin' which is not on PATH.
  Consider adding this directory to PATH or, if you prefer to suppress this warning, use --no-warn-script-location.
Successfully installed github-to-sqlite-1.1 sqlite-utils-2.7
```
As per the warnings, this isn't on my path: I can run it like this:

```
/Users/simon/Library/Python/3.7/bin/github-to-sqlite
```
Or I can add that directory to my path.

Which I didn't do, because I decided to use homebrew's Python 3.8 instead, with `pipenv` and `pipx`:
```
% brew install pipenv
# ...
% brew install pipx
Updating Homebrew...
==> Downloading https://homebrew.bintray.com/bottles/pipx-0.15.1.3_1.catalina.bottle.tar.gz
######################################################################## 100.0%
==> Pouring pipx-0.15.1.3_1.catalina.bottle.tar.gz
🍺  /usr/local/Cellar/pipx/0.15.1.3_1: 92 files, 566.8KB
```
Now I'll try using it to install a command-line tool ([github-to-sqlite](https://github.com/dogsheep/github-to-sqlite)):
```
% pipx install github-to-sqlite
  installed package github-to-sqlite 1.1, Python 3.8.2
  These apps are now globally available
    - github-to-sqlite
⚠️  Note: '/Users/simon/.local/bin' is not on your PATH environment variable. These apps will not be globally accessible until your PATH is updated. Run `pipx ensurepath` to automatically add it, or manually modify your PATH in your shell's config file (i.e. ~/.bashrc).
done! ✨ 🌟 ✨
```
In this case I WILL add `~.local/bin` to my PATH:
```
% pipx ensurepath
```
This put the following in my `.zshrc`:
```
% cat .zshrc      

# Created by `userpath` on 2020-04-21 18:18:34
export PATH="$PATH:/Users/simon/.local/bin"
```
