# Atuin for zsh shell history in SQLite

[Atuin](https://github.com/ellie/atuin) (via [Rhet Turnbull](https://twitter.com/RhetTurnbull/status/1518942324004319232)) "replaces your existing shell history with a SQLite database". Obviously I had to try this out!

I installed it with Homebrew:

    brew install atuin

Then ran this to add it to my `.zshrc` config:

    echo 'eval "$(atuin init zsh)"' >> ~/.zshrc

I restarted my terminal... and now I have a SQLite database full of commands I have run!

The database lives at `~/.local/share/atuin/history.db` (I figured that out with [this TIL](https://til.simonwillison.net/macos/open-files-with-opensnoop)), and can be opened in Datasette.

![Screenshot of Datasette showing the history table from the atuin database](https://user-images.githubusercontent.com/9599/165356208-4546e23a-47e6-47f1-a759-f1d849131aa0.png)

## Removing the "up" key binding

Atuin hijacks the `Ctrl+R` shortcut to provide an interactive search window, which I really like:

![Screenshot of my terminal history in Atuin](https://user-images.githubusercontent.com/9599/165371428-69f60fa5-0ad6-4d7a-a476-79d88c8b6959.png)

But it also hijacks the Up arrow key, which I didn't like - it interfered with how I usually use that (quickly getting back my previous command and editing it).

[This thread](https://github.com/ellie/atuin/issues/51) in the Atuin issues lead me to a solution. I edited my `~/.zshrc` file and replaced the `atuin` bit at the bottom with this:

```zsh
eval "$(atuin init zsh)"
# Disable up binding: https://github.com/ellie/atuin/issues/51#issuecomment-834833821
bindkey "^[[A" history-beginning-search-backward # after the atuin init
```
