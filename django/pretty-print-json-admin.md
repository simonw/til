# Pretty-printing all read-only JSON in the Django admin

I have a bunch of models with JSON fields that are marked as read-only in the Django admin - usually because they're recording the raw JSON that was imported from an API somewhere to create an object, for debugging purposes.

Here's a pattern I found for pretty-printing ANY JSON value that is displayed in a read-only field in the admin. Create a template called `admin/change_form.html` and populate it with the following:

```html+django
{% extends "admin/change_form.html" %}
{% block admin_change_form_document_ready %}
{{ block.super }}
<script>
Array.from(document.querySelectorAll('div.readonly')).forEach(div => {
    let data;
    try {
        data = JSON.parse(div.innerText);
    } catch {
        // Not valid JSON
        return;
    }
    div.style.whiteSpace = 'pre-wrap';
    div.style.fontFamily = 'courier';
    div.style.fontSize = '0.9em';
    div.innerText = JSON.stringify(data, null, 2);
});
</script>
{% endblock %}
```
This JavaScript will execute on every Django change form page, scanning for `div.readonly`, checking to see if the div contains a valid JSON value and pretty-printing it using JavaScript if it does.

It's a cheap hack and it works great.
