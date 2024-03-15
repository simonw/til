# Redirecting a whole domain with Cloudflare

I had to run this site on `til.simonwillison.org` for 24 hours due to a domain registration mistake I made.

Once I got `til.simonwillison.net` working again I wanted to permanently redirect the URLs on the temporary site to their equivalent on the correct domain.

Since I was running the site behind [Cloudflare](https://www.cloudflare.com/), I could get Cloudflare to handle the redirects for me using a Page Rule, which support wildcards for redirects.

I used these settings:

- URL: `til.simonwillison.org/*`
- Setting: Forwarding URL
- Status code: 301 (permanent redirect)
- Destination URL: `https://til.simonwillison.net/$1`

This did the right thing - hits to e.g. https://til.simonwillison.org/cloudflare?a=1 redirect to https://til.simonwillison.net/cloudflare?a=1

Here's a screenshot of the settings page I used to create the new Page Rule:

![Screenshot of the Cloudflare interface. Create a Page Rule for simonwillison.org.  If the URL matches: URL (required) til.simonwillison.org/*  Then the settings are: Forwarding URL https://til.simonwillison.net/$1  Select status code (required) 301 - Permanent Redirect. Save and Deploy Page Rule](https://github.com/simonw/til/assets/9599/6758a865-57fa-4da1-9e41-118f41e1d7b2)
