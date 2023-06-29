# Rendering Markdown with the GitHub Markdown API

I wanted to convert the Markdown used in my TILs to HTML, using the exact same configuration as GitHub does. GitHub has a whole load of custom extensions for things like tables and syntax highlighting (see [issue 17](https://github.com/simonw/til/issues/17)).

It turns out they have [an API for this](https://developer.github.com/v3/markdown/)!

```python
import httpx

body = """
# Example

This is example Markdown
"""

response = httpx.post(
    "https://api.github.com/markdown",
    json={
        # mode=gfm would expand #13 issue links, provided you pass
        # context=simonw/datasette too
        "mode": "markdown",
        "text": body,
    },
    headers=headers,
)
if response.status_code == 200:
    markdown_as_html = response.text
```

`response.headers` will give you back information that includes rate-limiting details:
```python
{'server': 'GitHub.com',
 'date': 'Sat, 22 Aug 2020 19:20:29 GMT',
 'content-type': 'text/html;charset=utf-8',
 'content-length': '14',
 'status': '200 OK',
 'x-commonmarker-version': '0.21.0',
 'x-ratelimit-limit': '60',
 'x-ratelimit-remaining': '57',
 'x-ratelimit-reset': '1598125911',
 'access-control-expose-headers': 'ETag, Link, Location, Retry-After, X-GitHub-OTP, X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset, X-OAuth-Scopes, X-Accepted-OAuth-Scopes, X-Poll-Interval, X-GitHub-Media-Type, Deprecation, Sunset',
 'access-control-allow-origin': '*',
 'strict-transport-security': 'max-age=31536000; includeSubdomains; preload',
 'x-frame-options': 'deny',
 'x-content-type-options': 'nosniff',
 'x-xss-protection': '1; mode=block',
 'referrer-policy': 'origin-when-cross-origin, strict-origin-when-cross-origin',
 'content-security-policy': "default-src 'none'",
 'vary': 'Accept-Encoding, Accept, X-Requested-With',
 'x-github-request-id': 'C9F0:12D7:32CDD4:8064E2:5F416FFD'}
```
## Calling it from JavaScript with fetch()

I built a [JavaScript tool that uses this API](/tools/render-markdown). Here's the key function:

```javascript
async function render(markdown) {
    return (await fetch('https://api.github.com/markdown', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'mode': 'markdown', 'text': markdown})
    })).text();
}
```
Called like this:
```javascript
let rendered = await render(input.value);
```

## Syntax highlighting CSS

Code examples you send to this API will come back something like this:

```html
<div class="highlight highlight-text-xml-svg"><pre>&lt;<span class="pl-ent">svg</span> <span class="pl-e">viewBox</span>=<span class="pl-s"><span class="pl-pds">"</span>0 0 500 100<span class="pl-pds">"</span></span>&gt;
  &lt;<span class="pl-ent">polyline</span>
     <span class="pl-e">fill</span>=<span class="pl-s"><span class="pl-pds">"</span>none<span class="pl-pds">"</span></span>
     <span class="pl-e">stroke</span>=<span class="pl-s"><span class="pl-pds">"</span>#0074d9<span class="pl-pds">"</span></span>
     <span class="pl-e">stroke-width</span>=<span class="pl-s"><span class="pl-pds">"</span>3<span class="pl-pds">"</span></span>
     <span class="pl-e">points</span>=<span class="pl-s"><span class="pl-pds">"</span></span>
<span class="pl-s">       0,120</span>
<span class="pl-s">       20,60</span>
<span class="pl-s">       40,80</span>
<span class="pl-s">       60,20<span class="pl-pds">"</span></span>/&gt;
```
https://github.com/primer/github-syntax-theme-generator has tools for theming these. I like this stylesheet (MIT licensed): https://github.com/primer/github-syntax-light/blob/master/lib/github-light.css - I figured this out in [issue 20](https://github.com/simonw/til/issues/20).
