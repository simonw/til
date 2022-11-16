#  How to create a tarball of a git repository using "git archive"

I figured this out in [a Gist in 2016](https://gist.github.com/simonw/a44af92b4b255981161eacc304417368) which has attracted a bunch of comments over the years. Now I'm upgrading it to a retroactive TIL.

Run this in the repository folder:

    git archive --format=tar.gz -o /tmp/my-repo.tar.gz --prefix=my-repo/ main

This will write out a file to `/tmp/my-repo.tar.gz`.

When you `tar -xzvf my-repo.tar.gz` that file it will output a `my-repo/` directory with just the files - not the `.git` folder - from your repository.

You can use a commit hash or tag or branch name instead of `main` to create an archive of a different point in that repository.

Without the `--prefix` option you'll get a `.tar.gz` file which, when compressed, writes a bunch of stuff to your current directory. This usually isn't what you want!

Here's a version that picks up the name of the directory you run it in:

    git archive --format=tar.gz -o $(basename $PWD).tar.gz --prefix=$(basename $PWD)/ main

Note the trailing `/` on `--prefix` - without this you'll get folders called things like `datasettetests`.

`basename $PWD` gives you the name of your current folder.
