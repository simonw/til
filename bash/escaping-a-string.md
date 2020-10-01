# Escaping strings in Bash using !:q

TIL this trick, [via Pascal Hirsch](https://twitter.com/phphys/status/1311727268398465029) on Twitter. Enter a line of Bash starting with a `#` comment, then run `!:q` on the next line to see what that would be with proper Bash escaping applied.

```
bash-3.2$ # This string 'has single' "and double" quotes and a $
bash-3.2$ !:q
'# This string '\''has single'\'' "and double" quotes and a $'
bash: # This string 'has single' "and double" quotes and a $: command not found
```
