# Compressing an animated GIF with gifsicle or ImageMagick mogrify

## Using gifsicle

Tip via Mark Norman Francis [on Twitter](https://twitter.com/cackhanded/status/1423526489623044098):

> Saw your GIF size TIL, and `gifsicle -O3 --colors 48 --lossy` gets it down to 320k. You can tweak the number of colours and loss to get it smaller but that’s when it starts to look worse to my eyes

I installed it using `brew install gifsicle` and ran it like this:

```
/tmp % ls -lah datasette-launch.gif 
-rw-r--r--@ 1 simon  wheel   3.7M Sep 13 12:52 datasette-launch.gif
/tmp % gifsicle -O3 --colors 48 --lossy -o datasette-launch-smaller.gif datasette-launch.gif 
/tmp % ls -lah datasette-launch*                                                            
-rw-r--r--  1 simon  wheel   613K Sep 13 12:54 datasette-launch-smaller.gif
-rw-r--r--@ 1 simon  wheel   3.7M Sep 13 12:52 datasette-launch.gif
```

Original: 3.7MB file:

![datasette-launch](https://user-images.githubusercontent.com/9599/133148193-89a01999-7fb4-407c-bb02-2bc79a70bd44.gif)

Compressed 613KB file:

![datasette-launch-smaller](https://user-images.githubusercontent.com/9599/133148197-e52db60d-442d-4db3-bf7c-28d5579e3b8a.gif)

The reduced colours there were a bit too much for me, especially for the purple gradient buttons at the end. So I tried this instead:

```
gifsicle -O3 --colors 128 --lossy -o datasette-launch-smaller-2.gif datasette-launch.gif
```
Which gave me a 723KB file which I think looks good enough for my purposes:

![datasette-launch-smaller-2](https://user-images.githubusercontent.com/9599/133148592-b98d5e78-f7fa-49e5-84d3-7c257c0bff17.gif)

## Using ImageMagick mogrify

Found this tip [on Stack Overflow](https://stackoverflow.com/a/47343340/6083): to reduce the site of an animated GIF, you can use the `mogrify` tool like this:

    mogrify -layers 'optimize' -fuzz 7%  sqlite-convert-demo.gif

This saves over the original, so make a copy of it first.

I ran this against this 1.3MB animated GIF:

![A demo of my sqlite-utils convert command](https://static.simonwillison.net/static/2021/sqlite-convert-demo-raw.gif)

The result was this 401KB GIF:

![Same demo of my sqlite-utils convert command, but a smaller file](https://static.simonwillison.net/static/2021/sqlite-convert-demo.gif)

The `-fuzz 7%` option is [documented here](https://imagemagick.org/script/command-line-options.php#fuzz) - it treats similar colours as the same colour:

> The distance can be in absolute intensity units or, by appending % as a percentage of the maximum possible intensity (255, 65535, or 4294967295).
