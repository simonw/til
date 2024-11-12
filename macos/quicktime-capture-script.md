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

## A version that captures bounding box regions too

I gave a talk at a conference where the resulting video featured both my on-stage presence and a superimposed output from my screen.

I wanted to grab captures of both - a full screen capture, but also a capture that only showed what was on my screen at the time.

I got Claude to update my script for that ([first session](https://gist.github.com/simonw/799babf92e1eaf36a5336b4889f72492), [second session](https://gist.github.com/simonw/03b0cff88f9b9cbb7af879a07512bf6f)) resulting in this script:

```zsh
#!/bin/zsh

# Initialize array for storing bounding boxes
typeset -a bounding_boxes

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --box)
            if [[ $2 =~ ^[0-9]+,[0-9]+,[0-9]+,[0-9]+$ ]]; then
                # Validate coordinates are within 0-100 range
                local coords=(${(s:,:)2})
                local valid=true
                for coord in $coords; do
                    if (( coord < 0 || coord > 100 )); then
                        valid=false
                        break
                    fi
                done
                if $valid; then
                    bounding_boxes+=($2)
                else
                    echo "Error: Bounding box coordinates must be between 0 and 100"
                    exit 1
                fi
            else
                echo "Error: Invalid bounding box format. Use: --box 'x1,y1,x2,y2' where coordinates are percentages (0-100)"
                exit 1
            fi
            shift 2
            ;;
        *)
            video_filename=$1
            shift
            ;;
    esac
done

# Check if the video filename is provided
if [[ -z $video_filename ]]; then
    echo "Please provide the video filename as an argument."
    exit 1
fi

# Function to convert time in seconds to HH:MM:SS format
function seconds_to_hms {
    local total_seconds=$1
    local hours=$((total_seconds / 3600))
    local minutes=$(((total_seconds % 3600) / 60))
    local seconds=$((total_seconds % 60))
    printf "%02d:%02d:%02d\n" $hours $minutes $seconds
}

# Function to capture frame with optional bounding box
function capture_frame {
    local current_time=$1
    local bbox=$2
    local formatted_time=$(seconds_to_hms $current_time)
    
    # Base filename without bbox suffix
    local base_filename="frame_${formatted_time//:/}"
    
    if [[ -z $bbox ]]; then
        # Capture full frame
        local filename="${base_filename}.jpg"
        ffmpeg -y -ss $formatted_time -i "$video_filename" -frames:v 1 -f image2 "$filename"
        echo "Saved full frame to $filename"
    else
        # Capture cropped frame using the bounding box
        local coords=(${(s:,:)bbox})
        local x1=$coords[1]
        local y1=$coords[2]
        local x2=$coords[3]
        local y2=$coords[4]
        
        # Calculate width and height as percentages
        local width=$((x2 - x1))
        local height=$((y2 - y1))
        
        local filename="${base_filename}_bbox${x1}_${y1}_${x2}_${y2}.jpg"
        ffmpeg -y -ss $formatted_time -i "$video_filename" \
            -vf "crop=iw*${width}/100:ih*${height}/100:iw*${x1}/100:ih*${y1}/100" \
            -frames:v 1 -f image2 "$filename"
        echo "Saved cropped frame to $filename"
    fi
}

# Main loop
while true; do
    echo "Press any key to capture the current video frame..."
    read -sk 1 key

    # Use osascript to get the current time from QuickTime Player
    current_time=$(osascript -e 'tell application "QuickTime Player" to tell document 1 to get current time')

    # Capture the full frame first
    capture_frame $current_time
    
    # Then capture each bounding box if any were specified
    for bbox in $bounding_boxes; do
        capture_frame $current_time $bbox
    done
done
```

This can be run like so:

```bash
capture-bbox.sh ../output.mp4  --box '31,17,100,87' --box '0,0,50,50'
```
You can use the `--box` option 0 or more times. The output for each frame will then look like this:
```
frame_003844.jpg
frame_003844_bbox0_0_50_50.jpg
frame_003844_bbox31_17_100_87.jpg
```
That's the original frame and an image for each of the specified bounding box regions.

The `--bbox` format uses percentages along the width and height of the image.

I also [got Claude to build](https://gist.github.com/simonw/799babf92e1eaf36a5336b4889f72492#create-bounding-box-drawing-tool) a visual tool for selecting these. Drop a full screen frame from an image into this [Bounding Box Drawing Tool](https://tools.simonwillison.net/bbox-cropper) and drag the box to find out the correct `--box` setting:

![Screenshot showing a box dragged around a section of an image with a --box output below it](https://github.com/user-attachments/assets/71064215-d3b1-4b5a-b45e-2358f96a9459)

