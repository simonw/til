# Enabling a user to execute a specific command as root without a password

I wanted a script running as a non-root user to be able to restart a systemd service on my Ubuntu machine without needing a password.

I figured out how to do that by adding the following line to the `sudoers` file, which can be edited as root using the `visudo` command:
```
# dogsheep user can restart datasette service
dogsheep  ALL = (root) NOPASSWD: /usr/bin/systemctl restart datasette
```
Having added this line, my `dogsheep` user account could now run the following:

```
$ sudo /usr/bin/systemctl restart datasette
```
But if it tries to run the command with any other arguments it gets prompted for a password:
```
$ sudo /usr/bin/systemctl restart datasette2
[sudo] password for dogsheep: 
```
