# Using curl to run GraphQL queries from the command line

I wanted to run a query against the GitHub GraphQL API using `curl` on the command line, while keeping the query itself as readable as possible. Here's the recipe I came up with, with TOKEN replaced by my GitHub API personal access token:
```
curl -s https://api.github.com/graphql -X POST \
-H "Authorization: Bearer TOKEN" \
-H "Content-Type: application/json" \
-d "$(jq -c -n --arg query '
{
  search(type: REPOSITORY, query: "user:simonw topic:git-scraping", first: 100) {
    repositoryCount
    nodes {
      __typename
      ... on Repository {
        nameWithOwner
        description
        defaultBranchRef {
          name
          target {
            ... on Commit {
              committedDate
              url
              message
            }
          }
        }
      }
    }
  }
}' '{"query":$query}')"
```
As you can see, the GraphQL query itself is embedded in plain texit inside a complex set of escaping tricks.

## Building a JSON document with jq

I needed to encode the query as part of a JSON document that looks like this:

```json
{"query":"\n{\n  search(type: REPOSITORY, query: \"user:simonw topic:git-scraping\", first: 100) {\n    repositoryCount\n    nodes {\n      __typename\n      ... on Repository {\n        nameWithOwner\n        description\n        defaultBranchRef {\n          name\n          target {\n            ... on Commit {\n              committedDate\n              url\n              message\n            }\n          }\n        }\n      }\n    }\n  }\n}"}
```
The `jq` recipe handles the construction of that document for me:
```
jq -c -n --arg query '
{
  search(type: REPOSITORY, query: "user:simonw topic:git-scraping", first: 100) {
    repositoryCount
    nodes {
      __typename
      ... on Repository {
        nameWithOwner
        description
        defaultBranchRef {
          name
          target {
            ... on Commit {
              committedDate
              url
              message
            }
          }
        }
      }
    }
  }
}' '{"query":$query}'
```
`jq -c` means "compact syntax" - so the JSON itself is produced as a single line.

The `-n` option stands for `--null-input` - which is described as:

> Don´t read any input at all! Instead, the filter is run once using null as the input. This is useful when using `jq` as a simple calculator or to construct JSON data from scratch.

Then `--arg query '...'` sets a variable within jQuery to the string representing my GraphQL query.

Finally I evaluate the jQuery expression `'{"query":$query}'` which constructs the final document with my GraphQL query as the value for the `"query"` key.

## Passing that to curl with "$()"

Having constructed the JSON document, I needed to pass it to the `curl -d` option to submit it to the server.

The recipe for doing that is:

```
-d "$(jq -c -n --arg query ...)"
```

I tried doing this with `-d $(jq ...)` first, and it didn't work - because whitespace inside the substition was treated as separate tokens passed to `curl`.

Adding the wrapping double quotes caused the substition result to be treated as a single value.

I was worried that double quotes within the string itself would break out of the pattern, but [this Stackoverflow answer](https://unix.stackexchange.com/questions/289574/nested-double-quotes-in-assignment-with-command-substitut) reassured me otherwise:

> Once one is inside `$(...)`, quoting starts all over from scratch.
>
> In other words, `"..."` and `$(...)` can nest within each other. Command substitution, `$(...)`, can contain one or more complete double-quoted strings.
