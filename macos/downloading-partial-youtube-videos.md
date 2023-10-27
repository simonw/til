# Downloading partial YouTube videos with ffmpeg

I spoke [at WordCamp US 2023](), and wanted to grab a copy of the video of my talk. I always try to keep my own copies of these because I've seen some conferences eventually take these offline in the past.

My presentation was livestreamed through YouTube, but the resulting livestream video [is 9.5 hours long](https://www.youtube.com/watch?v=LpDulftMkew)!

Normally I would download the full video and trim it locally, but I was on conference WiFi and didn't want to wait for the whole file - so I decided to see if it was possible to download just a subset.

I found [this recipe](https://unix.stackexchange.com/questions/230481/how-to-download-portion-of-video-with-youtube-dl-command/388148#388148) by [godofgrunts](https://unix.stackexchange.com/users/248065/godofgrunts) on StackExchange which looked like what I wanted:
```bash
#!/bin/bash
#Arguments: URL, Time stamp -5 seconds, length of clip, video file name

readarray -t urls <<< "$(yt-dlp --youtube-skip-dash-manifest -g "$1")"
ffmpeg -ss $2 -i "${urls[0]}" -ss $2 -i "${urls[1]}" -ss 5 -map 0:v -map 1:a -c:v libx264 -c:a aac -t $3 $4
```
But when I ran it I got an error, because `readarray` wasn't available on my Mac.

So I pasted it into GPT-4 with the prompt:

> Port this to macOS - I do not have the readarray command

It gave me back this:
```bash
#!/bin/bash
# Arguments: URL, Time stamp -5 seconds, length of clip, video file name

IFS=$'\n' urls=($(yt-dlp --youtube-skip-dash-manifest -g "$1"))
ffmpeg -ss $2 -i "${urls[0]}" -ss $2 -i "${urls[1]}" -ss 5 -map 0:v -map 1:a -c:v libx264 -c:a aac -t $3 $4
```

> 1. The IFS variable is set to a newline character, ensuring that the URLs returned by yt-dlp are split on new lines.
> 2. The urls array is populated using command substitution and array assignment.
> 3. The rest of the script remains unchanged.

I saved that as `clip-youtube.sh` and ran `chmod 755 clip-youtube.sh` and... it worked!

I called it like this:
```
./clip-youtube.sh 'https://www.youtube.com/watch?v=LpDulftMkew' 8:18:25 3600 simon-wordcamp.mp4
```
My section of the video starts at around 8h 18m and 25s. I specified 3600 to grab on hour of content (the Q&A went a bit over that, I should have specified more).

It took nearly a full hour for the script to run! It may have been faster to download the whole file and cut it up after all.

But... the result was a 308MB `simon-wordcamp.mp4` file.

## How that all works

Breaking this down a bit. The first part is this:

```bash
yt-dlp --youtube-skip-dash-manifest -g "$1"
```
Running that to see the output:
```bash
yt-dlp --youtube-skip-dash-manifest -g 'https://www.youtube.com/watch?v=LpDulftMkew'
```
Output:
```
https://rr2---sn-8xgp1vo-p5qs.googlevideo.com/videoplayback?expire=1693085635&ei=YxvqZJ2RJb6t_9EPwuSgkAk&ip=65.201.185.136&id=o-AAyFKyoRtQrnNL3zrfdNULpm39lectAVHkcbeoAF2jLI&itag=137&source=youtube&requiressl=yes&mh=Vv&mm=31%2C26&mn=sn-8xgp1vo-p5qs%2Csn-ab5l6nkd&ms=au%2Conr&mv=m&mvi=2&pcm2cms=yes&pl=21&initcwndbps=1816250&vprv=1&svpuc=1&mime=video%2Fmp4&gir=yes&clen=2674985800&dur=34334.996&lmt=1693003267530862&mt=1693063539&fvip=1&keepalive=yes&fexp=24007246&c=IOS&txp=7209224&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cvprv%2Csvpuc%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=AOq0QJ8wRAIgDzk4tc_9bCUvwN0Wg_73hJdAJHl2CDJW8ntEGmIu5HoCIH6u9T8EZSnITAln8Ebh6Vt_P17x3sKbecFfwdkH7AKP&lsparams=mh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpcm2cms%2Cpl%2Cinitcwndbps&lsig=AG3C_xAwRAIgFZ9mdd4hTdBnDCn0DhbbOkgCLsKQbaoI8eFU3SDBiAYCIHIwpPwy8LfmGv1sNezegCuIQ8f5OZV-J1pBYYZ6Spxi
https://rr2---sn-8xgp1vo-p5qs.googlevideo.com/videoplayback?expire=1693085635&ei=YxvqZMPFMYmi_9EP1YOsqA4&ip=65.201.185.136&id=o-AJrteXKDNXZVv-8ohwCNtkgRusvA7tjSCrK-Yhvj13FZ&itag=251&source=youtube&requiressl=yes&mh=Vv&mm=31%2C26&mn=sn-8xgp1vo-p5qs%2Csn-ab5sznzk&ms=au%2Conr&mv=m&mvi=2&pl=21&initcwndbps=1816250&spc=UWF9f2Mp7IK_PwGaM7XhKZtnkS6X3I4&vprv=1&svpuc=1&mime=audio%2Fwebm&gir=yes&clen=318551384&dur=34335.041&lmt=1693003946161041&mt=1693063539&fvip=1&keepalive=yes&fexp=24007246%2C51000023&beids=24350017&c=ANDROID&txp=7208224&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cspc%2Cvprv%2Csvpuc%2Cmime%2Cgir%2Cclen%2Cdur%2Clmt&sig=AOq0QJ8wRQIhAK--nt8-f1qPpaG1ioc5I2gQLEVD5sCFCUh6fjruOHPUAiAWz0o0kOhS-M--vPkNWD0ZqdSguD5lxFxwLu46Zgb5jw%3D%3D&lsparams=mh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AG3C_xAwRQIgWmu0j9lq5uhkxVkOfUK4cctQbhgwMcU1stpCvLNYBB4CIQCMt0PzKQ5T9ofUxoIYywGN_fE72dMvPuoEvJZr4jOwJg%3D%3D
```
I dug around a bit and it turned out `--youtube-skip-dash-manifest` is no longer necessary. So this is really:
```bash
yt-dlp -g 'https://www.youtube.com/watch?v=LpDulftMkew'
```
The `-g` option causes `yt-dlp` to produce the URL to the streams rather than downloading the video.

It returns two URLs because the first one is the video stream and the secand is the audio stream. We can reformat those URLs to spot that more clearly - the clue is the `&mime=video%2Fmp4` in the first compared to `&mime=audio%2Fwebm` in the second.

Then it calls `ffmpeg`. Here's a tidied version of that call:
```bash
ffmpeg \
  -ss '8:18:25' -i "${VIDEO_STREAM_URL}" \
  -ss '8:18:25' -i "${AUDIO_STREAM_URL}" \
  -ss 5 \
  -map 0:v \
  -map 1:a \
  -c:v libx264 \
  -c:a aac \
  -t 3600 simon-wordcamp.mp4
```
The two `-ss` lines seek the video stream and the audio stream to the `8:18:25` mark.

`-ss 5` seeks 5 seconds into the combined output. The instructions on StackExchange said to start at least 5s before the section of the video that you want to capture. The StackExchange recipe says this is for "giving me a few seconds to catch a good keyframe".

`-map 0:v` and `-map 1:a` sets the first stream up as video and the second stream as audio.

`-c:v libx264` and `-c:a aac` configure the output codecs for video (H.264 video) and audio (AAC).

`-t 3600 simon-wordcamp.mp4` sets the duration to an hour (60 * 60 seconds) and specifies the output file.
