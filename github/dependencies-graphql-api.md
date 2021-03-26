# Accessing repository dependencies in the GitHub GraphQL API

[Access to a Repositories Dependency Graph](https://developer.github.com/v4/previews/#access-to-a-repositories-dependency-graph) describes a preview API for accessing GitHub repository dependencies.

To access the preview you need to send this `Accept:` header: `application/vnd.github.hawkgirl-preview+json`

But... GitHub's own GraphQL explorer at https://developer.github.com/v4/explorer/ doesn't currently allow you to set custom HTTP headers.

## Installing GraphiQL

So I decided to try https://github.com/skevy/graphiql-app - since it's mentioned in the GitHub docs [here](https://developer.github.com/v4/guides/using-the-explorer/#using-graphiql).

    brew cask install graphiql

Then you can launch the app from `/Applications/GraphiQL.app`.

I created a personal access token at https://github.com/settings/tokens called graphiql and gave it all of the `read:` permissions.

I launched the graphiql app and added the following headers:

    Authorization: Bearer MY-PERSONAl-ACCESS-TOKEN
    Accept: application/vnd.github.hawkgirl-preview+json

I added `https://api.github.com/graphql` as the endpoint.

I tested it by running these queries:
```graphql
{
  user(login:"simonw") {
    id
    name
    url
    websiteUrl
  }
}
```
```graphql
{
  repository(owner:"simonw", name:"datasette") {
    id
    name
    issues {
      totalCount
    }
  }
}
```
```graphql
{
  search(type:REPOSITORY query:"datasette" first:10) {
    repositoryCount
    edges {
      node {
        __typename
        ... on Repository {
          nameWithOwner
          description
        }
      }
    }
  }
}
```
Then I figured out this query (using autocomplete) which returns dependencies detected for a repo:
```graphql
{
  repository(owner:"simonw", name:"datasette") {
    dependencyGraphManifests {
      totalCount
      nodes {
        filename
      }
      edges {
        node {
          blobPath
          dependencies {
            totalCount
            nodes {
              packageName
              requirements
              hasDependencies
              packageManager
            }
          }
        }
      }
    }
  }
}
```
This gave me back:
```json
{
  "data": {
    "repository": {
      "dependencyGraphManifests": {
        "totalCount": 1,
        "nodes": [
          {
            "filename": "setup.py"
          }
        ],
        "edges": [
          {
            "node": {
              "blobPath": "/simonw/datasette/blob/master/setup.py",
              "dependencies": {
                "totalCount": 12,
                "nodes": [
                  {
                    "packageName": "aiofiles",
                    "requirements": "~> 0.4.0",
                    "hasDependencies": false,
                    "packageManager": "PIP"
                  },
                  {
                    "packageName": "click",
                    "requirements": "~> 7.1.1",
                    "hasDependencies": false,
                    "packageManager": "PIP"
                  },
                  {
                    "packageName": "click-default-group",
                    "requirements": "~> 1.2.2",
                    "hasDependencies": true,
                    "packageManager": "PIP"
                  },
                  {
                    "packageName": "datasette",
                    "requirements": "",
                    "hasDependencies": true,
                    "packageManager": "PIP"
                  },
                  {
                    "packageName": "hupper",
                    "requirements": "~> 1.9",
                    "hasDependencies": true,
                    "packageManager": "PIP"
                  },
                  {
                    "packageName": "janus",
                    "requirements": "~> 0.4.0",
                    "hasDependencies": false,
                    "packageManager": "PIP"
                  },
                  {
                    "packageName": "jinja2",
                    "requirements": "~> 2.10.3",
                    "hasDependencies": true,
                    "packageManager": "PIP"
                  },
                  {
                    "packageName": "mergedeep",
                    "requirements": "~> 1.1.1",
                    "hasDependencies": false,
                    "packageManager": "PIP"
                  },
                  {
                    "packageName": "pint",
                    "requirements": "~> 0.9",
                    "hasDependencies": false,
                    "packageManager": "PIP"
                  },
                  {
                    "packageName": "pluggy",
                    "requirements": "~> 0.13.0",
                    "hasDependencies": true,
                    "packageManager": "PIP"
                  },
                  {
                    "packageName": "pyyaml",
                    "requirements": "~> 5.3",
                    "hasDependencies": false,
                    "packageManager": "PIP"
                  },
                  {
                    "packageName": "uvicorn",
                    "requirements": "~> 0.11",
                    "hasDependencies": true,
                    "packageManager": "PIP"
                  }
                ]
              }
            }
          }
        ]
      }
    }
  }
}
```

Sadly I really wanted to get the dependents, not the dependencies - but that's [still not available](https://stackoverflow.com/questions/58734176/how-to-use-github-api-to-get-a-repositorys-dependents-information-in-github) even as a preview API. So I [scraped them](https://github.com/dogsheep/github-to-sqlite/issues/34) instead.
