# Converting ORF raw files to JPEG on macOS

One of our cameras takes raw photos in ORF format, which I believe stands for "Olympus Raw Format". Here's a recipe I found for converting them to JPEG on macOS:

```bash
brew install dcraw imagemagick

mkdir -p jpegs
for f in *.ORF; do
  dcraw -c "$f" | magick -quality 90 - jpegs/"${f%.*}.jpg"
done
```
The result is a `jpegs/` directory containing a `.jpg` file for every one of the `.ORF` files.
