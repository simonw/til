# Linking from /latest/ to /stable/ on Read The Docs

[Read The Docs](https://readthedocs.org/) has a handy feature where documentation for older versions will automatically link to the latest release, for example [on this page](https://docs.datasette.io/en/0.56/spatialite.html):

<img width="978" alt="A documentation page with a note that says: You are not reading the most recent version of this documentation. 0.60 is the latest version available." src="https://user-images.githubusercontent.com/9599/150437341-14554fe7-1c47-4462-a1d9-9b8d822aaea8.png">

That feature is enabled by a "Show version warning" check box in their Advanced Settings preference pane.

It's implemented by [this JavaScript](https://github.com/readthedocs/readthedocs.org/blob/0852d7c10d725d954d3e9a93513171baa1116d9f/readthedocs/core/static-src/core/js/doc-embed/version-compare.js#L13-L21) in their default theme, called [from here](https://github.com/readthedocs/readthedocs.org/blob/bc3e147770e5740314a8e8c33fec5d111c850498/readthedocs/core/static-src/core/js/doc-embed/footer.js#L66-L86).

I had an extra requirement: I wanted pages on my `/en/latest/` documentation (which shows documentation for the in-development `main` branch on GitHub) to link back to the `/en/stable/` equivalent - but only if that page also existed in the stable documentation.

I ended up [adding this snippet](https://github.com/simonw/datasette/commit/ffca55dfd7cc9b53522c2e5a2fa1ff67c9beadf2) of jQuery JavaScript to my custom ` docs/_templates/layout.html` template:

```html+jinja
{% block footer %}
{{ super() }}
<script>
jQuery(function ($) {
  // Show banner linking to /stable/ if this is a /latest/ page
  if (!/\/latest\//.test(location.pathname)) {
    return;
  }
  var stableUrl = location.pathname.replace("/latest/", "/stable/");
  // Check it's not a 404
  fetch(stableUrl, { method: "HEAD" }).then((response) => {
    if (response.status == 200) {
      var warning = $(
        `<div class="admonition warning">
           <p class="first admonition-title">Note</p>
           <p class="last">
             This documentation covers the <strong>development version</strong> of Datasette.</p>
             <p>See <a href="${stableUrl}">this page</a> for the current stable release.
           </p>
        </div>`
      );
      warning.find("a").attr("href", stableUrl);
      var body = $("div.body");
      if (!body.length) {
        body = $("div.document");
      }
      body.prepend(warning);
    }
  });
});
</script>
{% endblock %}
```
The neatest piece of this solution is the way it uses an HTTP `HEAD` request via `fetch()` to confirm that the equivalent stable page exists before adding a link to it:
```javascript
  var stableUrl = location.pathname.replace("/latest/", "/stable/");
  // Check it's not a 404
  fetch(stableUrl, { method: "HEAD" }).then((response) => {
    if (response.status == 200) {
      // Add the link
```

Here's what my fix looks like, running on https://docs.datasette.io/en/latest/csv_export.html

<img width="978" alt="This page has a banner that says:  This documentation covers the development version of Datasette. See this page for the current stable release." src="https://user-images.githubusercontent.com/9599/150438021-0ab3db8f-7f65-4846-b2d4-880e10dce79d.png">

## Alternative solution: sphinx-version-warning

Just minutes after I committed my fix I was informed of the existence of [sphinx-version-warning](https://sphinx-version-warning.readthedocs.io/en/latest/), a Sphinx plugin that can solve this problem too. There's an example of using that to add a message to the `/latest/` page in [its own documentation configuration here](https://github.com/humitos/sphinx-version-warning/blob/a82156c2ea08e5feab406514d0ccd9d48a345f48/docs/conf.py#L32-L38).

```python
# -- Version Warning Banner configuration ------------------------------------
versionwarning_messages = {
    'latest': 'This is a custom message only for version "latest" of this documentation.',
}
versionwarning_admonition_type = 'tip'
versionwarning_banner_title = 'Tip'
versionwarning_body_selector = 'div[itemprop="articleBody"]'
```
I decided to stick with my version, mainly because I like the `fetch()` solution I used.

GitHub issue: [ Documentation should clarify /stable/ vs /latest/ #1608](https://github.com/simonw/datasette/issues/1608)
