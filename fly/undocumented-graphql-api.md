# Using the undocumented Fly GraphQL API

[Fly](https://fly.io/) has a GraphQL API which is used by some of their own tools - I found it while browsing around their code on GitHub.

It's very much undocumented, which means you would be very foolish to write any software against it and expect it to continue to work as Fly make changes.

Only it is *kind of* documented, because GraphQL introspection provides decent documentation.

(Also it's used [by example code](https://github.com/fly-apps/hostnamesapi) published by Fly, so maybe it's more supported than I initially thought.)

The endpoint is `https://api.fly.io/graphql` - you need a `Authorization: Bearer xxx` HTTP header to access it, where you can get the `xxx` token by running `flyctl auth token`.

Or, you can point your browser directly at https://api.fly.io/graphql - they are running a copy of [GraphiQL](https://github.com/graphql/graphiql) there which provides an interactive explorer plus documentation and schema tabs.

And if you're signed in to the Fly web interface it will use your `.fly.io` cookies to authenticate your GraphQL requests - so no need to worry about that `Authorization` header.

Here's a query I used to answer the question "what volumes do I have attached, across all of my instances?"

```graphql
{
  apps {
    nodes {
      name
      volumes {
        nodes {
          name
        }
      }
    }
  }
}
```
