# Syncing slide images and audio in iMovie

I found an MP3 recording of an old talk I gave and decided to use the slides from that talk to create a video using iMovie.

The slides were in Keynote, so I started by exporting them to individual images:

    File -> Export To -> Images...

<img width="664" alt="Screenshot of the Export your Presentation screen" src="https://github.com/simonw/til/assets/9599/8f07a00f-8317-4801-a437-856a24af69c9">

I then imported the images into iMovie by dragging and dropping the whole pile of them from the finder.

I dragged and dropped in my MP3 recording too.

## Turning off the Ken Burns effect

When you import images into iMovie it applies the Ken Burns zoom effect to them by default, which wasn't what I wanted.

To get rid of this you need to use the "Crop" tool (unintuitively). Select all of the images, click the "Crop" icon, then set the Style to "Fill".

<img width="627" alt="Screenshot showing where the crop icon is" src="https://github.com/simonw/til/assets/9599/dce15ef6-d4fa-447c-9ba0-dfa435ff5101">

## Syncing the audio

I wanted each slide to be on screen for the correct duration to match the audio.

At first I tried dragging and dropping the edges of the images, but this was way too fiddly.

Instead, I decided to manually alter the duration of each one.

I did this by selecting each image in turn, clicking the little (i) icon and manually editing the duration in seconds.

<img width="1317" alt="Screenshot of a iMovie edit timeline showing the form for editing the duration of an image" src="https://github.com/simonw/til/assets/9599/56f647cc-b048-44d8-ba88-039d41314884">

This was faster than I expected - I quickly got a feel for if I should jump the duration up to 8s or 10s and then tweaked those numbers by hitting the play and pause buttons.

## Publishing it to YouTube

I exported the result using the `File -> Share -> File...` menu. Despite the 1.03GB estimate the video ended up being 259.8MB - presumably because it was mostly static images.

<img width="768" alt="I used the default settings: 1080p, Quality High, Compress for Better Quality" src="https://github.com/simonw/til/assets/9599/5c946816-8dd1-43e0-939c-b0bb58e78096">

I created a custom title slide image for it because YouTube likes those to be 1280x720px - I used Pixelmator for that.

The completed video is here: <https://www.youtube.com/watch?v=omobajJmyIU>
