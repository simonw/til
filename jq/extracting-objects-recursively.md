# Extracting objects recursively with jq

The Algolia-powered Hacker News API returns nested comment threads that look like this: https://hn.algolia.com/api/v1/items/27941108

(For this story: https://news.ycombinator.com/item?id=27941108)

```json
{
    "id": 27941108,
    "created_at": "2021-07-24T14:15:05.000Z",
    "type": "story",
    "author": "edward",
    "title": "Fun with Unix domain sockets",
    "url": "https://simonwillison.net/2021/Jul/13/unix-domain-sockets/",
    "children": [
        {
            "id": 27942287,
            "created_at": "2021-07-24T16:31:18.000Z",
            "type": "comment",
            "author": "DesiLurker",
            "text": "<p>one lesser known...",
            "children": []
        },
        {
            "id": 27944615,
            "created_at": "2021-07-24T21:26:33.000Z",
            "type": "comment",
            "author": "galaxyLogic",
            "text": "<p>I read this from Wikipedia...",
            "children": [
                {
                    "id": 27944746,
                    "created_at": "2021-07-24T21:49:07.000Z",
                    "type": "comment",
                    "author": "hughrr",
                    "text": "<p>Yes although I ...",
                    "children": []
                }
            ]
        }
    ]
}
```
I wanted to flatten this into an array of items so I could send it to `sqlite-utils insert`. This recipe worked:

```
curl 'https://hn.algolia.com/api/v1/items/27941108' \
  | jq '[recurse(.children[]) | del(.children)]' \
  | sqlite-utils insert hn.db items - --pk id
```
The `jq` recipe here is:

```jq
[recurse(.children[]) | del(.children)]
```

The first `recurse(.children[])` recurses through a list of everything in a `.children` array.

The `| del(.children)` then deletes that array from the returned objects.

Wrapping it all in `[ ]` ensures the overall result will be an array.

Applied against the above example, this returns:

```json
[
    {
        "id": 27941108,
        "created_at": "2021-07-24T14:15:05.000Z",
        "type": "story",
        "author": "edward",
        "title": "Fun with Unix domain sockets",
        "url": "https://simonwillison.net/2021/Jul/13/unix-domain-sockets/"
    },
    {
        "id": 27942287,
        "created_at": "2021-07-24T16:31:18.000Z",
        "type": "comment",
        "author": "DesiLurker",
        "text": "<p>one lesser known..."
    },
    {
        "id": 27944615,
        "created_at": "2021-07-24T21:26:33.000Z",
        "type": "comment",
        "author": "galaxyLogic",
        "text": "<p>I read this from Wikipedia..."
    },
    {
        "id": 27944746,
        "created_at": "2021-07-24T21:49:07.000Z",
        "type": "comment",
        "author": "hughrr",
        "text": "<p>Yes although I ..."
    }
]
```
