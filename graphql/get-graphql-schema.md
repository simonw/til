# get-graphql-schema

The GraphQL schema language is a concise way to represent the available schema provided by a GraphQL endpoint. It looks something like this:

```graphql
type assets {
  url: String
  node_id: String
  name: String
  label: String
  content_type: String
  state: String
  created_at: String
  updated_at: String
  browser_download_url: String
  id: Int
  size: Int
  download_count: Int
  uploader: users
  release: releases
}

type assetsCollection {
  totalCount: Int
  pageInfo: PageInfo
  nodes: [assets]
  edges: [assetsEdge]
}
```
You can retrieve a JSON version of this from the GraphQL server itself using the query at the bottom of this document.

But... if you want it back in readable text as shown above, you can use the [get-graphql-schema]() tool. Run that like this:

    npx get-graphql-schema https://github-to-sqlite.dogsheep.net/graphql

## Retrieving the schema as JSON using GraphQL

I found this query using the network inspector against a GraphiQL instance (https://api.fly.io/graphql) that offered a "Schema" tab:

```graphql
query IntrospectionQuery {
  __schema {
    queryType {
      name
    }
    mutationType {
      name
    }
    subscriptionType {
      name
    }
    types {
      ...FullType
    }
    directives {
      name
      description
      locations
      args {
        ...InputValue
      }
    }
  }
}
fragment FullType on __Type {
  kind
  name
  description
  fields(includeDeprecated: true) {
    name
    description
    args {
      ...InputValue
    }
    type {
      ...TypeRef
    }
    isDeprecated
    deprecationReason
  }
  inputFields {
    ...InputValue
  }
  interfaces {
    ...TypeRef
  }
  enumValues(includeDeprecated: true) {
    name
    description
    isDeprecated
    deprecationReason
  }
  possibleTypes {
    ...TypeRef
  }
}
fragment InputValue on __InputValue {
  name
  description
  type {
    ...TypeRef
  }
  defaultValue
}
fragment TypeRef on __Type {
  kind
  name
  ofType {
    kind
    name
    ofType {
      kind
      name
      ofType {
        kind
        name
        ofType {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
              }
            }
          }
        }
      }
    }
  }
}
```
