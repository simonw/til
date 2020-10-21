# Writing JavaScript that responds to media queries

I wanted to change the layout of [my blog](https://simonwillison.net/) on mobile screens such that the content from the "Elsewhere" right hand column combined with the main column in the correct order (issue [#165](https://github.com/simonw/simonwillisonblog/issues/165)). I couldn't find a way to do this in pure CSS without duplicating a bunch of content, so I decided to do it with JavaScript.

I needed to apply some changes to the DOM if the users window was smaller than 800px - or if the user resized their window to less than 800px after they had first loaded the page.

Here's the JavaScript I came up with, using [Window.matchMedia()](https://developer.mozilla.org/en-US/docs/Web/API/Window/matchMedia):
```javascript
window.hasBeenRearrangedForMobile = false;
function rearrangeForMobile() {
  // Make changes to the DOM here
}
function conditionalRearrange(m) {
  if (m.matches && !window.hasBeenRearrangedForMobile) {
    rearrangeForMobile();
    window.hasBeenRearrangedForMobile = true;
  }
}
var mediaMatcher = window.matchMedia('(max-width: 800px)');
conditionalRearrange(mediaMatcher);
mediaMatcher.addListener(conditionalRearrange);
```
[Full code is here](https://github.com/simonw/simonwillisonblog/blob/13c287336675e3b4f8e3f3d0f4fdeff738e87ad0/templates/homepage.html#L45-L88).

My `rearrangeForMobile()` function made changes to the DOM that themselves were governed my show/hide CSS media queries - so if the user changes the width of the page things will continue to display correctly based on the current width, without needing to execute extra JavaScript.

Here's [the accompanying CSS](https://github.com/simonw/simonwillisonblog/blob/13c287336675e3b4f8e3f3d0f4fdeff738e87ad0/static/css/all.css#L795-L812):

```css
.elsewhere-date {
    display: none;
}

#primary .elsewhere-in-primary {
    display: none;
}

@media (max-width: 800px) {
  #primary .elsewhere-in-primary {
    display: block;
  }
  .elsewhere-date {
    display: inline;
  }
  .hide-secondary-on-mobile {
    display: none;
  }
  // ...
}
```
