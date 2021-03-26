# Dropdown menu with details summary

I added dropdown menus to [Datasette 0.51](https://docs.datasette.io/en/stable/changelog.html#v0-51) - see [#1064](https://github.com/simonw/datasette/issues/1064).

I implemented them using the HTML `<details><summary>` element. The HTML looked like this:

```html
<details class="nav-menu">
    <summary><svg aria-labelledby="nav-menu-svg-title" role="img"
        fill="currentColor" stroke="currentColor" xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 16 16" width="16" height="16">
            <title id="nav-menu-svg-title">Menu</title>
            <path fill-rule="evenodd" d="M1 2.75A.75.75 0 011.75 2h12.5a.75.75 0 110 1.5H1.75A.75.75 0 011 2.75zm0 5A.75.75 0 011.75 7h12.5a.75.75 0 110 1.5H1.75A.75.75 0 011 7.75zM1.75 12a.75.75 0 100 1.5h12.5a.75.75 0 100-1.5H1.75z"></path>
    </svg></summary>
    <div class="nav-menu-inner">
        <ul>
            <li><a href="/">Item one</a></li>
            <li><a href="/">Item two</a></li>
            <li><a href="/">Item three</a></li>
        </ul>
    </div>
</details>
```
See the top right corner of https://latest-with-plugins.datasette.io/ for a demo.

This displays an SVG icon which, when clicked, expands to show the menu. The SVG icon uses `aria-labelledby="nav-menu-svg-title" role="img"` and a `<title id="nav-menu-svg-title">` element for accessibility.

I styled the menu using a variant of the following CSS:

```css
details.nav-menu > summary {
    list-style: none;
    display: inline;
    position: relative;
    cursor: pointer;
}
details.nav-menu > summary::-webkit-details-marker {
    display: none;
}
details .nav-menu-inner {
    position: absolute;
    top: 2rem;
    left: 10px;
    width: 180px;
    z-index: 1000;
    border: 1px solid black;
}
.nav-menu-inner a {
    display: block;
}
```
`list-style: none;` hides the default reveal arrow from most browsers. `::-webkit-details-marker { display:none }` handles the rest.

The `summary` element uses `position: relative;` and the `details .nav-menu-inner` uses `position: absolute` - this positions the open dropdown menu in the right place.

## Click outside the box to close the menu

The above uses no JavaScript at all, but comes with one downside: it's usual with menus to clear them if you click outside the menu, but here you need to click on the exact icon again to hide it.

I solved that with the following JavaScript, run at the bottom of the page:

```javascript
document.body.addEventListener('click', (ev) => {
    /* Close any open details elements that this click is outside of */
    var target = ev.target;
    var detailsClickedWithin = null;
    while (target && target.tagName != 'DETAILS') {
        target = target.parentNode;
    }
    if (target && target.tagName == 'DETAILS') {
        detailsClickedWithin = target;
    }
    Array.from(document.getElementsByTagName('details')).filter(
        (details) => details.open && details != detailsClickedWithin
    ).forEach(details => details.open = false);
});
```
