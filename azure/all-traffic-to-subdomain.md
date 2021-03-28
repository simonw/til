# Writing an Azure Function that serves all traffic to a subdomain

[Azure Functions](https://docs.microsoft.com/en-us/azure/azure-functions/) default to serving traffic from a path like `/api/FunctionName` - for example `https://your-subdomain.azurewebsites.net/api/MyFunction`.

If you want to serve an entire website through a single function (e.g. using [Datasette](https://datasette.io/)) you need that function to we called for any traffic to that subdomain.

Here's how to do that - to capture all traffic to any path under `https://your-subdomain.azurewebsites.net/`.

First add the following section to your `host.json` file:

```
    "extensions": {
        "http": {
            "routePrefix": ""
        }
    }
```
Then add `"route": "{*route}"` to the `function.json` file for the function that you would like to serve all traffic. Mine ended up looking like this:
```json
{
    "scriptFile": "__init__.py",
    "bindings": [
        {
            "authLevel": "Anonymous",
            "type": "httpTrigger",
            "direction": "in",
            "name": "req",
            "route": "{*route}",
            "methods": [
                "get",
                "post"
            ]
        },
        {
            "type": "http",
            "direction": "out",
            "name": "$return"
        }
    ]
}
```
See https://github.com/simonw/azure-functions-datasette for an example that uses this pattern.
