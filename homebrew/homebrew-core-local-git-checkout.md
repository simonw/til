# Browsing your local git checkout of homebrew-core

The [homebrew-core](https://github.com/Homebrew/homebrew-core) repository contains all of the default formulas for Homebrew.

It's a huge repo, and if you browse it through the GitHub web interface you can run into errors like this one:

https://github.com/Homebrew/homebrew-core/commits/master/Formula/libspatialite.rb

> ### Sorry, this commit history is taking too long to generate.
>
> Refresh the page to try again, or view this history locally using the following command:
>
>     git log master -- Formula/libspatialite.rb

It turns out there's a full checkout of the repo (including history) in this folder on your computer already:

    /usr/local/Homebrew/Library/Taps/homebrew/homebrew-core

So you can browse the history for that file locally like so:

    cd /usr/local/Homebrew/Library/Taps/homebrew/homebrew-core
    git log master -- Formula/libspatialite.rb
