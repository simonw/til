# Seeing files opened by a process using opensnoop

I decided to try out [atuin](https://github.com/ellie/atuin?utm_source=tldrnewsletter), a shell extension that writes your history to a SQLite database.

It's really neat. I wanted to see where the SQLite database lived on disk so I could poke around inside it with [Datasette](https://datasette.io/).

The documentation didn't mention the location of the database file, so I decided to figure that out myself.

I worked out a recipe using `opensnoop`, which comes pre-installed on macOS.

In one terminal window, run this:

    sudo opensnoop 2>/dev/null | grep atuin

Then run the `atuin history` command in another terminal - and the files that it accesses will be dumped out by `opensnoop`:

```
  501  51725 atuin          4 /dev/dtracehelper    
  501  51725 atuin         -1 /etc/.mdns_debug     
  501  51725 atuin          4 /usr/local/Cellar/atuin/0.9.1/bin 
  501  51725 atuin         -1 /usr/local/Cellar/atuin/0.9.1/bin/Info.plist 
  501  51725 atuin          4 /dev/autofs_nowait   
  501  51725 atuin          5 /Users/simon/.CFUserTextEncoding 
  501  51725 atuin          4 /dev/autofs_nowait   
  501  51725 atuin          5 /Users/simon/.CFUserTextEncoding 
  501  51725 atuin         10 .                    
  501  51725 atuin         10 /Users/simon/.config/atuin/config.toml 
  501  51725 atuin         10 /Users/simon/.local/share/atuin/history.db 
  501  51725 atuin         11 /Users/simon/.local/share/atuin/history.db-wal 
  501  51725 atuin         12 /Users/simon/.local/share/atuin/history.db-shm 
```
Then I ran `open /Users/simon/.local/share/atuin/history.db` (because I have [Datasette Desktop](https://datasette.io/desktop) installed) and could start exploring that database:

![Screenshot of Datasette showing the history table from the atuin database](https://user-images.githubusercontent.com/9599/165356208-4546e23a-47e6-47f1-a759-f1d849131aa0.png)

The `2>/dev/null` bit redirects standard error for `opensnoop` to `/dev/null` - without this it spews out a noisy volume of `dtrace: error ...` warnings.
