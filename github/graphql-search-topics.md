# Searching for repositories by topic using the GitHub GraphQL API

I wanted to use the GitHub GraphQL API to return all of the repositories on the https://github.com/topics/git-scraping page.

At first glance there isn't a GraphQL field for that page - but it turns out you can access it using a GitHub search:

    topic:git-scraping sort:updated-desc

An oddity of GitHub search is that sort order can be defined using tokens that form part of the search query!

Here's a GraphQL query [tested here](https://developer.github.com/v4/explorer/) that returns the most recent 100 `git-scraping` tagged repos, sorted by most recently updated.

```graphql
{
  search(query: "topic:git-scraping sort:updated-desc", type: REPOSITORY, first: 100) {
    repositoryCount
    nodes {
      ... on Repository {
        nameWithOwner
        description
        updatedAt
        createdAt
        diskUsage
      }
    }
  }
}
```
