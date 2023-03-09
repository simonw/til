# Using ChatGPT to write AppleScript

I found a killer application for ChatGPT today: writing AppleScript!

I've been stubbornly refusing to learn AppleScript for nearly twenty years at this point. Thanks to ChatGPT I can continue not to learn it, but I can now use it to solve problems.

I wanted to figure out how to export the content of my Apple Notes notes. Here are some edited highlights from my conversation with ChatGPT:

**Me**:
> Write applescript to loop through all of my Apple Notes and output their contents

**ChatGPT**:

```applescript
tell application "Notes"
   repeat with eachNote in every note
      set noteTitle to the name of eachNote
      set noteBody to the body of eachNote
      display dialog noteTitle & return & return & noteBody
   end repeat
end tell
```
**Me**:
> How can I turn that into a zsh script which will output the results to my terminal

**ChatGPT**:
```zsh
#!/usr/bin/zsh

osascript -e 'tell application "Notes"
   repeat with eachNote in every note
      set noteTitle to the name of eachNote
      set noteBody to the body of eachNote
      set output to noteTitle & "\n" & noteBody & "\n"
      display dialog output
      log output
   end repeat
end tell'
```
I had to change that first line to `#!/bin/zsh` - then when I ran it it spammed my screen with dialog boxes.

**Me**:

> I want to log the notes contents to the terminal, not display it in a dialog

**ChatGPT**:

```zsh
#!/bin/zsh

osascript -e 'tell application "Notes"
   repeat with eachNote in every note
      set noteTitle to the name of eachNote
      set noteBody to the body of eachNote
      set output to noteTitle & "\n" & noteBody & "\n"
      log output
   end repeat
end tell'
```

I ended up using what I learned here to build [apple-notes-to-sqlite](https://github.com/dogsheep/apple-notes-to-sqlite), a new Python tool which wraps `osascript` under the hood and uses it to export my Apple Notes data to a SQLite database.
