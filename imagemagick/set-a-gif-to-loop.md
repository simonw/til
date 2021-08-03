# Set a GIF to loop using ImageMagick

I managed to accidentally create a GIF that ran once without looping. I think this is because I created it in [LICEcap](https://www.cockos.com/licecap/) but then deleted some frames and re-saved it using macOS Preview.

I used ImageMagick to get it to loop like this:

    convert chrome-samesite-missing.gif -loop 0 chrome-samesite-missing-loop.gif

Note that the output filename comes last, AFTER the `-loop 0` option.

I installed ImageMagick on macOS using `brew install imagemagick`

Here's the before GIF:

![This loops once](https://static.simonwillison.net/static/2021/chrome-samesite-missing.gif)

And the after GIF:

![This loops forever](https://static.simonwillison.net/static/2021/chrome-samesite-missing-loop.gif)
