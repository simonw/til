# Fixing "compinit: insecure directories" error

Every time I opened a terminal on my new Mac running Catalina with zsh I got the following annoying error:

```
Last login: Fri Apr 24 17:50:41 on ttys004
zsh compinit: insecure directories, run compaudit for list.
Ignore insecure directories and continue [y] or abort compinit [n]? ncompinit: initialization aborted
```

Based on a tip in https://github.com/zsh-users/zsh-completions/issues/680 I fixed it by doing this:

```
% compaudit
There are insecure directories:
/usr/local/share/zsh/site-functions
/usr/local/share/zsh
```

Then I ran these commands to fix it:

```
sudo chmod g-w /usr/local/share/zsh/site-functions
sudo chmod g-w /usr/local/share/zsh
```
