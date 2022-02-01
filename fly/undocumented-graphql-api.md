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
Here's a much more fun query:
```graphql
{
  # Your user account:
  viewer {
    avatarUrl
    createdAt
    email
    # This returned the following for me:
    # ["backend_wordpress", "response_headers_middleware", "firecracker", "dashboard_logs"]
    featureFlags
  }
  nearestRegion {
    # This returned "sjc"
    code
  }
  personalOrganization {
    name
    creditBalance
    creditBalanceFormatted
    # Not sure what these are but they look interesting - I have 7
    loggedCertificates {
      totalCount
      nodes {
        cert
        id
        root
      }
    }
    isCreditCardSaved
    wireGuardPeers {
      # Returned one entry for me, with name:
      # interactive-Simons-MacBook-Pro-swillison-gmail-com-26
      # Presumably the flyctl CLI command set this up
      totalCount
      nodes {
        name
        network
        peerip
        pubkey
        region
      }
    }
  }
}
```
This one returns recent logs (only for the past hour / max of 50 values - those are the highest numbers that can be used for those parameters):
```graphql
{
  apps {
    nodes {
      name
      vms {
        totalCount
        nodes {
          recentLogs(limit: 50, range: 3600) {
            id
            region
            message
            timestamp
          }
        }
      }
    }
  }
}
```
And another one which digs into the details of attached volumes:
```graphql
{
  apps {
    nodes {
      name
      services {
        checks {
          httpPath
          httpMethod
          name
        }
        description
      }
      volumes {
        nodes {
          id
          name
          createdAt
          host {
            id
          }
          sizeGb
          status
          usedBytes
          region
          app {
            name
          }
          attachedAllocation {
            privateIP
            # Not sure why attachedAllocation on a volume gives app HTTP traffic logs:
            recentLogs {
              id
              message
              timestamp
            }
            canary
            events {
              message
              timestamp
            }
          }
        }
      }
    }
  }
}
```
