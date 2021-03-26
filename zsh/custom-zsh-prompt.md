# Customizing my zsh prompt

I got fed up of the default macOS `zsh` prompt:

    simon@Simons-MacBook-Pro ~ % 

Mainly because I like copying and pasting terminal examples into GitHub issues.

I changed it to this:

    ~ % cd /tmp
    /tmp % 

By adding this line to the top of my `~/.zshrc` file:

    PROMPT='%1~ %# '
