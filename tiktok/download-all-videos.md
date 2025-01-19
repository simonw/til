# Downloading every video for a TikTok account

TikTok may or may not be banned in the USA within the next 24 hours or so. Here's a pattern you can use to download all of the videos from a specific account.

## Scrape the list of video URLs 

I used a variant of my [Twitter scraping trick](https://til.simonwillison.net/twitter/collecting-replies). Start by loading up a profile page - like [https://www.tiktok.com/@ilgallinaio_special](www.tiktok.com/@ilgallinaio_special) - in Firefox or Chrome or Safari.

Open up the DevTools and paste in the following JavaScript:

```javascript
window.videoUrls = new Set();

function collect() {
    Array.from(document.querySelectorAll('a[href*="/video/"]'), el => el.href).forEach(href => {
        window.videoUrls.add(href);
    })
};

setInterval(collect, 500);
```

This will scan the page every half a second looking for links to TikTok videos - links with `/video/` in their URL - and add those to a growing set called `videoUrls`.

Now switch to the "oldest" sort direction and scroll down the page until you reach the bottom. TikTok implements infinite-ish scrolling so this may take a while for an account with a lot of videos.

Once you get to the bottom, copy out the collected list of URLs. In Firefox I used this command for that:

```javascript
copy(Array.from(window.videoUrls))
```
That copied the array of URLs to my clipboard. I then pasted them into a file and saved it as `videos.json` - the file contents looked something like this (but a lot longer):
```json
[
  "https://www.tiktok.com/@ilgallinaio_special/video/7204803049351695622",
  "https://www.tiktok.com/@ilgallinaio_special/video/7204877634189151493",
  "https://www.tiktok.com/@ilgallinaio_special/video/7205157890372537606",
  "https://www.tiktok.com/@ilgallinaio_special/video/7205189803074211077"
]
```
## Download them all with yt-dlp

The [yt-dlp](https://github.com/yt-dlp/yt-dlp) Python program can download from TikTok. I ran it against all of the URLs in my `videos.json` file like this:

```bash
mkdir -p downloads
jq -r '.[]' videos.json | while read url; do
    uvx yt-dlp -o "downloads/%(title)s-%(id)s.%(ext)s" "$url"
    if [[ $? -eq 0 ]]; then
        echo "Successfully downloaded: $url"
    else
        echo "Failed to download: $url"
    fi
    sleep 1
done
```
This creates a `downloads/` folder containing files with names like this:
```
#perte -7204803049351695622.mp4
#perte -7204877634189151493.mp4
#perte -7205189803074211077.mp4
#perte i galli moroseta🐓🐓🌸🍾🍾💪😅-7205157890372537606.mp4
```

## Bonus: running Whisper against them

I did this against an account that wasn't just dancing chickens and decided to use Whisper running on macOS via [mlx-whisper](https://pypi.org/project/mlx-whisper/) to generate text files with transcripts, so I could search that content later on.

Here's the recipe I used for that, powered by `uv run`:

```bash
for f in *.mp4; do [[ ! -f "${f:r}.txt" ]] && echo "Processing $f" && uv run --with mlx-whisper mlx_whisper "$f"; done
```
This can be run multiple times - it checks to see if a `.txt` file exists already and only executes against `.mp4` files that have not yet been processed.

## Extra bonus: adding a progress bar

After I kicked this off against a larger account I realized a progress bar would be nice. I got ChatGPT o1 to write me this script:

```python
#!/usr/bin/env python3

import sys
import time
import subprocess

def main():
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <total> <shell_command>")
        sys.exit(1)
    
    total = int(sys.argv[1])
    # If your command may include spaces, you might need to do this:
    # shell_command = ' '.join(sys.argv[2:])
    # but for the simple example provided:
    shell_command = sys.argv[2]

    # -- Step 1: Get initial progress and record the time --
    try:
        initial_output = subprocess.check_output(shell_command, shell=True)
        done_initial = int(initial_output.strip())
    except Exception as e:
        print(f"Error running initial command: {shell_command}\n{e}")
        sys.exit(1)

    # Clamp in case the command returns something above the total or below zero
    if done_initial < 0:
        done_initial = 0
    if done_initial > total:
        done_initial = total

    time_initial = time.time()

    # Print one quick update before we start the loop
    print_progress(done_initial, total, 0, 0)

    # If we already reached (or exceeded) the total, exit immediately
    if done_initial >= total:
        print("\nDone!")
        sys.exit(0)

    # -- Step 2: Repeatedly poll the command to update progress --
    polling_interval = 1.0  # seconds between checks

    while True:
        time.sleep(polling_interval)

        # Fetch current progress
        try:
            output = subprocess.check_output(shell_command, shell=True)
            done = int(output.strip())
        except Exception as e:
            print(f"\nError running command: {shell_command}\n{e}")
            sys.exit(1)
        
        # Clamp done to never exceed total or go below 0
        if done < 0:
            done = 0
        if done > total:
            done = total

        # How much progress has been made since we started measuring?
        delta_done = done - done_initial
        delta_time = time.time() - time_initial

        # Print the progress bar
        print_progress(done, total, delta_done, delta_time)

        if done >= total:
            break

    print("\nDone!")


def print_progress(done, total, delta_done, delta_time):
    """
    Print a single-line progress bar with percentage and ETA (if possible).
    Overwrites the previous line via carriage return.
    """

    # Fraction complete
    fraction = done / total if total else 1.0

    # Build the bar
    bar_length = 50
    filled_length = int(bar_length * fraction)
    bar = "#" * filled_length + "-" * (bar_length - filled_length)

    # Compute ETA based only on new progress (delta_done)
    if delta_done > 0:
        time_per_item = delta_time / delta_done
        remaining = total - done
        eta_seconds = int(time_per_item * remaining)
        eta_string = format_eta(eta_seconds)
    else:
        # If no new items have completed since the script started, can't guess yet
        eta_string = "calculating..."

    progress_line = (
        f"\r[{bar}] {done}/{total} ({fraction*100:.1f}%) - ETA: {eta_string}"
    )
    print(progress_line, end='', flush=True)


def format_eta(seconds):
    """Convert number of seconds into a H:MM:SS or M:SS format string."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    if h > 0:
        return f"{h:d}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"


if __name__ == "__main__":
    main()
```
Which I can then run like this:

```bash
uv run progress.py 45 'ls *.mp4 | wc -l'
```
The `45` there is the expected number of downloads (found with `jq length < videos.json`). The `ls *.mp4 | wc -l` string is a command to run on each iteration to count how many items have been processed.

This command provides both a visible ASCII progress bar and an ETA prediction of when the program will finish, based on how many items have been processed and how quickly they appear to be running.
