# Running a Python ASGI app on Zeit Now v2

Now v2 really wants you to deploy static assets with [serverless functions](https://zeit.co/docs/v2/serverless-functions/introduction) tucked away in a separate folder. They suggest creating modules like `api/index.py` which will be served up automatically as API backends to your client-side JavaScript.

It turns out you can subvert that model entirely and route all of your traffic through a single function - great for serving up Python WSGI or ASGI apps that handle traffic routing themselves.

the trick is to use the `"routes"` key in a `now.json` file like this:

```json
{
    "version": 2,
    "builds": [
        {
            "src": "json_head.py",
            "use": "@now/python"
        }
    ],
    "routes": [
        {
            "src": "(.*)",
            "dest": "json_head.py"
        }
    ]
}
```

Here `json_head.py` is a Python module which uses [Sanic](https://github.com/huge-success/sanic) to expose a `app` object that conforms to the ASGI protocol. The same trick works for [Starlette](https://github.com/encode/starlette) too, and should work for libraries that expose WSGI protocol objects such as Flask.

Some examples I've built that use this pattern:

* https://github.com/simonw/json-head
* https://github.com/simonw/gzthermal-web
* Apps published using https://github.com/simonw/datasette-publish-now

Here's [the Zeit builder code](https://github.com/zeit/now/blob/c9437e714a754da2d25ae23160d5ad9cf64e2228/packages/now-python/now_init.py#L82) that detects ASGI or WSGI apps, for a peek at how it works under the hood.

See also:

* [Hello, Zeit Now v2](https://simonwillison.net/2020/Apr/8/weeknotes-zeit-now-v2/#hello-zeit-now-v2) where I started exploring it more
* [Better Datasette on Now v2](https://simonwillison.net/2020/Apr/16/weeknotes-hacking-23-different-projects/) documenting further improvement tricks I uncovered
