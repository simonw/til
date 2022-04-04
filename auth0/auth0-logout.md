# Logging users out of Auth0

If you [implement Auth0](https://til.simonwillison.net/auth0/oauth-with-auth0) for login, you may be tempted to skip implementing logout. I started out just with a `/logout/` page that cleared my own site's cookies, ignoring the Auth0 side of it.

Since users were still signed in to Auth0 (still had cookies there), this meant that if they clicked "login" again after clicking "logout" they would be logged straight in without needing to authenticate at all.

There are two problems with this approach:

1. It defies user expectations. If someone logged out they want to be logged out. Users don't understand the difference between being logged out in your own site and logged out for Auth0.
2. Sometimes people have a legitimate reason for wanting to properly log out - if they are on a shared computer and they need to be able to sign out and then sign back in as a different account.

For example, a couple who share the same computer and want to sign into their own separate accounts. I ran into this use-case pretty quickly!

## Logging users out of Auth0

The good news is this is easy to implement via a redirect. Clear your own site's cookies and then send them to:

    https://YOURDOMAIN.us.auth0.com/v2/logout?client_id=YOUR_CLIENT_ID&returnTo=URL

That `returnTo` URL is where Auth0 will return them to. I used my site's homepage.

It needs to be listed under "Allowed Logout URLs" in the Auth0 settings.

Relevant Auth0 documentation:

- [Logout](https://auth0.com/docs/authenticate/login/logout) Auth0 high level documentation
- [Log Users Out of Auth0](https://auth0.com/docs/authenticate/login/logout/log-users-out-of-auth0) describes how you can log them out of Auth0 (what I wanted) or you can additionally log them out of Google SSO (not what I wanted)
- [GET /v2/logout](https://auth0.com/docs/api/authentication#logout) API documentation

I implemented this for [pillarpointstewards/issues/54](https://github.com/natbat/pillarpointstewards/issues/54), in [this commit](https://github.com/natbat/pillarpointstewards/commit/2a79046b52da79216e6548d2ef386decf6b65656).
