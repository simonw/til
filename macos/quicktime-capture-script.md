# A script to capture frames from a QuickTime video

I was putting together some notes for a talk I gave, and I wanted an efficient way to create screenshots of specific moments in a video of that talk.

After much messing around in ChatGPT and Claude 3 Opus I put together this system for doing that.

First, open a video in QuickTime Player. Make sure you only have one QuickTime Player window open. Hit play.

Now run the `zsh` script below - I called mine `capture.sh` and ran it with `chmod 755 capture.sh` and then `./capture.sh`.

Keep the terminal window on top. Any time you want to capture the currently displayed frame in the video, hit `<enter>` in that window - it will then read the current timestamp using AppleScript and then pass that to `ffmpeg` (`brew install ffmpeg` if you don't have that yet) to grab a JPEG of that point in the video and save it to `/tmp`.

When you are done, quit the script with `Ctrl+C` and copy all of the `/tmp/frame_*.jpg` captured videos out of `/tmp` and put them somewhere more permanent.

```zsh
#!/bin/zsh

# Check if the video filename is provided as an argument
if [ $# -eq 0 ]; then
    echo "Please provide the video filename as an argument."
    exit 1
fi

video_filename=$1

# Function to convert time in seconds to HH:MM:SS format
function seconds_to_hms {
    local total_seconds=$1
    local hours=$((total_seconds / 3600))
    local minutes=$(((total_seconds % 3600) / 60))
    local seconds=$((total_seconds % 60))
    printf "%02d:%02d:%02d\n" $hours $minutes $seconds
}

# Function to capture frame
function capture_frame {
    local current_time=$1
    local formatted_time=$(seconds_to_hms $current_time)
    local filename="/tmp/frame_${formatted_time//:/}.jpg"
    
    # Run ffmpeg to capture the frame
    ffmpeg -ss $formatted_time -i "$video_filename" -frames:v 1 $filename
    
    echo "Saved frame to $filename"
}

# Main loop
while true; do
    echo "Press any key to capture the current video frame..."
    read -sk 1 key

    # Use osascript to get the current time from QuickTime Player
    current_time=$(osascript -e 'tell application "QuickTime Player" to tell document 1 to get current time')

    # Capture the frame at the current time
    capture_frame $current_time
done
```
It took multiple rounds of prompting to figure this out - the most relevant transcripts are [this one from ChatGPT](https://chat.openai.com/share/1c6f907c-816e-497c-bf91-6cb930cc45a1) and [this one from Opus](https://gist.github.com/simonw/42e5a0e4d80785d7595db75faa11534c).

The frames it produced are a good combination of quality and filesize. Here's one, which is an 80KB JPEG:

![Frame from a video, showing a slide image displayed in a Firefox window](https://static.simonwillison.net/static/2024/frame_000023.jpg)
