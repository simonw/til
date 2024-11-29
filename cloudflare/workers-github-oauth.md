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

I tweaked the code to fix this, and later again to add error handling and then to address a potential security issue. My currently deployed code looks like this:

```javascript
export default {
  async fetch(request, env) {
    const generateHTML = ({ title, content, isError = false, headers = {} }) => {
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
        headers: {
          'Content-Type': 'text/html',
          ...headers
        },
        status: isError ? 400 : 200
      });
    };

    try {
      const url = new URL(request.url);
      const clientId = env.GITHUB_CLIENT_ID;
      const clientSecret = env.GITHUB_CLIENT_SECRET;
      const redirectUri = env.GITHUB_REDIRECT_URI;
      
      if (!url.searchParams.has('code')) {
        // Initial authorization request
        const state = crypto.randomUUID();
        const githubAuthUrl = new URL('https://github.com/login/oauth/authorize');
        githubAuthUrl.searchParams.set('client_id', clientId);
        githubAuthUrl.searchParams.set('redirect_uri', redirectUri);
        githubAuthUrl.searchParams.set('scope', 'gist');
        githubAuthUrl.searchParams.set('state', state);

        // Create headers object with the state cookie
        const headers = new Headers({
          'Location': githubAuthUrl.toString(),
          'Set-Cookie': `github_auth_state=${state}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=3600`
        });

        return new Response(null, {
          status: 302,
          headers
        });
      }

      // Callback handling
      const returnedState = url.searchParams.get('state');
      const cookies = request.headers.get('Cookie') || '';
      const stateCookie = cookies.split(';')
        .map(cookie => cookie.trim())
        .find(cookie => cookie.startsWith('github_auth_state='));
      const savedState = stateCookie ? stateCookie.split('=')[1] : null;

      // Cookie cleanup header
      const clearStateCookie = {
        'Set-Cookie': 'github_auth_state=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0'
      };

      // Validate state parameter
      if (!savedState || savedState !== returnedState) {
        return generateHTML({
          title: 'Invalid State Parameter',
          content: `
            <h3>Security Error</h3>
            <p>Invalid state parameter detected. This could indicate a CSRF attempt.</p>
          `,
          isError: true,
          headers: clearStateCookie
        });
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
          redirect_uri: redirectUri,
          state: returnedState
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
          isError: true,
          headers: clearStateCookie
        });
      }
      
      // Success response with cookie cleanup
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
        `,
        headers: clearStateCookie
      });

    } catch (error) {
      // Error response with cookie cleanup
      return generateHTML({
        title: 'Unexpected Error',
        content: `
          <h3>Unexpected Error</h3>
          <p>An unexpected error occurred during authentication.</p>
          <p>Details: ${error.message}</p>
        `,
        isError: true,
        headers: {
          'Set-Cookie': 'github_auth_state=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0'
        }
      });
    }
  }
};
```

The GitHub API has been around for a very long time, so it shouldn't be surprising that Claude knows exactly how to write the above code. I was still delighted at how much work it had saved me.

(I should mention now that I completed the entire initial project on my phone, before I got up to make the morning coffee.)

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

The initial code that Claude wrote was missing an important detail: error handling. If the GitHub API returns an error - e.g. because the `?code=` is invalid - the page won't reflect that to the user.

I pasted in the code and prompted:

> `Add error handling to this Cloudflare Workers script - if the GitHub API returns an error it should be shown to the user`

Claude [wrote more code](https://gist.github.com/simonw/85debbdf3d981ff7e54f8cdb6be47578#create-github-oauth-cloudflare-worker-with-error-handling), but it was a bit verbose. I prompted:

> `refactor that code to have less code for the HTML`

And [got back this](https://gist.github.com/simonw/85debbdf3d981ff7e54f8cdb6be47578#rewrite-untitled), which is much better. 

Here's [an example page](https://tools.simonwillison.net/github-auth?code=bad-code) showing the new error message.

## Preventing CSRF attacks

Robert Munteanu [on Mastodon](https://fosstodon.org/@rombert/113566295983095957):

> I have looked into OAuth 2.0 and OIDC recently, I wonder what your toughts are about adding CSRF protection? There seems to be no checking of the state parameter in the workers code.
>
> https://www.rfc-editor.org/rfc/rfc6749#section-10.12

He's absolutely right! The `state=` parameter was being set but in the first few versions of the code it wasn't being checked later.

### Understanding the attack

I started thinking this through with the help of Claude: I [pasted in the code](https://gist.github.com/simonw/e87e55dfe13e7201dc0ae5042bc4d4eb) and prompted:

> `Explain the consequences of this not checking the state parameter`

Some back and forth I'm ready to explain this in my own words.

The specific attack to worry about here is one where an attacker tricks/forces a user into signing in to an account that the _attacker_ controls.

For my Gist example here, imagine if I could create a brand new GitHub account and then trick you into signing in to that account using OAuth, while giving you the impression that you had signed into your own account.

If the user saves a Gist containing their private information, you can now access that as the real owner of the account.

With GitHub OAuth here's how that could happen: as an attacker, I could initiate the OAuth flow against my new dedicated malicious account, and then at the end intercept that final redirect URL with the `?code=` parameter:

```
https://tools.simonwillison.net/github-auth?code=auth-code-I-generated
```
Rather than visit that URL I instead send it to my target and trick them into clicking on it.

When they visit that page the Worker exchanges that `?code=` for an access token against MY account and stores that in my victim's `localStorage`.

Now any Gists they save will be visible to me as the account's real owner.

### How to prevent it

This attack is why the OAuth specification describes the `&state=` parameter. This is a random value that the client generates and then sends to the server. The server echoes that value back to the client in the final redirect URL as the `?state=` parameter.

To avoid CSRF attacks, we need to record that initial generated `state` and then compare it to the `state=` in the final redirect URL.

I pasted in another copy of my script and prompted Claude:

> `Modify this to store the state= parameter in an HTTP only session cookie called github_auth_state and then compare that when the user comes back and show an error if they do not match, otherwise unset the cookie and complete the operation`

Claude [wrote some code](https://gist.github.com/simonw/ae56f00572dd80f9180687f9532a8226#create-github-oauth-worker-with-state-validation), but when I tried it out on Cloudflare I got this error... which I pasted back into Claude as a follow-up prompt:

> `Unexpected Error An unexpected error occurred during authentication. Details: Can't modify immutable headers.`

This time it [wrote code that worked](https://gist.github.com/simonw/ae56f00572dd80f9180687f9532a8226#rewrite-untitled) - it turns out the correct pattern for sending custom HTTP headers in a Cloudflare Worker looks like this:

```javascript
return new Response(`
  <!DOCTYPE html>
  <html>...</html>
`, {
  headers: {
    'Content-Type': 'text/html',
    ...headers
  },
);
```
