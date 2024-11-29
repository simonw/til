# GitHub OAuth for a static site using Cloudflare Workers

My [tools.simonwillison.net](https://tools.simonwillison.net/) site is a growing collection of small HTML and JavaScript applications hosted as static files on GitHub Pages.

Many of those tools take advantage of external APIs such as those provided by OpenAI and Anthropic and Google Gemini, thanks to the increasingly common `access-control-allow-origin: *` [CORS header](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS).

I want to start building tools that work with [the GitHub API](https://docs.github.com/en/rest), in order to implement things like saving data to a [Gist](https://gist.github.com/)

To do that, I needed to implement [OAuth](https://docs.github.com/en/apps/oauth-apps): redirecting users to GitHub to request permission to access their data and then storing an access token in their browser's `localStorage` to be used by JavaScript running on my site.

There is just one catch: it currently isn't possible to implement GitHub OAuth entirely from the client, because that API depends on a secret that must be held server-side and cannot be exposed.

This morning, I had an idea: my tools site is [hosted by GitHub Pages](https://github.com/simonw/tools), but it's served via my [Cloudflare](https://www.cloudflare.com/) account for the `simonwillison.net` domain.

Could I spin up a tiny [Cloudflare Workers](https://workers.cloudflare.com/) server-side script implementing GitHub OAuth and add it to a path on that `tools` subdomain?

The answer turned out to be yes.

## Getting Claude to write me a Worker

I prompted [Claude](https://claude.ai/) with the following:

> `Write a Cloudflare worker that implements an oauth flow with GitHub to get a token scoped for gist read and write only`
>
> `Landing on the worker page redirects to GitHub for the oauth - GitHub sends back to the same page, which then outputs a script block that sets the access key in localstorage`

This is the simplest possible design for an OAuth flow: send the user straight to GitHub, then exchange the resulting `?code=` for an access token and write that to `localStorage`.

Here's [the full Claude transcript](https://gist.github.com/simonw/975b8934066417fe771561a1b672ad4f). Claude gave me almost *exactly* what I needed - the only missing detail was that it set the `redirectUri` to `url.origin` (just the site domain) when it should have been the full URL to the worker page.

I edited the code to its final version, which looked like this:
```javascript
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const clientId = env.GITHUB_CLIENT_ID;
    const clientSecret = env.GITHUB_CLIENT_SECRET;
    const redirectUri = env.GITHUB_REDIRECT_URI;
    
    // If we have a code, exchange it for an access token
    if (url.searchParams.has('code')) {
      const code = url.searchParams.get('code');
      
      // Exchange the code for an access token
      const tokenResponse = await fetch('https://github.com/login/oauth/access_token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          client_id: clientId,
          client_secret: clientSecret,
          code: code,
          redirect_uri: redirectUri
        })
      });
      
      const tokenData = await tokenResponse.json();
      
      // Return HTML that stores the token and closes the window
      return new Response(`
        <!DOCTYPE html>
        <html>
          <head>
            <title>GitHub OAuth Success</title>
          </head>
          <body>
            <script>
              localStorage.setItem('github_token', '${tokenData.access_token}');
              document.body.innerHTML = 'Authentication successful! You can close this window.';
            </script>
          </body>
        </html>
      `, {
        headers: {
          'Content-Type': 'text/html'
        }
      });
    }
    
    // If no code, redirect to GitHub OAuth
    const githubAuthUrl = new URL('https://github.com/login/oauth/authorize');
    githubAuthUrl.searchParams.set('client_id', clientId);
    githubAuthUrl.searchParams.set('redirect_uri', redirectUri);
    githubAuthUrl.searchParams.set('scope', 'gist');
    githubAuthUrl.searchParams.set('state', crypto.randomUUID());
    
    return Response.redirect(githubAuthUrl.toString(), 302);
  }
};
```
I find it hard to imagine a simpler implementation of this pattern.

The GitHub API has been around for a very long time, so it shouldn't be surprising that Claude knows exactly how to write the above code. I was still delighted at how much work it had saved me.

(I should mention now that I completed this entire project on my phone, before I got up to make the morning coffee.)

## Deploying this to Cloudflare Workers

There are four steps to deploying this:

1. Configuring a GitHub OAuth application to get a client ID and secret
2. Create a new worker with the code
3. Set the three variables it needs
4. Configure the correct URL to serve the worker

I created the GitHub OAuth app here: https://github.com/settings/applications/new

The most important thing to get right here is the "Authorization callback URL": I set that to `https://tools.simonwillison.net/github-auth` - a URL that didn't exist yet but would after I deployed the Worker.

Then in my Cloudflare dashboard, I navigated to Workers & Pages and clicked "Create" and then "Create Worker". 

I deployed the default "Hello world" example and edited it to paste in the code that Claude had written for me.

The Cloudflare editing UI was *not* built with mobile phones in mind, but I just managed to paste in my code with it!

<img src="https://github.com/user-attachments/assets/25c8bce0-39db-4e0e-93ba-69912a1411d6" style="width: 400px" alt="The Cloudflare workers editing UI looks awful in Mobile Safari - a very narrow column with some visible code and half the page taken up with extra settings.">

I used the "settings" page to set the `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET` and `GITHUB_REDIRECT_URI` environment variables needed by the Worker.

The last step was to configure that URL. I navigated to my `simonwillison.net` Cloudflare dashboard, hit "Workers Routes" and then added a new route mapping `tools.simonwillison.net/github-auth*` to the Worker I had just created.

That final `*` wildcard turned out to be necessary to ensure that `?code=` querystring URLs would also activate the `/github-auth` worker - without that I got a 404 served by GitHub Pages for those URLs instead.

Here's the deployed page - visiting it should redirect you straight to GitHub: https://tools.simonwillison.net/github-auth

## Using this from an application

The OAuth flow works by setting a `github_token` key in `localStorage()` for the entire `tools.simonwillison.net` domain - which means JavaScript on any page can check for that key and make API calls to the GitHub Gist API if the key is present.

Here's some more code [Claude wrote](https://gist.github.com/simonw/29efb202da39775761ab6ab498d942ca) for integrating the new auth mechanism into an existing tool:

```javascript
function checkGithubAuth() {
    const token = localStorage.getItem('github_token');
    if (token) {
        authLinkContainer.style.display = 'none';
        saveGistBtn.style.display = 'inline-block';
    } else {
        authLinkContainer.style.display = 'inline-block';
        saveGistBtn.style.display = 'none';
    }
}

function startAuthPoll() {
    const pollInterval = setInterval(() => {
        if (localStorage.getItem('github_token')) {
            checkGithubAuth();
            clearInterval(pollInterval);
        }
    }, 1000);
}

authLink.addEventListener('click', () => {
    window.open('https://tools.simonwillison.net/github-auth', 'github-auth', 'width=600,height=800');
    startAuthPoll();
});
```

`authLink` here is a reference to a "Authenticate with GitHub" link on that page. Clicking that link uses `window.open` to open a popup showing my new `/github-auth` page, which then automatically redirects to GitHub for permission.

Clicking the link also starts a every-second poll to check if `github_token` has been set in `localStorage` yet. As soon as that becomes available the polling ends, the "Authenticate with GitHub" UI is hidden and a new `saveGistBtn` (a button to save a Gist) is made visible.

Here's the page that uses that: https://tools.simonwillison.net/openai-audio-output - you'll need to provide an OpenAI API key and submit a prompt in order to see the option to Authenticate with GitHub.

## Adding error handling

That code Claude wrote is missing an important detail: error handling. If the GitHub API returns an error - e.g. because the `?code=` is invalid - the page won't reflect that to the user.

I pasted in the code and prompted:

> `Add error handling to this Cloudflare Workers script - if the GitHub API returns an error it should be shown to the user`

Claude [wrote more code](https://gist.github.com/simonw/85debbdf3d981ff7e54f8cdb6be47578#create-github-oauth-cloudflare-worker-with-error-handling), but it was a bit verbose. I prompted:

> `refactor that code to have less code for the HTML`

And [got back this](https://gist.github.com/simonw/85debbdf3d981ff7e54f8cdb6be47578#rewrite-untitled), which is much better. I've now deployed that as an update to the original script.

```javascript
export default {
  async fetch(request, env) {
    const generateHTML = ({ title, content, isError = false }) => {
      return new Response(`
        <!DOCTYPE html>
        <html>
          <head>
            <title>${title}</title>
            <style>
              body {
                font-family: -apple-system, system-ui, sans-serif;
                padding: 2rem;
                max-width: 600px;
                margin: 0 auto;
                text-align: center;
              }
              .message {
                padding: 1rem;
                margin: 1rem 0;
                border-radius: 4px;
                background-color: ${isError ? '#ffebee' : '#e8f5e9'};
                border: 1px solid ${isError ? '#ffcdd2' : '#c8e6c9'};
                color: ${isError ? '#b71c1c' : '#2e7d32'};
              }
            </style>
          </head>
          <body>
            <div class="message">
              ${content}
            </div>
            ${isError ? '<p>Please close this window and try again. If the problem persists, contact support.</p>' : ''}
          </body>
        </html>
      `, {
        headers: { 'Content-Type': 'text/html' },
        status: isError ? 400 : 200
      });
    };

    try {
      const url = new URL(request.url);
      const clientId = env.GITHUB_CLIENT_ID;
      const clientSecret = env.GITHUB_CLIENT_SECRET;
      const redirectUri = env.GITHUB_REDIRECT_URI;
      
      if (!url.searchParams.has('code')) {
        const githubAuthUrl = new URL('https://github.com/login/oauth/authorize');
        githubAuthUrl.searchParams.set('client_id', clientId);
        githubAuthUrl.searchParams.set('redirect_uri', redirectUri);
        githubAuthUrl.searchParams.set('scope', 'gist');
        githubAuthUrl.searchParams.set('state', crypto.randomUUID());
        return Response.redirect(githubAuthUrl.toString(), 302);
      }

      const tokenResponse = await fetch('https://github.com/login/oauth/access_token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          client_id: clientId,
          client_secret: clientSecret,
          code: url.searchParams.get('code'),
          redirect_uri: redirectUri
        })
      });
      
      const tokenData = await tokenResponse.json();
      
      if (tokenData.error) {
        return generateHTML({
          title: 'GitHub OAuth Error',
          content: `
            <h3>Authentication Error</h3>
            <p>Error: ${tokenData.error}</p>
            ${tokenData.error_description ? `<p>Description: ${tokenData.error_description}</p>` : ''}
          `,
          isError: true
        });
      }
      
      return generateHTML({
        title: 'GitHub OAuth Success',
        content: `
          <h2>Authentication successful!</h2>
          <p>You can close this window.</p>
          <script>
            try {
              localStorage.setItem('github_token', '${tokenData.access_token}');
            } catch (err) {
              document.body.innerHTML += '<p style="color: #c62828;">Warning: Unable to store token in localStorage</p>';
            }
          </script>
        `
      });

    } catch (error) {
      return generateHTML({
        title: 'Unexpected Error',
        content: `
          <h3>Unexpected Error</h3>
          <p>An unexpected error occurred during authentication.</p>
          <p>Details: ${error.message}</p>
        `,
        isError: true
      });
    }
  }
};
```
Here's [an example page](https://tools.simonwillison.net/github-auth?code=bad-code) showing the new error message.
