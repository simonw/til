# Combined release notes from GitHub with jq and paginate-json

Matt Holt [asked](https://twitter.com/mholt6/status/1690177417393135616):

> Is there a tool that uses the GitHub API to generate a doc with all release notes from a repo?

Here's how do do that with the GitHub [releases API](https://docs.github.com/en/free-pro-team@latest/rest/releases/releases?apiVersion=2022-11-28#list-releases) and [jq](https://stedolan.github.io/jq/):

```bash
curl -s 'https://api.github.com/repos/simonw/llm/releases' | \
  jq -r '.[] | "## " + .name + "\n\n*" + .created_at + "*\n\n" + .body + "\n"'
```

The output from that command (run against my [simonw/llm](https://github.com/simonw/llm) repo) starts like this:
```
## 0.6.1

*2023-07-24T15:53:48Z*

- LLM can now be installed directly from Homebrew core: `brew install llm`. [#124](https://github.com/simonw/llm/issues/124)
- Python API documentation now covers [System prompts](https://llm.datasette.io/en/stable/python-api.html#system-prompts).
- Fixed incorrect example in the [Prompt templates](https://llm.datasette.io/en/stable/templates.html#prompt-templates) documentation. Thanks, Jorge Cabello. [#125](https://github.com/simonw/llm/pull/125)

## 0.6

*2023-07-18T21:36:37Z*

- Models hosted on [Replicate](https://replicate.com/) can now be accessed using the [llm-replicate](https://github.com/simonw/llm-replicate) plugin, including the new Llama 2 model from Meta AI. More details here: [Accessing Llama 2 from the command-line with the llm-replicate plugin](https://simonwillison.net/2023/Jul/18/accessing-llama-2/).
...
```
## Handling paginated responses

The GitHub API paginates responses at 30 items per page. Each JSON document returned includes an HTTP `link` header indicating the next page, like this:
```
link: <https://api.github.com/repositories/140912432/releases?page=2>; rel="next"
```

I wrote my [paginate-json](https://github.com/simonw/paginate-json) tool to help paginate through exactly this kind of output (the WordPress API uses the same pattern, [as does Datasette](https://docs.datasette.io/en/stable/json_api.html#pagination)).

You can install that with `pip` or `pipx`:
```bash
pipx install paginate-json
```
Then run the following command to fetch and combine all pages of release notes for a larger project:
```bash
paginate-json 'https://api.github.com/repos/simonw/sqlite-utils/releases' | \
  jq -r '.[] | "## " + .name + "\n\n*" + .created_at + "*\n\n" + .body + "\n"'
```
Example output from that [is here in this Gist](https://gist.github.com/simonw/f5565b0b67cdd3591e00db67c702f5c5).

## Writing the jq recipe with ChatGPT/GPT-4

I can never remember the `jq` syntax even for simple things like this, so I [prompted GPT-4](https://chat.openai.com/share/df880b38-15e3-4398-80ae-8a95a6752244) with:
```
[{"name": "one", "created_at": "dt one", "body": "markdown here"}, {...}]

Write a jq program that turns that into a combined output:

## one

*dt one*

Markdown here

## two... etc
```
It gave me the following:
```bash
jq -r '.[] | "## " + .name + "\n\n*dt " + .created_at + "*\n\n" + .body + "\n"'
```
That wasn't exactly what I needed, but it was very easy to edit that into the final program.
