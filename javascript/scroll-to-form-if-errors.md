# Scroll page to form if there are errors

For a Django application I'm working on ([this issue](https://github.com/simonw/django-sql-dashboard/issues/44)) I have a form that can be quite a long way down the page.

If the form is displayed with errors, I want to scroll the user down to the form so they don't get confused.

Since Django forms display errors in an element with a `errorlist` class, this worked:

```javascript
window.addEventListener("load", () => {
  if (document.querySelector('.errorlist')) {
    document.querySelector('#my-form').scrollIntoView();
  }
});
```

[Element.scrollIntoView()](https://developer.mozilla.org/en-US/docs/Web/API/Element/scrollIntoView) on MDN, and [on Can I use](https://caniuse.com/scrollintoview).
