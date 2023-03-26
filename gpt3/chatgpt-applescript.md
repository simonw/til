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

## Bonus: Use JavaScript instead

[tzs on Hacker News](https://news.ycombinator.com/item?id=35319618) tipped me off to the fact that AppleScript automation can be written in JavaScript these days too.

Turns out ChatGPT knows how to translate my AppleScript to JavaScript!

My prompt:

> ```applescript
> tell application "Notes"
>    repeat with eachNote in every note
>       set noteTitle to the name of eachNote
>       set noteBody to the body of eachNote
>       set output to noteTitle & "\n" & noteBody & "\n"
>       log output
>    end repeat
> end tell
>
> Write that in JavaScript that talks to Apple automation instead

ChatGPT response:

> To write a script in JavaScript that talks to Apple automation, you can use the JavaScript for Automation (JXA) language. Here's the equivalent script using JXA:
>
> ```javascript
> const Notes = Application('Notes');
> Notes.includeStandardAdditions = true;
> 
> const notes = Notes.notes();
> const noteData = [];
> 
> notes.forEach((note) => {
>   const noteTitle = note.name();
>   const noteBody = note.body();
>   const output = noteTitle + '\n' + noteBody + '\n';
>   noteData.push(output);
> });
> 
> noteData.forEach((data) => {
>   console.log(data);
> });
> ```
>
> To run this script, save it as a `.scpt` file with a text editor and then run it using the Script Editor app on macOS or using the command line with `osascript`:
>
> ```bash
> osascript -l JavaScript path/to/your/script.scpt
> ```
