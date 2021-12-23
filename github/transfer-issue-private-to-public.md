# Transferring a GitHub issue from a private to a public repository

I have my own private `notes` repository where I sometimes create research threads. Occasionally I want to transfer these to a public repository to publish their contents.

https://docs.github.com/en/issues/tracking-your-work-with-issues/transferring-an-issue-to-another-repository says:

> You can't transfer an issue from a private repository to a public repository.

I found this workaround:

1. Create a new private repository. I called mine `simonw/temp`
2. Transfer the issue from your original repository to this new temporary repository
3. Use the "Settings" tab in the temporary repository to change the entire repository's visibility from private to public
4. Transfer the issue from the temporary repository to the public repository that you want it to live in

## Using the gh tool

You can perform transfers using the web interface, but I also learned how to do it using the `gh` tool.

Install that with `brew install gh`

Then you can run this:

    gh issue transfer https://github.com/simonw/temp/issues/1 simonw/datasette-tiddlywiki

I used this trick today to transfer https://github.com/simonw/datasette-tiddlywiki/issues/2 out of my private `notes` repo.
