# Livestreaming a community election event on YouTube

I live in El Granada, California. Wikipedia calls us [a census designated place](https://en.wikipedia.org/wiki/El_Granada,_California) - we don't have a mayor or city council. But we do have a [Community Services District](https://granada.ca.gov/) - originally responsible for our sewers, and since 2014 also responsible for our parks. And we get to vote for the board members [in the upcoming November election](https://granada.ca.gov/2024-candidate-listing)!

My partner Natalie decided to arrange a "candidates forum" - effectively a debate between three of the candidates running for the two open seats on the board. I was recruited to help record and livestream the event on YouTube.

We had an outdoor venue (at [Jettywave Distillery](https://www.jettywave.com/)). I've never livestreamed an event that wasn't just me sharing the screen of my laptop before - here are my notes on what I did, what worked and what didn't.

## Equipment

I ended up using:

- An iPhone 15 Pro as the camera, on a stand
- A Mac M2 laptop to run the stream
- A RØDE Wireless GO II kit (two microphones, one receiver) for audio
- Firefox for the first half, then Chrome for the second

I originally planned to stream directly from the iPhone but it turns out YouTube don't allow newly created channels to stream via a mobile device for some reason.

Thanks to the Apple [Continuity Camera](https://support.apple.com/en-us/102546) this wasn't a problem at all: I could stream from my laptop but use my iPhone as the camera for it.

## Audio

I decided to get a RØDE Wireless GO II kit after using one to record [a podcast episode](https://www.latent.space/p/devday-2024) with swyx and crew a few weeks ago. It comes as two tiny lapel mic transmitters and a small receiver that plugs into the laptop (or phone) via USB-C.

I tried a few setups for the mics. The venue had its own A/V system so my first idea was to put one of my microphones next to a speaker. This worked OK, but then I realized that since we had two hand-held microphones for the participants I could tape my little RØDE mics directly to those and capture audio that way. This worked great!

## Streaming

Starting a YouTube stream through their web interface on a laptop was pretty straight-forward. I had to give the stream a name, set it as "Not for kids", select the camera (my iPhone) and microphone (the RØDE receiver) and start streaming.

It took me a little while to figure out how best to control the camera. It turns out you can both zoom in and pan around the image on the iPhone using this interface which shows up in the menu bar:

<img alt="Camera control menu. A video preview shows with a 1.6x zoom option displayed, coming from my iPhone on 65% battery. A bunch of other options such as Center Stage, Portrait, Studio Light, Reactions and Background are shown as well." src="https://static.simonwillison.net/static/2024/camera-controls.jpg" width="400">

The video preview starts as just a moving image - you have to click on it to get the controls to show up, and if you zoom in by interacting with the overlay you can then pan around the image by dragging the preview.

## Firefox crashed! I switched to Chrome

I started running the stream from Firefox. This seemed to be working just fine, but it turns out that about 45 minutes into the first stream Firefox stopped transmitting audio (leaving an embarassing audio-free segment in the [final video](https://www.youtube.com/watch?v=MolqZq9ij2c)), and then crashed entirely with macOS complaining that it was using around 150GB of RAM!

With hindsight, I could have had the RØDE microphones record audio directly onto their own storage as a backup. I'll definitely do that next time.

I assumed YouTube were more stringent with their Chrome testing than their Firefox testing, so I switched to Chrome for the second half of the event - [video here](https://www.youtube.com/watch?v=GHtMbhG9EIU) - and kept an eye on its memory usage in Activity Monitor. That worked fine.

**Lesson learned:** For this kind of event, losing audio is worse than losing video. Just because test streams that were 5 minutes long worked fine doesn't mean that an hour long stream won't run into unexpected problems. There's a reason the RØDE microphon's have the option to create their own audio backups!

## Embedding the video

I tried embedding the YouTube live video on our [coastsidecivic.com](https://coastsidecivic.com/) website for the duration of the event, but the iframe showed a message saying that the owner of the video had disallowed embedding.

I didn't think I had, but it took me quite a while to track down the default-off option in the livestream settings (confusing beacuse normal videos defaulted to on):

![Edit settings panel - deep in the Details panel at the bottom is an Allow embedding checkbox](https://static.simonwillison.net/static/2024/youtube-embedding.jpg)

Once  I'd checked this option embedding the livestream video worked just fine. I used this HTML:

```html
<iframe style="
    width: 100%;
    aspect-ratio: 560 / 315;
    height: auto;" width="560" height="315"
    src="https://www.youtube.com/embed/GHtMbhG9EIU"
    frameborder="0" allowfullscreen="">
</iframe>
```
That `aspect-ratio` trick gave me the video at the correct dimensions even when it expanded to fill 100% of available width.

## Fixing the audio

After publishing we noticed that the audio in the part 1 (but not the part 2) video was uneven: the microphone for the candidates had produced much quieter audio. I don't know why that wasn't a problem in the second video.

I ended up downloading the YouTube video, extracting the audio and using the [auto-leveller tool](https://auphonic.com/features#leveler) from [auphonic.com](https://auphonic.com/) to automatically fix this.

YouTube doesn't let you replace the full audio for a video OR replace the video itself, so I combined the previous video and the new audio using `ffmpeg` and then uploaded a fresh video, then set the previous video to "unlisted" and placed a link to the new one in the old one's description.

[Original video](https://www.youtube.com/watch?v=MolqZq9ij2c) / [Video with fixed audio](https://www.youtube.com/watch?v=nG-vNJmqZ3o) - the change is most obvious from about 8 minutes in.

Here's the `ffmpeg` command I used:

```bash
ffmpeg -i "GCSD Candidates Forum - Part 1.mp4" \
  -i "part1-auphonic-loudness-normalization.mp3" \
  -c:v copy -map 0:v:0 -map 1:a:0 -shortest "part1-audio-fixed.mp4
```
I figured that out using [llm-cmd](https://github.com/simonw/llm-cmd) like this:

`llm cmd use ffmpeg to combine the video from GCSD\ Candidates\ Forum\ -\ Part\ 1.mp4 with the audio from part1-auphonic-loudness-normalization.mp3 and save the output as part1-audio-fixed.mp4`
