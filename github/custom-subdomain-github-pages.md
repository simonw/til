# Setting up a custom subdomain for a GitHub Pages site

This is so much easier than I was expecting it to be.

I launched my new [Datasette Lite](https://github.com/simonw/datasette-lite) project ([background](https://simonwillison.net/2022/May/4/datasette-lite/)) using GitHub Pages - originally hosted here:

https://simonw.github.io/datasette-lite/

Shortly after launching I realized that the project deserved its own vanity subdomain. I wanted to use `lite.datasette.io` for this.

GitHub Pages makes this really easy.

I started by pointing the `CNAME` for `lite.datasette.io` at `simonw.github.io` - I use Vercel for the DNS for that domain, so I set this up in their interface.

Then I used the Pages tab in the "settings" interface for the GitHub repository and told it about my new domain.

GitHub wrote a file called [CNAME](https://github.com/simonw/datasette-lite/blob/main/CNAME) directly into the root of my repository for me containing just `lite.datasette.io`

This started working over HTTP straight away - it took a few more minutes for the Lets Encrypt certificate to be issued for it, at which point https://lite.datasette.io/ started working too.

I then used the "Enforce HTTPS" option to ensure any hits to `http://...` were redirected to `https://`

<img width="781" alt="Screenshot of the GitHub interface for setting the domain, showing the Enforce HTTPS checkbox" src="https://user-images.githubusercontent.com/9599/166835190-3ca925a8-3fbf-4656-aea5-1b67bb984a24.png">

## Redirects

GitHub Pages set up redirects from the old https://simonw.github.io/datasette-lite/ site to the new one without me even asking them to.

The redirects preserve both query string parameters AND fragment hashes, which means that this old URL continues to work after the move:

https://simonw.github.io/datasette-lite/#/fixtures?sql=select+sqlite_version%28%29

It redirects to:

https://lite.datasette.io/#/fixtures?sql=select+sqlite_version%28%29
