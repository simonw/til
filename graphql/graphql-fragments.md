# GraphQL fragments

One of [the scripts](https://github.com/simonw/datasette.io/blob/main/build_directory.py) that builds and deploys [datasette.io](https://datasette.io/) uses a GraphQL query to retrieve information from GitHub about the repositories used for the various Datasette tools and plugins.

That query was [very big](https://gist.github.com/simonw/80ef5a69f147741009d0edea4ef3b6ea) - over 4,000 lines long!

That's because it was shaped like this:
```graphql
{
  repo_0: repository(name: "datasette-query-history", owner: "bretwalker") {
    id
    nameWithOwner
    createdAt
    openGraphImageUrl
    usesCustomOpenGraphImage
    defaultBranchRef {
      target {
        oid
      }
    }
    repositoryTopics(first: 100) {
      totalCount
      nodes {
        topic {
          name
        }
      }
    }
    openIssueCount: issues(states: [OPEN]) {
      totalCount
    }
    closedIssueCount: issues(states: [CLOSED]) {
      totalCount
    }
    releases(last: 1) {
      totalCount
      nodes {
        tagName
      }
    }
  }
  # ...
  repo_137: repository(name: "yaml-to-sqlite", owner: "simonw") {
    id
    nameWithOwner
    createdAt
    openGraphImageUrl
    usesCustomOpenGraphImage
    defaultBranchRef {
      target {
        oid
      }
    }
    repositoryTopics(first: 100) {
      totalCount
      nodes {
        topic {
          name
        }
      }
    }
    openIssueCount: issues(states: [OPEN]) {
      totalCount
    }
    closedIssueCount: issues(states: [CLOSED]) {
      totalCount
    }
    releases(last: 1) {
      totalCount
      nodes {
        tagName
      }
    }
  }
}
```
That block was repeated for every repository - 138 in total!

I figured there was likely a way to do this more efficiently, and it turns out there is: [GraphQL fragments](https://www.apollographql.com/docs/react/data/fragments/).

Here's that example query rewritten to use fragments instead:

```graphql
fragment repoFields on Repository {
  id
  nameWithOwner
  createdAt
  openGraphImageUrl
  usesCustomOpenGraphImage
  defaultBranchRef {
    target {
      oid
    }
  }
  repositoryTopics(first: 100) {
    totalCount
    nodes {
      topic {
        name
      }
    }
  }
  openIssueCount: issues(states: [OPEN]) {
    totalCount
  }
  closedIssueCount: issues(states: [CLOSED]) {
    totalCount
  }
  releases(last: 1) {
    totalCount
    nodes {
      tagName
    }
  }
}
{
  repo_0: repository(name: "datasette-query-history", owner: "bretwalker") {
    ...repoFields
  }
  repo_137: repository(name: "yaml-to-sqlite", owner: "simonw") {
    ...repoFields
  }
}
```
Now each additional repo added to the query is only 3 extra lines of GraphQL, not 30!
