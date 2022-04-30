# Intercepting fetch in a service worker

I'm learning service workers. I wanted to start with one that intercepts calls to a `/path` and returns "Hello World".

Here's the initial recipe I came up with.

`index.html` contained this:

```html
<h1>Service worker demo</h1>

<script>
const registerServiceWorker = async () => {
  if ('serviceWorker' in navigator) {
    try {
      const registration = await navigator.serviceWorker.register(
        '/sw.js',
        {
          scope: '/',
        }
      );
      if (registration.installing) {
        console.log('Service worker installing');
      } else if (registration.waiting) {
        console.log('Service worker installed');
      } else if (registration.active) {
        console.log('Service worker active');
      }
    } catch (error) {
      console.error(`Registration failed with ${error}`);
    }
  }
};

registerServiceWorker();
</script>
```
This is using the service worker registration boilerplate [from MDN](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API/Using_Service_Workers#registering_your_worker).

Then my service worker script itself in `sw.js` just does this:

```javascript
self.addEventListener('fetch', (event) => {
  const request = event.request;
  const url = (new URL(request.url));
  if (url.pathname == "/") {
    // Don't intercept hits to the homepage
    return;
  }
  const params = new URLSearchParams(url.search);
  const info = {
    url: request.url,
    method: request.method,
    path: url.pathname,
    params: Array.from(params.entries())
  };
  event.respondWith(new Response(
    `<p>Hello world! Request was: <pre>${JSON.stringify(info, null, 4)}</p>`, {
    headers: { 'Content-Type': 'text/html' }
  }));
});
```
You have to run service workers with a real web server - you can't serve them directly from disk.

I used the Python 3 one-liner recipe for that:

    python3 -m http.server 8009

Then I visited `http://localhost:8009/` to load the service worker.

Then I visited `http://localhost:8009/foo/bar?a=1&b=2` and got this:

<img alt="Hello world! Request was: {
    &quot;url&quot;: &quot;http://localhost:8009/foo/bar?a=1&b=2&quot;,
    &quot;method&quot;: &quot;GET&quot;,
    &quot;path&quot;: &quot;/foo/bar&quot;,
    &quot;params&quot;: [
        [
            &quot;a&quot;,
            &quot;1&quot;
        ],
        [
            &quot;b&quot;,
            &quot;2&quot;
        ]
    ]
}" src="https://user-images.githubusercontent.com/9599/166125219-7820133e-4c9f-4ea2-898b-87b126f07115.png">
