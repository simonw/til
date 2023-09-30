# Understanding the CSS auto-resizing textarea trick

Chris Coyier [wrote about](https://chriscoyier.net/2023/09/29/css-solves-auto-expanding-textareas-probably-eventually/) the new `form-sizing: normal` property, which can get a `<textarea>` to automatically expand to fit its content - but currently only in Google Chrome Canary. Chris also linked to [his own favourite trick](https://codepen.io/chriscoyier/pen/XWKEVLy) for doing that, using some CSS grid trickery.

I decided to dig into that grid trick and figure out how it works, as well as adapt it slightly for my own preferences.

Here are [the changes I made to the CSS and HTML](https://gist.github.com/simonw/6815f73098c803e31fcd20059318b937/revisions). I'll describe my finished, adapted version of the trick below.

## The finished effect

The goal here is to build a `<textarea>` that expands in height as more content is added to it.

I had an extra goal: I wanted it to start out as a single line of text, then expand to a `<textarea>` should the user hit the enter key.

I should mention that the jury is out on whether or not this is a good idea: users may expect that if they hit enter in a single-line input, they will submit the form. But I want to try it out anyway!

You can [try the final effect here](https://til.simonwillison.net/tools/resizing-textarea). Here's an animated GIF demo:

![As text is typed into the textarea the textarea expands in height to fit](https://static.simonwillison.net/static/2023/resizing-textarea.gif)


## The HTML

I'm using the same as HTML as Chris, with two tweaks: I added `rows="1"` to start it at the height of a single line, and I dropped in a `placeholder="Placeholder shows here"` to see what a placeholder would look like:

```html
<form>
  <label for="text">Textarea label:</label>
  <div class="grow-wrap">
    <textarea
      rows="1"
      name="text"
      placeholder="Placeholder shows here"
      id="text"
      onInput="this.parentNode.dataset.replicatedValue = this.value"></textarea>
  </div>
</form>
```

The critical trick here is from Chris: that `onInput=` attribute has JavaScript that ensures that any time the `<textarea>` value changes, the `data-replicated-value` attribute on the parent `<div>` is updated to match the textarea's value.

## The CSS

This is where things get clever.

Our goal here is to have the `<textarea>` visibly increase in size to fit its content.

We can do that using CSS grid. Here's a heavily commented version of the CSS:

```css
.grow-wrap {
  /* This is the wrapper element around the `<textarea>` */
  display: grid;
}
```
This sets the `<div class="grow-wrap">` element up as a CSS grid container, so elements inside it will be positioned using CSS grid.

```css
/* ::after adds a pseudo-element inside, after the `<textarea>` */
.grow-wrap::after {
  /* Note the weird space! Needed to prevent jumpy behavior */
  content: attr(data-replicated-value) " ";

  /* This is how `<textarea>` text behaves */
  white-space: pre-wrap;

  /* Hidden from view, clicks, and screen readers */
  visibility: hidden;
}
```
This is the really clever bit. Using `::after` adds a pseudo-element inside the `<div class="grow-wrap">` element, directly after the textarea.

The `content: attr(data-replicated-value) " "` CSS rule means that the content of this pseudo-element will be the value of the `data-replicated-value` attribute on the parent element.

This means that any time the `<textarea>` content changes, the JavaScript will update that `data-replicated-value` attribute and the text content inside that pseudo-element will change too - which modifies its height.

Chris has a comment about that weird space. I tried removing it and here's the jumpiness that results:

![As text is typed into the textarea the textarea jumps up and down in size](https://static.simonwillison.net/static/2023/auto-resize-jumpy-2.gif)

The textarea doesn't extend in height when you hit newline and are focused on a blank row - you have to type at least one character for it to adjust its size.

That `white-space: pre-wrap` rule causes that content to behave the same as content in a `<textarea>` - spaces and newlines will be preserved. This should keep the hidden pseudo-element the same physical size as the textarea.

Finally, the `visibility: hidden` rule means that the pseudo-element is not visible on the page.

Next, some extra styles for the `<textarea>`:

```css
.grow-wrap > textarea {
  /* You could leave this, but after a user resizes, then it ruins the auto sizing */
  resize: none;

  /* Firefox shows scrollbar on growth, you can hide like this. */
  overflow: hidden;
}
```
The comments here explain what's going on. I tried removing `overflow: hidden` to see what would happen in Firefox - this is what that looked like:

![As text is typed into the textarea each time a newline is added a vertical scrollbar appears for a moment and then vanishes again](https://static.simonwillison.net/static/2023/auto-resize-firefox.gif)

Finally, the styles that apply to both the `<textarea>` and the `::after` pseudo-element:

```css
.grow-wrap > textarea,
.grow-wrap::after {
  /* Identical styling required!! */
  border: 1px solid black;
  border-radius: 3px;
  padding: 0.35rem;
  font: inherit;
  line-height: 1.4;
  font-family: sans-serif;

  /* textarea and ::after should occupy the first (and only) cell of the grid: */
  grid-area: 1 / 1 / 2 / 2;
}
```

These styles apply to both the `<textarea>` and the invisible pseudo-element. They need to be identical to ensure that the invisible pseudo-element accurately reflects the size of the textarea.

I tweaked these a little bit from Chris's version: I added a border-radius and tweaked the padding.

That last `grid-area: 1 / 1 / 2 / 2` line deserves some explanation. This is a shorthand for setting the following four CSS properties:
```css
  grid-row-start: 1;
  grid-column-start: 1;
  grid-row-end: 2;
  grid-column-end: 2;
```
This actually means "you occupy the first cell of the grid" - from the leading edge of the first row to the leading edge of the second row, and from the leading edge of the first column to the leading edge of the second column.

Since this CSS is applied to both the `<textarea>` and the `::after` pseudo-element, this is saying that they both occupy the first (and only) cell.

A CSS grid cell will expand to fit its largest content, so that invisible pseudo-element will influence the size of it. Then the `<textarea>` will expand to fit the size of the cell.

It's a really clever hack!

## One extra piece of JavaScript

A neat thing about this solution is that the JavaScript is entirely contained in that single `onInput` attribute in the HTML.

But... I found a limitation. Some browsers preserve the contents of a `<textarea>` if you click forward and backward... but if the page loads and the `<textarea>` has multiple lines of content, the `data-replicated-value` attribute won't be set until you make another edit to it.

So I added this to the bottom of the page:

```javascript
document.querySelectorAll('textarea').forEach(el => {
  el.dispatchEvent(new Event('input', {
    bubbles: true,
    cancelable: true
  }));
});
```
This snippet loops through every `<textarea>` element on the page and dispatches an artificial `input` event on it - which triggers our `onInput=` attribute and updates the `data-replicated-value` attribute, which then updates the size of the accompanying pseudo-element.

This also means that if you load the page with a value already in the `<textarea>` (on an edit screen for example) it will resize to fit that content.

## Persisting the textarea value

To help show that this was working I added some code to persist and load the `<textarea>` value from `localStorage`:

```javascript
const KEY = 'resizeTextareaContent';
const ta = document.querySelector('textarea');
function saveTextarea() {
  localStorage.setItem(KEY, ta.value);
}
const saved = localStorage.getItem(KEY);
if (saved && !ta.value) {
  ta.value = saved;
}
ta.addEventListener('input', saveTextarea);
```
## A custom focus outline

I added one last piece of CSS, to modify the outline effect that displays when the `<textarea>` is focused:

```css
textarea:focus {
  outline: none;
  box-shadow: inset 0 0 2px navy;
}
```
Here's what it looks like without that:

![The textarea has a bold blue outline surrounding it](https://static.simonwillison.net/static/2023/more-outline.png)

And with it:

![The textarea has a more subtle blue inset shadow](https://static.simonwillison.net/static/2023/less-outline.png)
