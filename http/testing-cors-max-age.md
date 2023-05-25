# Testing the Access-Control-Max-Age CORS header

Today I noticed that [Datasette](https://datasette.io/) wasn't serving  a `Access-Control-Max-Age` header.

This meant that any `OPTIONS` CORS pre-flight requests would be repeated for every request, which hurts performance - the browser should be able to cache the result of the pre-flight request for a period of time instead.

I fixed that in [issue 2079](https://github.com/simonw/datasette/issues/2079) with [this commit](https://github.com/simonw/datasette/commit/b49fa446d683ddcaf6faf2944dacc0d866bf2d70) - so now Datasette running with the `--cors` option serves the following headers:

    Access-Control-Allow-Origin: *
    Access-Control-Allow-Headers: Authorization, Content-Type
    Access-Control-Expose-Headers: Link
    Access-Control-Allow-Methods: GET, POST, HEAD, OPTIONS
    Access-Control-Max-Age: 3600

I wanted to prove to myself that this was having the desired effect.

## Testing pre-flight requests

Here's the way I ended up testing that this was working. I opened up https://www.example.com/ and ran this in the console:

```javascript
fetch('https://latest.datasette.io/ephemeral/foo/1/-/update', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ test: 'test' })
});
```
Then I hit "up" and ran it again. Then I looked in the Network panel in Firefox to see what requests had been made.

I ran this against two sites - `latest.datasette.io` which was running the new code that added the `max-age` header, and `latest-with-plugins.datasette.io` which didn't serve that header.

The first time I ran this experiment I saw this:

![Firefox network panel, showing the following requests to latest.datasette.io: OPTIONS, POST, OPTIONS, POST, OPTIONS, POST, OPTIONS, POST](https://github.com/simonw/til/assets/9599/4d9eba7f-79b6-4eb1-9097-61aa2c54b67f)

It didn't seem to have made a difference - each POST was still preceded by an OPTIONS request.

Then I noticed that the "Disable Cache" checkbox was checked! It turns out this disables CORS pre-flight caching as well.

After I turned that off and ran my experiment again I learned something else: according to the [fetch specification](https://fetch.spec.whatwg.org/#http-access-control-max-age) the default value for `Access-Control-Max-Age` is 5s - so testing within a 5s interval won't trigger a new OPTIONS request.

Having figured that out, I managed to get the following result:

![POST to latest. POST to latest. OPTIONS to latest-with-plugins. POST to latest-with-plugins. POST to latest-with-plugins, less than 2s after the previous one. OPTIONS to latest-with-plugins 6s after the previous one. POST to latest-with-plugins. POST to latest.](https://github.com/simonw/til/assets/9599/de8d8009-7d14-42ed-8d07-16ca9f10ef57)

Note how the calls to `latest-with-plugins` are all preceded by an OPTIONS request, with the exception of the duplicate call which happens within 5s of the previous one.

None of the calls to `latest` have an OPTIONS request, because the caching for an hour is working as planned.

Here's the full sequence of commands I ran to generate this result:

```javascript
fetch('https://latest.datasette.io/ephemeral/foo/1/-/update', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ test: 'test' })
});
// And run it again
fetch('https://latest.datasette.io/ephemeral/foo/1/-/update', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ test: 'test' })
});
// Now try a thing that doesn't serve that max-age header yet:
fetch('https://latest-with-plugins.datasette.io/ephemeral/foo/1/-/update', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ test: 'test' })
});
// And a second time but within 5s
fetch('https://latest-with-plugins.datasette.io/ephemeral/foo/1/-/update', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ test: 'test' })
});
// Third time after waiting longer than 5s
fetch('https://latest-with-plugins.datasette.io/ephemeral/foo/1/-/update', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ test: 'test' })
});
// Try that original one again - still within the 1hr cache time
fetch('https://latest.datasette.io/ephemeral/foo/1/-/update', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ test: 'test' })
});
```
