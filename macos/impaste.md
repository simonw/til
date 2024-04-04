# impaste: pasting images to piped commands on macOS

I wanted the ability to paste the image on my clipboard into a command in the macOS terminal.

It turns out `pbpaste` only works with textual data - so copying a portion of a screenshot to my clipboard (using [CleanShot X](https://cleanshot.com/)) and running the following produced a 0 byte file:
```bash
pbpaste > /tmp/screenshot.png
```
With some initial clues from [Feraidoon Mehri in a GitHub issue](https://github.com/simonw/llm/issues/331#issuecomment-2038425242) followed by some ChatGPT and [Claude 3 Opus prompting](https://gist.github.com/simonw/736bcc9bcfaef40a55deaa959fd57ca8) I got to the following script, saved as `~/.local/bin/impaste` on my machine (that folder is on my `PATH`) and made excutable with `chmod 755 ~/.local/bin/impaste`:

```zsh
#!/bin/zsh

# Generate a unique temporary filename
tempfile=$(mktemp -t clipboard.XXXXXXXXXX.png)

# Save the clipboard image to the temporary file
osascript -e 'set theImage to the clipboard as «class PNGf»' \
  -e "set theFile to open for access POSIX file \"$tempfile\" with write permission" \
  -e 'write theImage to theFile' \
  -e 'close access theFile'

# Output the image data to stdout
cat "$tempfile"

# Delete the temporary file
rm "$tempfile"
```
Now I can copy an image to my clipboard and run this:
```
impaste > /tmp/image.png
```
Or pipe `impaste` into any command that accepts images.
