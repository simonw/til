# HTML video with subtitles

Via [Mariatta](https://fosstodon.org/@mariatta/112883308634473940) I found my [PyVideo speaker page](https://pyvideo.org/speaker/simon-willison.html), and thanks to that page I learned that a talk I gave in 2009 had been rescued from the now-deceased [Blip.tv](https://en.wikipedia.org/wiki/Blip.tv) and is now hosted by the Internet Archive:

[Cowboy Development with Django](https://archive.org/details/pyvideo_24___cowboy-development-with-django) from DjangoCon 2009.

I grabbed a copy of the MP4 and ran it through [MacWhisper](https://goodsnooze.gumroad.com/l/macwhisper) to generate a transcript for my own records... and then I decided to ask Claude what my options would be for hosting my own copy of that video along with generated subtitles.

Claude suggested WebVTT, and gave me the following example HTML when I asked:

```html
<video controls>
  <source src="path/to/your/video.mp4" type="video/mp4">
  <track label="English" kind="subtitles" srclang="en" src="path/to/your/subtitles-en.vtt" default>
  <track label="Español" kind="subtitles" srclang="es" src="path/to/your/subtitles-es.vtt">
  Your browser does not support the video tag.
</video>
```

MacWhisper has an export as VTT option, so I used that and got this file:

https://static.simonwillison.net/static/2010/24_cowboy-development-with-django.vtt

It looks like this:
```
WEBVTT

00:00:00.000 --> 00:00:02.560
Now and then, I'd like to invite to the stage Simon Willison,


00:00:02.560 --> 00:00:06.120
who very kindly has offered to fill in the space
```
It turns out fetching VTT files is governed by CORS rules, so you need to host the HTML on the same domain as the VTT file (or use CORS headers). Here's a demo page with the MP4 video and those VTT files:

https://static.simonwillison.net/static/2010/24_cowboy-development-with-django.html

```html
<video controls>
  <source src="https://static.simonwillison.net/static/2010/24_cowboy-development-with-django.mp4" type="video/mp4">
  <track label="English" kind="subtitles" srclang="en" src="https://static.simonwillison.net/static/2010/24_cowboy-development-with-django.vtt" default>
  Your browser does not support the video tag.
</video>
```

It totally works! Here's a screenshot in Firefox:

![Screenshot of a video player, at 11:52 through the video showing the subtitles "In 2009, they quietly tried to pass a law saying they were exempt from the Freedom of Information Act](https://github.com/user-attachments/assets/8bf09466-d063-4599-8fa9-e38a5d22a0e5)
