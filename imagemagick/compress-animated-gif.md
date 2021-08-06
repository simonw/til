# Compressing an animated GIF with ImageMagick mogrify

Found this tip [on Stack Overflow](https://stackoverflow.com/a/47343340/6083): to reduce the site of an animated GIF, you can use the `mogrify` tool like this:

    mogrify -layers 'optimize' -fuzz 7%  sqlite-convert-demo.gif

This saves over the original, so make a copy of it first.

I ran this against this 1.3MB animated GIF:

![A demo of my sqlite-utils convert command](https://static.simonwillison.net/static/2021/sqlite-convert-demo-raw.gif)

The result was this 401KB GIF:

![Same demo of my sqlite-utils convert command, but a smaller file](https://static.simonwillison.net/static/2021/sqlite-convert-demo.gif)

The `-fuzz 7%` option is [documented here](https://imagemagick.org/script/command-line-options.php#fuzz) - it treats similar colours as the same colour:

> The distance can be in absolute intensity units or, by appending % as a percentage of the maximum possible intensity (255, 65535, or 4294967295).
