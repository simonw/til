# Trying out Quarto on macOS

I decided to try out [Quarto](https://quarto.org/), the new notebook/markdown/publishing system built on Pandoc.

I followed their [Get started](https://quarto.org/docs/get-started/) guide and downloaded and installed the macOS installer.

Having run the installer, `quarto --help` showed that I had the CLI command installed.

## Setting up VS Code and solving ImportErrors

Next I installed the Quarto extension for VS Code by clicking the "Install" button on this page: https://marketplace.visualstudio.com/items?itemName=quarto.quarto

I started following the tutorial there, which worked... up until the point where I clicked "Render", when I got this error in the VS Code terminal:

```
ModuleNotFoundError: No module named 'nbformat'
```

This looked suspiciously to me like an [xkcd 1987](https://xkcd.com/1987/) problem: which of the many versions of Python on my computer was Quarto using? And why didn't that version have the right packages installed?

I figured out which Python was being used by adding this block to the tutorial Markdown file and executing it in VS Code:

````
```{python}
import sys
print(sys.executable)
```
````
This output:
```
/Applications/Xcode.app/Contents/Developer/usr/bin/python3
```
Now that I knew which Python was being used, I could install the `nbformat` and later the `nbclient` packages that the error messages were complaining about:

```
/Applications/Xcode.app/Contents/Developer/usr/bin/python3 -m pip install nbformat nbclient
```

Having installed those two packages into that particular Python instance, the "Render" button in VS Code worked and gave me a rendered PDF preview.
