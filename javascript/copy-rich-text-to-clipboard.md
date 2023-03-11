# Copy rich text to the clipboard

I've been experimenting with a tool for generating the content for a weekly Substack newsletter by querying the Datasette API for my blog and assembling HTML for the last week of content.

I haven't started sending this out yet, but I figured out how to write rich text to the clipboard as part of my initial prototype.

Substack allows you to paste in rich text (e.g. copied-and-pasted rendered HTML), so it's useful to be able to programatically add rich text to the user's clipboard in order to conveniently paste into Substack.

Initially I tried to get this working using the new [Clipboard.write()](https://developer.mozilla.org/en-US/docs/Web/API/Clipboard/write), but I spotted this warning on the [Interact with the clipboard](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Interact_with_the_clipboard) page of MDN:

> However, while `navigator.clipboard.readText()` and `navigator.clipboard.writeText()` work on all browsers, `navigator.clipboard.read()` and `navigator.clipboard.write()` do not. For example, on Firefox at the time of writing, `navigator.clipboard.read()` and `navigator.clipboard.write()` are not fully implemented, such that to:
>
> - work with images use `browser.clipboard.setImageData()` to write images to the clipboard and `document.execCommand("paste")` to paste images to a webpage.
> - write rich content (such as, HTML, rich text including images, etc.) to the clipboard, use `document.execCommand("copy")` or `document.execCommand("cut")`. Then, either `navigator.clipboard.read()` (recommended) or `document.execCommand("paste")` to read the content from the clipboard.

This is a bit tough to read, but the TLDR version is that for rich text copying in Firefox the `.write()` method doesn't work properly yet.

I actually pasted the above code into ChatGPT as a clue and got it to write me the following code, which I then tidied up and added the `document.body.appendChild()` and `document.body.removeChild()` lines (it failed without them):

```javascript
function copyRichText(html) {
    const htmlContent = html;
    // Create a temporary element to hold the HTML content
    const tempElement = document.createElement("div");
    tempElement.innerHTML = htmlContent;
    document.body.appendChild(tempElement);
    // Select the HTML content
    const range = document.createRange();
    range.selectNode(tempElement);
    // Copy the selected HTML content to the clipboard
    const selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
    document.execCommand("copy");
    selection.removeAllRanges();
    document.body.removeChild(tempElement);
}
```
## In an Observable notebook

I used this to add a "copy" button to my Observable notebook like this:
```javascript
Object.assign(html`<button>Copy rich text newsletter to clipboard`, {
  onclick: () => {
    const htmlContent = newsletterHTML;
    // Create a temporary element to hold the HTML content
    const tempElement = document.createElement("div");
    tempElement.innerHTML = htmlContent;
    document.body.appendChild(tempElement);
    // Select the HTML content
    const range = document.createRange();
    range.selectNode(tempElement);
    // Copy the selected HTML content to the clipboard
    const selection = window.getSelection();
    selection.removeAllRanges();
    selection.addRange(range);
    document.execCommand("copy");
    selection.removeAllRanges();
    document.body.removeChild(tempElement);
  }
})
```
This depends on some other cell defining `newsletterHTML` as a string of HTML.

Here's [the notebook](https://observablehq.com/d/81869763464a0735) that uses that.
