# Simplest possible OAuth authentication with Auth0

[Auth0](https://auth0.com/) provides an authentication API which you can use to avoid having to deal with user accounts in your own web application.

We used them last year for [VaccinateCA VIAL](https://github.com/CAVaccineInventory/vial), using the [Python Social Auth](https://github.com/python-social-auth/social-app-django) library recommended by the [Auth0 Django tutorial](https://auth0.com/docs/quickstart/webapp/django/01-login).

That was quite a lot of code, so today I decided to figure out how to implement Auth0 authentication from first principles.

Auth0 uses standard OAuth 2. Their documentation [leans very heavily](https://auth0.com/docs/quickstart/webapp) towards client libraries, but if you dig around enough you can find the [Authentication API](https://auth0.com/docs/api/authentication) documentation with the information you need.

I found that pretty late, and figured out most of this by following [their Flask tutorial](https://auth0.com/docs/quickstart/webapp/python) and then [reverse engineering](https://github.com/natbat/pillarpointstewards/issues/6) what the prototype was actually doing.

## Initial setup

To start, you need to create a new Auth0 application and note down three values. Mine looked something like this:
```python
AUTH0_DOMAIN = "pillarpointstewards.us.auth0.com"
AUTH0_CLIENT_ID = "DLXBMPbtamC2STUyV7R6OFJFDsSTHqEA"
AUTH0_CLIENT_SECRET = "..." # Get it from that page
```
You also need to decide on the "callback URL" that authenticated users will be redirected to, then add that to the "Allowed Callback URLs" setting in Auth0. You can set this as a comma-separated list.

My callback URL started out as `http://localhost:8000/callback`.

## Redirecting to Auth0

The first step is to redirect the user to Auth0 to sign in. The redirect URL looks something like this:
```
https://pillarpointstewards.us.auth0.com/authorize?
  response_type=code
  &client_id=DLXBMPbtamC2STUyV7R6OFJFDsSTHqEA
  &redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fcallback
  &scope=openid+profile+email
  &state=FtYFQBczDZemVurdBan5PjRiePPGhU
```
You can also hit https://pillarpointstewards.us.auth0.com/.well-known/openid-configuration to get back JSON describing all of the end points, but I prefer to hard-code them in rather than take on the performance overhead of that additional HTTP request.

The `state=` field there is a random string that you generate. You should store this in a cookie so you can compare it later on to [protect against CSRF attacks](https://auth0.com/docs/secure/attack-protection/state-parameters).

## User redirects back to your callback URL

The user signs in on Auth0 (which they may do via Google SSO, or by creating or using an Auth0 account). Auth0 then redirects them back to your callback URL, like this:

    https://your-site/callback?code=CODE_HERE&state=STATE_YOU_PROVIDED

Check that state against the cookie you set earlier (optional but a good idea).

Now you need to exchange the `code=` for an access token.

You do that with an authenticated server-side HTTP POST to the following URL:

`https://pillarpointstewards.us.auth0.com/oauth/token`

With these POST parameters:

```
grant_type=authorization_code
&redirect_uri=http%3A%2F%2Flocalhost%3A3000%2Fcallback
&code=804-RPsfJb9zIiLNtgP5LVKUnYor8_lN7vltl7DkRpxF-
```
The redirect URI is the same as before. The code is the code that was passed to you in the URL to the `/callback` page.

This call needs to be authenticated using HTTP basic authentication with the username set to your client ID and the password set to your client secret.

In HTTP, that looks like a `Authorization: Basic BASE64` header, where `BASE64` is the base-64 encoded string of `username:password` (or `client_id:client_secret`.

In Python using [HTTPX](https://www.python-httpx.org) that looks like this:

```python
response = httpx.post(
    "https://{}/oauth/token".format(config["domain"]),
    data={
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
        "code": code,
    },
    auth=(config["client_id"], config["client_secret"]),
)
access_token = response.json()["access_token"]
```
The response from that is a JSON object with a `"access_token"` key containing an access token.

## Fetching the user information

The `access_token` can then be used to make an authenticated API call to `https://pillarpointstewards.us.auth0.com/userinfo` to get back the user's profile:

```python
profile_response = httpx.get(
    "https://{}/userinfo".format(config["domain"]),
    headers={"Authorization": "Bearer {}".format(access_token)},
)
profile = profile_response.json()
```
And that's it!

## datasette-auth0

I implemented this in a new authentication plugin for Datasette called [datasette-auth0](https://datasette.io/plugins/datasette-auth0).

The bulk of the implementation is in this file: <https://github.com/simonw/datasette-auth0/blob/0.1a0/datasette_auth0/__init__.py>
