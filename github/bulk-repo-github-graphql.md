# Bulk fetching repository details with the GitHub GraphQL API

I wanted to be able to fetch details of a list of different repositories from the GitHub GraphQL API by name in a single operation.

It turns out the `search()` operation can be used for this, given 100 repos at a time. The trick is to use the `repo:` search operator, e.g `repo:simonw/datasette repo:django/django` as demonstrated by [this search](https://github.com/search?q=repo%3Asimonw%2Fdatasette+repo:simonw/sqlite-utils&type=Repositories).

Here's the GraphQL query, tried out using https://docs.github.com/en/graphql/overview/explorer

```graphql
{
  search(type: REPOSITORY, query: "repo:simonw/datasette repo:django/django", first: 100) {
    nodes {
      ... on Repository {
        id
        nameWithOwner
        createdAt
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
  }
}
```
