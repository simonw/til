# Lazy loading images in HTML

[Most modern browsers](https://caniuse.com/loading-lazy-attr) now include support for the `loading="lazy"` image attribute, which causes images not to be loaded unti the user scrolls them into view.

![Animated screenshot showing the network panel in the Firefox DevTools - as I scroll down a page more images load on demand just before they scroll into view.](https://user-images.githubusercontent.com/9599/204108097-6f385377-5daf-4895-9216-4ea0916a296a.gif)

I used it for the slides on my annotated version of this presentation: [Massively increase your productivity on personal projects with comprehensive documentation and automated tests](https://simonwillison.net/2022/Nov/26/productivity/).

There's one catch though: you need to provide the size of the image (I used `width=` and `height=` attributes) in order for it to work! Without those your browser still needs to fetch the images in order to calculate their dimensions to calculate page layout.

Here's the HTML I used for each slide image:

```html
<img
  alt="Issue driven development"
  width="450"
  height="253"
  loading="lazy"
  src="https://static.simonwillison.net/static/2022/djangocon-productivity/productivity.022.jpeg"
>
```
