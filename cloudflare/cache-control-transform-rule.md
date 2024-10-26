# Setting cache-control: max-age=31536000 with a Cloudflare Transform Rule

I ran https://simonwillison.net/ through [PageSpeed Insights](https://pagespeed.web.dev/) and it warned me that my static assets were not being served with browser caching headers:

![A screenshot of a web performance report showing static asset cache policies. Header reads "Serve static assets with an efficient cache policy — 20 resources found" followed by a list of URLs from static.simonwillison.net showing file names, cache TTL status (mostly "None"), and transfer sizes ranging from 96 KiB to 8,871 KiB.](https://github.com/user-attachments/assets/115514c7-a51d-410b-a4dd-67c34084420d)

I serve static assets for my blog (mainly images) from `static.simonwillison.net`, which is an AWS S3 bucket served via Cloudflare.

I investigated with `curl -i`:

```bash
curl -I https://static.simonwillison.net/static/2024/prompt-gemini-extract.gif
```
```
HTTP/2 200 
date: Wed, 23 Oct 2024 20:02:52 GMT
content-type: image/gif
content-length: 160263
x-amz-id-2: LpMSRQox/dMz/qS2p2jb6OmP7/YsEa4YZnOfEVgB5biGOPynNxqs8eY5EgWW0xzbclBnOI6LTAQ=
x-amz-request-id: BK8F63EJYFP5K1YB
last-modified: Wed, 23 Oct 2024 18:18:49 GMT
etag: "38a67c2deb66fe4b6f57796c2f2f5c44"
cf-cache-status: HIT
age: 149
accept-ranges: bytes
report-to: {"endpoints":[{"url":"https:\/\/a.nel.cloudflare.com\/report\/v4?s=xu4hL1Hr5W2ZDo6VSCd4NBfPp2tmCYiTNbct64mFfU6AAkBofX%2BHSZ6P%2FpIo3QKX5CqweeBhgS%2BYNOuzWW2E4pb4O3V1pISkOHzU0NPM%2B9QgGyuquDc%2FOl2aZM5HL3MjBPm0oKJD2AWWeyY%3D"}],"group":"cf-nel","max_age":604800}
nel: {"success_fraction":0,"report_to":"cf-nel","max_age":604800}
server: cloudflare
cf-ray: 8d7453c3481b9e5e-SJC
alt-svc: h3=":443"; ma=86400
server-timing: cfL4;desc="?proto=TCP&rtt=23918&sent=5&recv=9&lost=0&retrans=0&sent_bytes=2907&recv_bytes=585&delivery_rate=124913&cwnd=177&unsent_bytes=0&cid=ec38180c3ba3b0e7&ts=47&x=0"
```
That confirms it's being served by Cloudflare that Cloudflare itself is caching the page (`cf-cache-status: HIT`) - but there's no `cache-control` header in there telling my browser to cache the image. This means the image is fetched again from Cloudflare every time the page loads.

I wanted a quick way to add `cache-control: max-age=31536000` headers to every one of those resources. I already have a policy that I rename a file any time I upload a new version so I may as well cache everything in the browser for 31536000 (24 * 60 * 60 * 365 seconds aka a full year).

## Using Cloudflare Transform Rules

Cloudflare has a bewildering array of options these days. I asked Claude and it suggested using a "Transform Rule".

Here's the form I found in the Cloudflare dashboard for adding a new rule:

![A screenshot of a Cloudflare Transform Rules configuration page showing the creation of a new HTTP Response Header Modification Rule. The rule is named "Cache-Control: max-age=31536000" and is set to apply to requests where the hostname equals "static.simonwillison.net". The rule adds a cache-control header with max-age=31536000.](https://github.com/user-attachments/assets/42c0ab9f-5b78-4dfa-b684-aae2fe156e5f)

Cloudflare is configured for my entire `simonwillison.net` domain with the S3 bucket configured as a proxied caching CNAME to S3.

As such, I only wanted my rule to apply to `static.simonwillison.net`. I configured that using a custom filter expression of `Hostname = static.simonwillison.net`.

Then I told it to add a header name of `cache-control` and a value of `max-age=31536000` to all matching responses.

## Confirming it worked

I ran this again:
```bash
curl -I https://static.simonwillison.net/static/2024/prompt-gemini-extract.gif
```
And got back:
```
HTTP/2 200 
date: Wed, 23 Oct 2024 20:07:12 GMT
content-type: image/gif
content-length: 160263
x-amz-id-2: LpMSRQox/dMz/qS2p2jb6OmP7/YsEa4YZnOfEVgB5biGOPynNxqs8eY5EgWW0xzbclBnOI6LTAQ=
x-amz-request-id: BK8F63EJYFP5K1YB
last-modified: Wed, 23 Oct 2024 18:18:49 GMT
etag: "38a67c2deb66fe4b6f57796c2f2f5c44"
cf-cache-status: HIT
age: 409
accept-ranges: bytes
report-to: {"endpoints":[{"url":"https:\/\/a.nel.cloudflare.com\/report\/v4?s=2HCHW9L52YEhmN%2FbP1ZVxQLL%2FtLrpf5GTN1J%2B8dUnvC53hhSyW2PDiAHv%2B43DvJnsUsnrInVAxdZCgTsIfQ7JCg98jFzHMdu6xb3uOGAHPdC1aE9utyUGvAedNa6RVxO9yx30qkUSuiwR2k%3D"}],"group":"cf-nel","max_age":604800}
nel: {"success_fraction":0,"report_to":"cf-nel","max_age":604800}
cache-control: max-age=31536000
server: cloudflare
cf-ray: 8d745a2099107ac4-SJC
alt-svc: h3=":443"; ma=86400
server-timing: cfL4;desc="?proto=TCP&rtt=23766&sent=5&recv=8&lost=0&retrans=0&sent_bytes=2907&recv_bytes=585&delivery_rate=131337&cwnd=117&unsent_bytes=0&cid=bd0475734101defd&ts=55&x=0"
```
Note the new `cache-control:` header in there.

I then tested it in Firefox. I loaded the page, opened up the network tab in browser DevTools and hit refresh. I got this:

![A screenshot of a browser network requests panel showing 18 HTTP requests for various resources including images, JavaScript, and icons. The requests are primarily to static.simonwillison.net, with most returning 200 status codes and "cached" transfer status. The page took 786ms to finish loading with DOMContentLoaded at 59ms.](https://github.com/user-attachments/assets/94b4eae4-c530-4379-b655-bea1f3689092)

Note the summary that says "1.38MB / 1.62 kB transferred" - the caching is working extremely well.

## Bonus: access-control-allow-origin

I have an S3 bucket behind Cloudflare and I wanted a quick and easy way to put files online that are served with `access-control-allow-origin: *`, initially so I could experiment with things like [Datasette Lite](https://lite.datasette.io/) and the [DuckDB WASM Shell](https://duckdb.org/docs/api/wasm/overview.html).

![Screenshot of a CORS configuration interface with fields for rule name "static.simonwillis.net/static/cors-allow/*", custom filter expression selected, URI Full field with wildcard operator and value "https://static.simonwillison.net/static/cors-allow/*", and response header configuration for access-control-allow-origin set to "*"](https://github.com/user-attachments/assets/bd476176-a942-47af-9d73-c9cbde476f89)
