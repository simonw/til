# Redirecting all paths on a Vercel instance

I wanted to redirect all traffic to `https://something.vercel.app/` to a different domain - preserving the path and the querystring and serving a 301 status code.

The [Vercel redirects](https://vercel.com/docs/configuration#project/redirects) documentation doesn't mention that you can capture patterns from the source and place them in the destination. The example they give is:

```json
{
  "redirects": [
    { "source": "/me", "destination": "/profile.html" },
    { "source": "/user", "destination": "/api/user", "permanent": false },
    { "source": "/view-source", "destination": "https://github.com/vercel/vercel" }
  ]
}
```
It turns out you can use `(.*)` in the source and then `$1` in the destination. Here's the example that worked for me:
```json
{
    "redirects": [
        {
            "source": "/(.*)",
            "destination": "https://timezones-api.datasette.io/$1",
            "statusCode": 301
        }
    ]
}
```
Vercel use 307 and 308 HTTP status codes. I prefer 301 and 302 which is why I used `statusCode` above instead of their `"permanent": true`.

Here's how I deployed it:
```
~ % cd /tmp
/tmp % mkdir timezones-api
/tmp % cd timezones-api 
timezones-api % echo '{
    "redirects": [
        {
            "source": "/(.*)",
            "destination": "https://timezones-api.datasette.io/$1",
            "statusCode": 301
        }
    ]
}
' > vercel.json
timezones-api % vercel 
Vercel CLI 19.2.0
> NOTE: Deploying to Now 2.0 automatically. More: https://vercel.com/docs/version-detection
? Set up and deploy “/private/tmp/timezones-api”? [Y/n] y
? Which scope do you want to deploy to? simonw
? Found project “simonw/timezones-api”. Link to it? [Y/n] y
🔗  Linked to simonw/timezones-api (created .vercel and added it to .gitignore)
No framework detected. Default Project Settings:
- Build Command: `npm run vercel-build` or `npm run build`
- Output Directory: `public` if it exists, or `.`
- Development Command: None
? Want to override the settings? [y/N] y
? Which settings would you like to overwrite (select multiple)? None
🔍  Inspect: https://vercel.com/simonw/timezones-api-cn71cufah/simonw [1s]
✅  Production: https://timezones-api-simonw.vercel.app [copied to clipboard] [10s]
📝  Deployed to production. Run `vercel --prod` to overwrite later (https://vercel.link/2F).
💡  To change the domain or build command, go to https://vercel.com/simonw/timezones-api/settings
```
