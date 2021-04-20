# Usable horizontal scrollbars in the Django admin for mouse users

I got a complaint from a Windows-with-mouse user of a Django admin project I'm working on: they couldn't see the right hand columns in a table without scrolling horizontally, but since the horizontal scrollbar was only available at the bottom of the page they had to scroll all the way to the bottom first in order to scroll sideways.

As a trackpad user I'm not affected by this, since I can two-finger scroll sideways anywhere on the table.

(I've had the same exact complaint about Datasette in the past, so I'm very interested in solutions).

Matthew Somerville [on Twitter](https://twitter.com/dracos/status/1384391599476641793) suggested setting the maxmimum height of the table to the height of the window, which would cause the horizontal scrollbar to always be available.

Here's the recipe I came up with for doing that for tables in the Django admin:

```html
<script>
function resizeTable() {
  /* So Windows mouse users can see the horizontal scrollbar
     https://github.com/CAVaccineInventory/vial/issues/363 */
  let container = document.querySelector("#changelist-form .results");
  let paginator = document.querySelector("p.paginator");
  if (!container || !paginator) {
    return;
  }
  let height =
    window.innerHeight -
    container.getBoundingClientRect().top -
    paginator.getBoundingClientRect().height -
    10;
  container.style.overflowY = "auto";
  container.style.height = height + "px";
}
window.addEventListener("load", resizeTable);
</script>
```
Here `#changelist-form .results` is a `<div>` that wraps the main table on the page, and `p.paginator` is the pagination links shown directly below the table. I decided to set the vertically scrollable height to `window height - top-of-table - paginator height - 10px`.

I added this code to my project's custom `admin/base_site.html` template, which now looks something like this:

```html+django
{% extends "admin/base_site.html" %}

{% block footer %}
<div id="footer"></div>
<script>
/* Script goes here */
</script>
{% endblock %}
```
The end result looks like this:

<img width="1355" alt="Select_county_to_change___VIAL_admin" src="https://user-images.githubusercontent.com/9599/115450508-d4c6cd00-a1d0-11eb-8efd-5561a630337c.png">
