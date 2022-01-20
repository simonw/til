# Promoting the stable version of the documentation using rel=canonical

I was thinking about documentation SEO today. Like many projects, Datasette offers multiple versions of the documentation:

- https://docs.datasette.io/en/latest/ is the latest `main` branch on GitHub
- https://docs.datasette.io/en/stable/ is the most recent stable (non alpha or beta) release - currently 0.60
- https://docs.datasette.io/en/0.59.4/ is the documentation for that specific version - I have more than 70 of those now

For other projects that do this I've often found myself running a Google search and landing on on older version of their documentation. How best to avoid that?

I started by looking at how Django addresses this. Django uses `rel=canonical` - so, on this page: https://docs.djangoproject.com/en/2.2/topics/db/ they have the following HTML:

```html
<link rel="canonical" href="https://docs.djangoproject.com/en/4.0/topics/db/">
```

I tend to default to imitating Django, so I decided to see if I could do that for the Datasette documentation...

... and found out it's already solved for me! [Read The Docs](https://readthedocs.org/), the platform I use for the Datasette documentation, already implements exactly this pattern.

So https://docs.datasette.io/en/0.50/introspection.html includes the following HTML:
```html
<link rel="canonical" href="https://docs.datasette.io/en/stable/introspection.html" />
```
Here's [their documentation](https://docs.readthedocs.io/en/latest/custom_domains.html#canonical-urls) covering this feature. I think you need to have configured a "default version" (though they may set a sensible default for that already) - for my project the page for doing that is the Advanced settings page at https://readthedocs.org/dashboard/datasette/advanced/

This TIL started life as [a Twitter thread](https://twitter.com/simonw/status/1484287724773203971).
