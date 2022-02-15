# nullglob in bash

I ran into a tricky problem while working [on this issue](https://github.com/simonw/datasette-publish-fly/issues/17): the following line was behaving in an unexpected way for me:

    datasette content.db *.db --create

What I expect this to do is to create a `content.db` database if one does not exist, and then start Datasette with both that database and any other databases that exist in the directory.

The surprising behaviour occurred when the directory started off empty. Running the above in `bash` caused a file called `*.db` to be created in the directory.

It turns out if `bash` can't find any files matching a wildcard it passes that wildcard as a literal value to the underlying command!

`sh` does the same thing. `zsh` returns an error:

```
% datasette content.db *.db --create
zsh: no matches found: *.db
```
The solution, for `bash`, is to set the `nullglob` shell option. That can be done like this:

    shopt -s nullglob

This lasts for the rest of the interactive session, and causes `bash` to behave the way I expected it to, completely ignoring the `*.db` wildcard if it has no matches.

## Using this in a Dockerfile

I originally ran into this because I had a `Dockerfile` with a last line that looked like this:

`CMD datasette serve --host 0.0.0.0 --cors --inspect-file inspect-data.json --metadata metadata.json /data/tiddlywiki.db --create --port $PORT /data/*.db`

The goal here was to serve any existing databases in the `/data/` mounted volume, and to explicitly create that `tiddlywiki.db` database if it did not exist.

But it created a `*.db` database file if the folder was empty, due to the issue described above.

I ended up using this recipe to work around the problem:

`CMD ["/bin/bash", "-c", "shopt -s nullglob && datasette serve --host 0.0.0.0 --cors --inspect-file inspect-data.json /data/tiddlywiki.db --create --port $PORT /data/*.db"]`

This uses `CMD` to execute `/bin/bash` and pass it a one-liner that sets `nullglob` and then calls Datasette. This worked as intended.
