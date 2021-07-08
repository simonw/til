# Preventing double form submissions with JavaScript

I needed this for [VIAL issue 722](https://github.com/CAVaccineInventory/vial/issues/722). I decided to disable form submissions for two seconds after they are submitted, to protect against accidental double submissions without risk of unexpected issues that could cause the form to be permanently disabled even though it should still be able to submit it.

I ended up adding this code to a custom Django Admin base template:

```javascript
function protectForm(form) {
  var locked = false;
  form.addEventListener('submit', (ev) => {
    if (locked) {
      ev.preventDefault();
      return;
    }
    locked = true;
    setTimeout(() => {
      locked = false;
    }, 2000);
  });
}
window.addEventListener('load', () => {
  Array.from(document.querySelectorAll('form')).forEach(protectForm);
});
```
