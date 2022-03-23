# Exporting and editing a Twitter Spaces recording

I hosted [a Twitter Spaces conversation](https://twitter.com/simonw/status/1504604448202518529) the other day. The recording is only available for 30 days afterwards, and I wanted to publish it elsewhere.

## Exporting the recording

Right now [the only way](https://media.twitter.com/en/articles/products/2021/twitter-spaces/recorded-spaces) to export a recording is to request an export of your *entire* Twitter account, and then wait around 24 hours for the export to be generated.

I hoped I could instead hack around in my browser network panel to extract the audio, but it's served up as hundreds of smaller files so this wasn't feasible.

So I hit export, waited 24 hours and downloaded my 900MB archive zip file.

Within the zip file was a `spaces_media/` folder containing a 49.8MB `space-1ypKdEXvkMLGW_0.ts` audio recording.

## Converting that to mp3

I used `ffmpeg` (installed via `brew install ffmpeg`) to convert that file to an MP3:
```
spaces_media % ffmpeg -i space-1ypKdEXvkMLGW_0.ts space.mp3 
ffmpeg version 4.2.1 Copyright (c) 2000-2019 the FFmpeg developers
  built with gcc 9.2.0 (Alpine 9.2.0)
  configuration: --prefix=/usr --enable-avresample --enable-avfilter --enable-gnutls --enable-gpl --enable-libass --enable-libmp3lame --enable-libvorbis --enable-libvpx --enable-libxvid --enable-libx264 --enable-libx265 --enable-libtheora --enable-libv4l2 --enable-postproc --enable-pic --enable-pthreads --enable-shared --enable-libxcb --disable-stripping --disable-static --disable-librtmp --enable-vaapi --enable-vdpau --enable-libopus --disable-debug
  libavutil      56. 31.100 / 56. 31.100
  libavcodec     58. 54.100 / 58. 54.100
  libavformat    58. 29.100 / 58. 29.100
  libavdevice    58.  8.100 / 58.  8.100
  libavfilter     7. 57.100 /  7. 57.100
  libavresample   4.  0.  0 /  4.  0.  0
  libswscale      5.  5.100 /  5.  5.100
  libswresample   3.  5.100 /  3.  5.100
  libpostproc    55.  5.100 / 55.  5.100
[aac @ 0x7f59653ad180] Format aac detected only with low score of 25, misdetection possible!
[aac @ 0x7f59653ad180] Estimating duration from bitrate, this may be inaccurate
Input #0, aac, from 'space-1ypKdEXvkMLGW_0.ts':
  Metadata:
    TIT3            : 3856965984.391
    id3v2_priv.com.apple.streaming.transportStreamTimestamp: \x00\x00\x00\x01\xc9\xdd\xe3\x82
    JSONMetadata    : {"HydraVersion":4,"ntp":3856965984.391}
    HydraParticipants: []
    HydraAudioLevel : [0]
  Duration: 01:09:09.41, bitrate: 96 kb/s
    Stream #0:0: Audio: aac (LC), 48000 Hz, stereo, fltp, 96 kb/s
Stream mapping:
  Stream #0:0 -> #0:0 (aac (native) -> mp3 (libmp3lame))
Press [q] to stop, [?] for help
Output #0, mp3, to 'space.mp3':
  Metadata:
    TIT3            : 3856965984.391
    id3v2_priv.com.apple.streaming.transportStreamTimestamp: \x00\x00\x00\x01\xc9\xdd\xe3\x82
    JSONMetadata    : {"HydraVersion":4,"ntp":3856965984.391}
    HydraParticipants: []
    HydraAudioLevel : [0]
    TSSE            : Lavf58.29.100
    Stream #0:0: Audio: mp3 (libmp3lame), 48000 Hz, stereo, fltp
    Metadata:
      encoder         : Lavc58.54.100 libmp3lame
size=   59777kB time=01:03:45.69 bitrate= 128.0kbits/s speed=  56x    
video:0kB audio:59777kB subtitle:0kB other streams:0kB global headers:0kB muxing overhead: 0.000740%
```

## Editing the file

I wanted to make a *very* basic edit to the file - just to cut off the first six minutes.

I used QuickTime Player on my Mac to do this.

I opened the file in that application, then moved the play head to the point that I wanted to start the track and used `Edit -> Split Clip` to split the clip - then deleted the section before the split.

Then I used `File -> Export As -> Audio Only...` to export the audio. This gave me a `.m4a` file.

I uploaded that file directly [to SoundCloud](https://soundcloud.com/simon-willison/sqlite-happy-hour-22nd-march-2022).
