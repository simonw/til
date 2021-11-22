# Loading lit from Skypack

[Lit 2](https://lit.dev/blog/2021-09-21-announcing-lit-2/) stable was released today, offering a tiny, feature-full framework for constructing web components using modern JavaScript.

The [getting started documentation](https://lit.dev/docs/getting-started/) involves a whole lot of `npm` usage, but I wanted to just drop something into an HTML page and start trying out the library, without any kind of build step.

After [some discussion](https://twitter.com/simonw/status/1440462801630208001) on Twitter and with [the help of @WestbrookJ](https://twitter.com/WestbrookJ/status/1440477115741130757) I figured out the following pattern, which loads code from [Skypack](https://www.skypack.dev/):

```html
<script type="module">
import { LitElement, html } from 'https://cdn.skypack.dev/lit';
  
class MyEl extends LitElement {
  render() {
    return html`Hello world!`
  }
}
customElements.define('my-el',MyEl);
</script>
<my-el></my-el>
```

Also relevant: [lit-dist](https://github.com/fserb/lit-dist).
