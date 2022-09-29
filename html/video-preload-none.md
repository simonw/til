# HTML video that loads when the user clicks play

Today I figured out how to use the `<video>` tag to show a static thumbnail that gets replaced by the loaded video only when the user clicks play.

This is useful if you are going to show multiple video players on a page at the same time, as I do [on webvid.datasette.io](https://webvid.datasette.io/webvid/videos) ([described here](https://simonwillison.net/2022/Sep/29/webvid/)).

```html
<video controls
  width="400"
  preload="none"
  poster="https://ak.picdn.net/shutterstock/videos/172/thumb/1.jpg?ip=x480"
>
  <source
    src="https://ak.picdn.net/shutterstock/videos/172/preview/stock-footage-furnace-chimney.mp4"
    type="video/mp4"
  >
</video>
```
- `preload="none"` causes the browser to not preload the video until the user hits play.
- `poster="..."` provides an image thumbnail to show in the player when it first loads

More information: [MDN guide to the Video element](https://developer.mozilla.org/en-US/docs/Web/HTML/Element/video)
