# Using the tesseract CLI tool

Tesseract OCR has a command-line utility which is woefully under-documented. Thanks to [Alexandru Nedelcu](https://alexn.org/blog/2020/11/11/organize-index-screenshots-ocr-macos.html) I figured out how to use it today.

To install on macOS:

    brew install tesseract

To convert an image into an annotated PDF (which you can then copy and paste text out of, and which will be correctly indexed by Spotlight):

    tesseract image.png output-file -l eng pdf
    
The second `output-file` argument there is the path and filename of the output - note that I didn't include a `.pdf` extension because Tesseract adds that automatically - so the output will be in a file called `output-file.pdf`.

To get out just the plain text:

    tesseract image.png output-file -l eng txt
