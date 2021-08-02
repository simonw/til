# Search and replace with regular expressions in VS Code

I wanted to replace all instances of this:

    `#90 <https://github.com/simonw/sqlite-utils/issues/90>`__

With this:

    :issue:`90`

For [sqlite-utils issue #306](https://github.com/simonw/sqlite-utils/issues/306).

I used the VS Code's Find and Replace tool with regular expression mode turned on (the `.*` button). I used the following for the find:

    `#(\d+) <https://github.com/simonw/sqlite-utils/issues/\1>`__

Note the `\1` reference to say "the same thing I captured earlier with parenthesis". Then I used this as the replace string:

    :issue:`$1`

Here the `$1` means "the first thing captured with parenthesis".

<img width="983" alt="Screenshot of the find and replace dialog" src="https://user-images.githubusercontent.com/9599/127925903-156f2f74-d8d3-4ce3-b65b-aed29a279253.png">

The resulting change can be seen in [commit e83aef95](https://github.com/simonw/sqlite-utils/commit/e83aef951bd3e8c179511faddb607239a5fa8682).
