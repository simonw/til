# Escaping strings in Bash using !:q

TIL this trick, [via Pascal Hirsch](https://twitter.com/phphys/status/1311727268398465029) on Twitter. Enter a line of Bash starting with a `#` comment, then run `!:q` on the next line to see what that would be with proper Bash escaping applied.

```
bash-3.2$ # This string 'has single' "and double" quotes and a $
bash-3.2$ !:q
'# This string '\''has single'\'' "and double" quotes and a $'
bash: # This string 'has single' "and double" quotes and a $: command not found
```
How does this work? [James Coglan explains](https://twitter.com/mountain_ghosts/status/1311767073933099010):

> The `!` character begins a history expansion; `!string` produces the last command beginning with `string`, and `:q` is a modifier that quotes the result; so I'm guessing this is equivalent to `!string` where `string` is `""`, so it produces the most recent command, just like `!!` does

A bunch more useful tips in the [thread about this on Hacker News](https://news.ycombinator.com/item?id=24659282).
