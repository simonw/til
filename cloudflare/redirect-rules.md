# Cloudflare redirect rules with dynamic expressions

I wanted to ensure `https://niche-museums.com/` would redirect to `https://www.niche-museums.com/` - including any path - using Cloudflare.

I've [solved this with page rules in the past](https://til.simonwillison.net/cloudflare/redirect-whole-domain), but this time I tried using a "redirect rule" instead.

Creating a redirect rule that only fires for hits to the `niche-museums.com` (as opposed to `www.niche-museums.com`) hostname was easy. The harder part was figuring out how to assemble the URL.

I eventually found the clues I needed [in this Cloudflare blog post](https://blog.cloudflare.com/dynamic-redirect-rules). The trick is to assemble a "dynamic" URL redirect using the `concat()` function in the Cloudflare expression language, [described here](https://developers.cloudflare.com/ruleset-engine/rules-language/functions/#transformation-functions).

    concat("https://www.niche-museums.com", http.request.uri)

Here are the full configuration settings I used for my redirect rule:

![Configuration screen for setting up a custom URL redirection rule. Custom filter expression is selected, indicating the rule will only apply to traffic matching the custom expression. When incoming requests match... Field: Hostname, Operator: Equals, Value: niche-museums.com. Expression Preview: (http.host eq "niche-museums.com"). Then... URL redirect, Type: Dynamic, Expression: concat("https://www.niche-museums.com", http.request.uri), Status code: 301 (permanent redirect). Preserve query string: This option is unchecked. Buttons: Cancel, Save as Draft, Deploy.](https://static.simonwillison.net/static/2024/cloudflare-redirect-rule.jpg)
