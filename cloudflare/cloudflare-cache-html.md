# How to get Cloudflare to cache HTML

To my surprise, if you setup a [Cloudflare](https://www.cloudflare.com/) caching proxy in front of a website it won't cache HTML pages by default, even if they are served with `cache-control:` headers.

This is [documented here](https://developers.cloudflare.com/cache/troubleshooting/customize-caching/):

> Cloudflare does not cache HTML resources automatically. This prevents us from unintentionally caching pages that often contain dynamic elements.

I figured out how to get caching to work using a "Cache Rule". Here's the rule I added:

![Cloudflare Cache Rule interface. Rule name: Cache everything including HTML. When incoming requests match… hostname contains .datasette.site. Expression preview: (http.host contains ".datasette.site"). Then... Cache Elegibility is set to Eligible for cache. Edge TTL is set to Use cache-control header if present, bypass cache if not.](https://static.simonwillison.net/static/2024/cloudflare-cache-rule.jpg)

I've told it that for any incoming request with a hostname containing `.datasette.site` (see [background in my weeknotes](https://simonwillison.net/2024/Jan/7/page-caching-and-custom-templates-for-datasette-cloud/)) it should consider that page eligible for caching, and it should respect the `cache-control` header.

With this configuration in place, my backend can now serve headers that look like this:

`cache-control: s-maxage=15`

This will cause Cloudflare to cache the page for 15 seconds.

I tried to figure out a rule that would serve all requests no matter what they looked like, but the interface would not let me leave the rules blank - so `hostname contains .datasette.site` was the best I could figure out.
