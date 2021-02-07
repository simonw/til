# Shrinking PNG files with pngquant and oxipng

I usually use [Squoosh.app](https://squoosh.app/) to reduce the size of my PNGs, but in this case I had a folder with nearly 50 images in it so I wanted to do it using the command-line.

[pngquant](https://pngquant.org/) can reduce the number of colours in a PNG image, which I find makes a huge differente to the file size (also possible using Squoosh).

[oxipng](https://github.com/shssoichiro/oxipng) is a performante lossless PNG compressor.

I got great results by running `pngquant` first, then `oxipng` on the results.

Both can be installed via Homebrew:

    brew install pngquant oxipng

Then I ran this command to reduce to a maximum of 50 colours per image:

    pngquant --quality 20-50 *.png

(I don't know if the lower bound of 20 is the right thing to do here, maybe `0-50` would be better?)

This creates a file called `x-fs8.png` for any file called `x.png`.

Then I ran this to apply `oxipng`:

    oxipng -o 3 -i 0 --strip safe *-fs8.png

The results were that a 383KB file dropped down to just 70KB. The images are visually different but the size savings are huge, which is particularly important if you plan to put 50+ images on a single web page.
