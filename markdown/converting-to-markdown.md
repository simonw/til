# Converting HTML and rich-text to Markdown

If you copy and paste from a web page - including a full table - into a GitHub issue comment GitHub converts it to the corresponding Markdown for you. Really quick way to construct Markdown tables.

![GitHub converting to Markdown](https://raw.githubusercontent.com/simonw/til/main/markdown/converting-to-markdown.gif)

https://mixmark-io.github.io/turndown/ is an open source JavaScript library by Dom Christie that can convert HTML strings into Markdown strings. Code: https://github.com/mixmark-io/turndown - it used to be called `to-markdown` and lived at `domchristie.github.io/turndown`, which now 404s.

https://euangoddard.github.io/clipboard2markdown/ is a tool which lets you paste in rich-text and uses turndown to convert it for you directly in your browser.

## 2md, explained

https://2md.ca/ is another tool that does this, written in TypeScript. It's accompanied by [a detailed essay](https://2md.ca/how-it-works) explaining exactly how it works.
