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

The resulting (but truncated) JSON from the GraphQL query looks like this:

```json
{
  "data": {
    "search": {
      "repositoryCount": 22,
      "nodes": [
        {
          "__typename": "Repository",
          "nameWithOwner": "simonw/csv-diff",
          "description": "Python CLI tool and library for diffing CSV and JSON files",
          "defaultBranchRef": {
            "name": "main",
            "target": {
              "committedDate": "2021-02-23T02:53:11Z",
              "url": "https://github.com/simonw/csv-diff/commit/33e0a5918283c02a339a1fb507fc7a9cda89a198",
              "message": "Handle missing JSON keys, refs #13"
            }
          }
        },
```

## Combining it with sqlite-utils insert

My end goal was to create a SQLite database with a record for each of my GitHub repositories that were tagged `git-scraping` that included the date of their most recent commit. Here's how I did that:

```
curl https://api.github.com/graphql -X POST \
-H "Authorization: Bearer ..." \
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
}' '{"query":$query}')" \
  | jq .data.search.nodes | sqlite-utils insert /tmp/github.db repos - --flatten
```
The line doing the work at the end is:

    | jq .data.search.nodes | sqlite-utils insert /tmp/github.db repos - --flatten

This uses `jq` to pull out the `{"data": {"search": {"nodes": [...]` array from the returned JSON, then pipes that into [sqlite-utils insert](https://sqlite-utils.datasette.io/en/stable/cli.html#cli-inserting-data).

This line does the rest:

    sqlite-utils insert /tmp/github.db repos - --flatten

That reads from standard input (`-`) and creates a `repos` table in the new `github.db` SQLite file.

The `--flatten` option at the end ensures that nested fields such as `{"defaultBranchRef": {"target": {"committedDate": ...` are flattened to columns with names like `defaultBranchRef_target_committedDate`.

The final table schema looks like this:

```
% sqlite-utils schema /tmp/github.db 
CREATE TABLE [repos] (
   [__typename] TEXT,
   [nameWithOwner] TEXT,
   [description] TEXT,
   [defaultBranchRef_name] TEXT,
   [defaultBranchRef_target_committedDate] TEXT,
   [defaultBranchRef_target_url] TEXT,
   [defaultBranchRef_target_message] TEXT
);
```
