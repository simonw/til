# Clone, edit and push files that live in a Gist

GitHub [Gists](https://gist.github.com/) are full Git repositories, and can be cloned and pushed to.

You can clone them anonymously (read-only) just using their URL:

    git clone https://gist.github.com/simonw/0a30d52feeb3ff60f7d8636b0bde296b

But if you want to be able to make local edits and then push them back, you need to use this recipe instead:

    git clone git@gist.github.com:0a30d52feeb3ff60f7d8636b0bde296b.git

You can find this in the "Embed" menu, as the "Clone via SSH" option.

This only uses the Gist's ID, the `simonw/` part from the URL is omitted.

This uses your existing GitHub SSH credentials.

You can then edit files in that repository and commit and push them like this:

    cd 0a30d52feeb3ff60f7d8636b0bde296b
    # Edit files here
    git commit -m "Edited some files" -a
    git push
