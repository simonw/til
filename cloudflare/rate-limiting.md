# Rate limiting by IP using Cloudflare's rate limiting rules

My [blog](https://simonwillison.net/) was showing poor performance, with some pages taking several seconds to load or even failing entirely.

Tailing the Heroku logs showed that it was getting a barrage of traffic to the `/search/` page, which implements faceted search and hence has an almost unlimited set of possible combinations - `/search/?tag=python&year=2023` and suchlike.

I have this in my `robots.txt` file precisely to prevent bots from causing problems here:

```
User-agent: *
Disallow: /search/
```
Evidently something was misbehaving and ignoring my `robots.txt`!

My entire site runs behind Cloudflare with a 200 second cache TTL. This means my backend normally doesn't even notice spikes in traffic as they are mostly served from the Cloudflare cache.

Unfortunately this trick doesn't help for crawlers that are hitting every possible combination of facets on my search page!

## Using Cloudflare to rate limit requests to a path

Thankfully, it turns out Cloudflare can also [rate limit requests](https://developers.cloudflare.com/waf/rate-limiting-rules/) to a path.

I found this option in the `Security -> WAF -> Rate limiting rules` area of the admin panel. Here's how I configured my rule:

![Screenshot of a rate limiting rule configuration interface titled "Edit rate limiting rule" with fields filled as follows: Rule name "simonwillison.net/search/ rate limit", URI Path field set to wildcard operator with value "/search/*", IP-based rate limiting set to 5 requests per 10 seconds, action set to Block for 10 seconds duration, with expression preview showing (http.request.uri.path wildcard "/search/*")](https://static.simonwillison.net/static/2025/cloudflare-waf.jpg)

Matching the URI path on `/search/*` and having it block requests from an IP if the rate exceeded 5 requests in 10 seconds appeared to do the job.

I've been running this for a few days now, and the Cloudflare dashboard shows that it's blocked 2,850 requests in the past 24 hours:

![Screenshot of a rate limiting rules dashboard showing a table with one configured rule: Order 1, Action "Block", Name "simonwillison.net/search/ rate limit" with "URI Path" below it, CSR column shows "-", Activity last 24hr shows a small chart with "2.85k", and Enabled toggle is switched on (green), with Create rule button, Search bar, and Show filters button visible at the top](https://static.simonwillison.net/static/2025/cloudflare-waf-dash.jpg)

Clicking through shows the Cloudflare WAF logs, which provide detailed information about the blocked requests:

![Screenshot of a firewall events dashboard showing "Firewall Events" header with "Create custom rule" button, filtered by "Rule ID equals c38a7fb4c184431094d..." for "Previous 24 hours", displaying sampled logs table with one entry dated "Jul 3, 2025 12:23:12 PM" showing "Block" action from "Hong Kong" IP "47.239.129.149" for "Rate limiting rules" service, with detailed matched service section showing "Service: Rate limiting rules", "Action taken: Block", "Ruleset: default ...73e0cc32", "Rule: simonwillison.net/search/ rate limit ...ed8e65a4", and request details including "Ray ID: 9598c18c8e0d716d", "IP address: 47.239.129.149", "ASN: AS45102 ALIBABA-CN-NET Alibaba US Technology Co., Ltd.", "Country: Hong Kong", "User agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3402.42 Safari/537.36", "HTTP Version: HTTP/1.1", "Referer: None (direct)", "Method: GET", "Host: simonwillison.net", "Path: /search/", "Query string: ?month=3&tag=legal&year=2008"](https://static.simonwillison.net/static/2025/cloudflare-waf-log.jpg)
