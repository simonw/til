# Piping echo to a file owned by root using sudo and tee

I wanted to create a file with a shell one-liner where the file lived somewhere owned by root.

I tried this but it didn't work:
```bash
sudo echo '#!/bin/sh
/usr/bin/tarsnap -c \
  -f "$(uname -n)-$(date +%Y-%m-%d_%H-%M-%S)" \
  /home/simon/team-storage' > /root/tarsnap-backup.sh
```
Running `echo` using `sudo` didn't pass through to the `> filename` bit.

Here's what did work:

```bash
echo '#!/bin/sh
/usr/bin/tarsnap -c \
  -f "$(uname -n)-$(date +%Y-%m-%d_%H-%M-%S)" \
  /home/simon/team-storage' | sudo tee /root/tarsnap-backup.sh > /dev/null
```

No need for `sudo` on the `echo` - but it pipes the output to `sudo tee` which can then write the file to disk.

The `> /dev/null` at the end supresses any output from the `tee` command. If you want to see the output you can do this instead:

```bash
echo '#!/bin/sh
/usr/bin/tarsnap -c \
  -f "$(uname -n)-$(date +%Y-%m-%d_%H-%M-%S)" \
  /home/simon/team-storage' | sudo tee /root/tarsnap-backup.sh
```
