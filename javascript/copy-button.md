# Implementing a "copy to clipboard" button

I had to figure this out while building [datasette-copyable](https://github.com/simonw/datasette-copyable/) - demo [here](https://covid-19.datasettes.com/covid/ny_times_us_counties.copyable?state=Texas&county=Harris).

The trick is to run `document.execCommand("copy")` to copy to the clipboard - but only after first ensuring that some selectable content (probably in a textarea) has been selected.

So you do this:
```javascript
var ta = document.querySelector("textarea");
var button = document.querySelector("button");
button.onclick = () => {
    ta.select();
    document.execCommand("copy");
};
```
But that's not quite enough: there's no visible indication that anything happened!

I decided to fix this by updating the text on the button to say "Copied!" and then reverting the button text back again 1.5 seconds later.

I also opted to add the "copy" button using JavaScript, since without JavaScript enabled it won't do anything.

Here's the full HTML and JavaScript snippet I used:
```html
<div>
<textarea class="copyable">{{ copyable }}</textarea>
<p class="raw-link"><a href="{{ raw_link }}">Raw data</a></p>
</div>

<script>
var ta = document.querySelector("textarea.copyable");
var p = document.querySelector("p.raw-link");
var button = document.createElement("button");
button.className = "copyable-copy-button";
button.innerHTML = "Copy to clipboard";
button.onclick = () => {
    ta.select();
    document.execCommand("copy");
    button.innerHTML = "Copied!";
    setTimeout(() => {
        button.innerHTML = "Copy to clipboard";
    }, 1500);
};
p.appendChild(button);
p.insertAdjacentElement("afterbegin", button);
</script>
```
