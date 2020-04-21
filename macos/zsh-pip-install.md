# Running pip install -e .[test] in zsh on macOS Catalina

macOS Catalina uses `zsh` rather than `bash` as the default shell (apparently because Apple don't like GPL 3).

I usually set up my Python projects for development like this:

    datasette % pipenv shell
    Launching subshell in virtual environment…
     . /Users/simon/.local/share/virtualenvs/datasette-AWNrQs95/bin/activate                                                                         
    datasette %  . /Users/simon/.local/share/virtualenvs/datasette-AWNrQs95/bin/activate
    (datasette) simon@Simons-MacBook-Pro datasette % pip install -e .[test]
    zsh: no matches found: .[test]

In `zsh` the `[` character has special meaning.

Two solutions. The first is to use quotes:

    datasette % pip install -e '.[test]'
    Obtaining file:///Users/simon/Dropbox/Development/datasette
    ...

The second is to prefix it with `noglob`:

    datasette % noglob pip install -e .[test]
