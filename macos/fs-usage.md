# Using fs_usage to see what files a process is using

Today I wanted to figure out where the `vercel` CLI tool on my Mac kept its authentication tokens.

I solved the problem using the macOS `fs_usage` command, which traces filesystem activity for everything or for a specific process.

I ran `vercel login` to start the tool running. Thankfully Vercel's tool pauses at that point and asks you to select a login provider - which means you can find the PID of the new process in another window:

```
$ vercel login
Vercel CLI 28.16.11
> Log in to Vercel (Use arrow keys)
❯ Continue with GitHub 
  Continue with GitLab 
  Continue with Bitbucket 
  Continue with Email 
  Continue with SAML Single Sign-On 
  ─────────────────────────────────
  Cancel 
```
Then in another window:
```
$ ps aux | grep vercel
simon            87632   0.0  0.0 408644400   1552 s023  S+    7:58AM   0:00.00 grep vercel
simon            87587   0.0  0.1 409432576 100576 s021  S+    7:58AM   0:00.41 node /opt/homebrew/bin/vercel login
```
Then I started `fs_usage` like this:

```bash
sudo fs_usage -f pathname 87587
```

The `-f pathname` option filters to just show "Pathname-related events". The PID comes at the end.

With that command running, I completed the login process in the other window. A whole bunch of output was dumped to the `fs_usage` window, including the following:

```
08:02:07.011111  lstat64                   /Users/simon/Library/Application Support/com.vercel.cli                                0.000006   node.4017721
08:02:07.011124  lstat64                   /Users/simon/Library/Application Support/com.vercel.cli/auth.json                      0.000011   node.4017721
08:02:07.011587  stat64                    /Users/simon/Library/Application Support/com.vercel.cli/auth.json                      0.000009   node.4017721
08:02:07.011716  open     F=27   (_WC_T______X)  /Users/simon/Library/Application Support/com.vercel.cli/auth.json.1284651536     0.000074   node.4017721
08:02:07.019564  close    F=27                                                                                                    0.000013   node.4017721
```
So the answer to my question is that Vercel store their authentication tokens in `~/Library/Application Support/com.vercel.cli/auth.json`.

Sure enough:

```
$ cat ~/Library/Application\ Support/com.vercel.cli/auth.json 
{
  "// Note": "This is your Vercel credentials file. DO NOT SHARE!",
  "// Docs": "https://vercel.com/docs/project-configuration#global-configuration/auth-json",
  "token": "... redacted ..."
}
```

## More fs_usage

Running `sudo fs_usage` without any other parameters displays a constant stream of everything happening on the machine - pretty overwhelming!

This includes network operations and disk I/O as well.

The `-f` filter option accepts the following values:

- `network` - network-related events, such as `accept`, `recfrom` and `sendto`. These do not appear very readable, just presenting information like `recvfrom F=13 B=0x2fc`.
- `filesys` filesystem events are also very low-level: `fcntl`, `stat64`, `pread` etc - but some of them do at least include the full path to the file being accessed.
- `pathname` events are things like `stat64`, `open`, `close`, `readlink` - these all include the path and appear to be less verbose than `filesys` - I think `pathname` is the most useful filter.
- `exec` events show when processes are started and stopped. I haven't played with these enough to see them working yet.
- `diskio` events show disk I/O operations and are even more low-level than `filesys`.
- `cachehit` appears to show ALL of the above information, with the addition of `CACHE_HIT` rows.

So for most of my purposes it looks like `sudo fs_usage -f pathname PID` is the most useful command.

## See also these TILs

- [Using lsof on macOS](https://til.simonwillison.net/macos/lsof-macos)
- [Seeing files opened by a process using opensnoop](https://til.simonwillison.net/macos/open-files-with-opensnoop)
