# Understanding Kristofer Joseph's Single File Web Component

[Via Brian LeRoux](https://twitter.com/brianleroux/status/1453472609518034944) I found [single-file-web-component.html](https://gist.github.com/kristoferjoseph/c4e47389ae0f0447db175b914e471628) by Kristofer Joseph. It's really clever! It demonstrates how to build a `<hello-world></hello-world>` custom Web Component in a single HTML file, using some neat tricks.

For my own education I spent some time picking it apart and built my own annotated version of the code showing what I learned.

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>Single File Web Component</title>
    <style>
      body {
        background-color: #eee;
        font-family: Helvetica, sans-serif;
      }
      h1 {
        color: blue;
        background-color: pink;
      }
    </style>
  </head>
  <body>
    <template id="single-file">
      <style>
        /*
          These styles affect only content inside the shadow DOM.

          Styles in the outside document mostly do not affect stuff
          here, but there are some exceptions: font-family affects
          this <h1> for example. I don't understand the rules here.
        */
        h1 {
          color: red;
        }
      </style>

      <h1>Hello world (web component)</h1>
      <!--
      This code still works if you remove the type="module" parameter.

      Using that parameter enables features such as 'import ... from'

      More importantly it stops variables inside the script tag from
      leaking out to the global scope - if you remove type="module"
      from here then the HelloWorld class becomes visible.
      -->
      <script type="module">
        class HelloWorld extends HTMLElement {
          constructor() {
            /*
              If you remove the call to super() here Firefox shows an error:
              "Uncaught ReferenceError: must call super constructor before
              using 'this' in derived class constructor'"
            */
            super();
            const template = document.getElementById("single-file");
            /*
              mode: 'open' means you are allowed to access
              document.querySelector('hello-world').shadowRoot to get
              at the DOM inside. Set to 'closed' and the .shadowRoot
              property will return null.
            */
            this.attachShadow({ mode: "open" }).appendChild(
              template.content.cloneNode(true)
            );
            /* 
              template.content is a 'DocumentFragment' array.

              template.content.cloneNode() without the true performs
              a shallow clone, which provides a empty DocumentFragment
              array.

              template.content.cloneNode(true) provides one with 6 items
            */
          }
          connectedCallback() {
            // https://developer.mozilla.org/en-US/docs/Web/Web_Components/Using_custom_elements#using_the_lifecycle_callbacks
            console.log("Why hello there 👋");
          }
        }
        customElements.define("hello-world", HelloWorld);
      </script>
    </template>

    <h1>This is not a web component</h1>

    <hello-world></hello-world>

    <script>
      const sf = document.getElementById("single-file");
      /*
        Before executing this line, sf.content.lastElementChild
        is the <script type="module"> element hidden away inside
        the <template> - we remove it from the template here and
        append it to the document.body, causing it to execute in
        the main document and activate the <hello-world> tag.
      */
      document.body.appendChild(sf.content.lastElementChild);
    </script>
  </body>
</html>
```
