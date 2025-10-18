# Exploring OpenAI's deep research API model o4-mini-deep-research

I was reviewing some older PRs and landed [this one](https://github.com/simonw/llm-prices/pull/9) by Manuel Solorzano adding pricing for [o4-mini-deep-research](https://platform.openai.com/docs/models/o4-mini-deep-research) and [o3-deep-research](https://platform.openai.com/docs/models/o3-deep-research) to my [llm-prices.com](https://www.llm-prices.com/) site. I realized I hadn't tried those models yet so I decided to give one of them a go.

`o4-mini-deep-research` is significantly cheaper than `o3-deep-research` - $2/$8 per million for input/output compared to $10/$40 - so I tried that one.

These models are only available via the Responses API and recommend running using their "background" model. My [LLM](https://llm.datasette.io/) tooling doesn't support that yet so I used `curl` instead.

Here's what I tried:

```bash
curl https://api.openai.com/v1/responses \
  -H "Authorization: Bearer $(llm keys get openai)" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "o4-mini-deep-research-2025-06-26",
    "input": "Find locations of every surviving orchestrion in the world. Include the city, country, venue, latitude, longitude, brief description and if available a history of when and where that orchestrion was made and its path to its current location. Return a JSON array of objects. Include a notes field for anything interesting that doesn'\''t fit the other fields.",
    "reasoning": { "summary": "auto" },
    "background": true,
    "tools": [
      { "type": "web_search_preview" },
      { "type": "code_interpreter", "container": { "type": "auto" } }
    ]
  }'
```
Here's the prompt I'm using (I [really like orchestrions](https://www.niche-museums.com/115)):

> `Find locations of every surviving orchestrion in the world. Include the city, country, venue, latitude, longitude, brief description and if available a history of when and where that orchestrion was made and its path to its current location. Return a JSON array of objects. Include a notes field for anything interesting that doesn't fit the other fields.`

This returned a response ID and `"status": "queued", which started like this:

```json
{
  "id": "resp_04911070f2b5d8560068f3ccd776788190b51f5497d7b27a30",
  "object": "response",
  "created_at": 1760808151,
  "status": "queued",
```
I then polled that ID for the result, looking at the `"status"` field with `jq` each time:
```bash
curl https://api.openai.com/v1/responses/resp_04911070f2b5d8560068f3ccd776788190b51f5497d7b27a30 \
  -H "Authorization: Bearer $(llm keys get openai)" \
  -H "Content-Type: application/json" | jq .status
```
That returned `"in_progress"` for a while, and then finally `"succeeded"`.

Here's [the full JSON](https://gist.github.com/simonw/3454a4ce40f8547a5c65c911de611ff4) that came back from that final request. That's 90KB of data (after pretty-printing with `jq`).

First lets look at the cost. That JSON ended with this `"usage"` block:

```json
{
    "input_tokens": 60506,
    "input_tokens_details": {
        "cached_tokens": 0
    },
    "output_tokens": 22883,
    "output_tokens_details": {
        "reasoning_tokens": 20416
    },
    "total_tokens": 83389
}
```
Running this [through llm-prices.com](https://www.llm-prices.com/#it=60506&ot=22883&ic=2&cic=0.5&oc=8&sel=o4-mini-deep-research) for $2/$8 per million input/output tokens gives a total of 30.4076 cents.

But what about the searches it ran? Annoyingly, OpenAI don't include those in the `"usage"` block. As far as I can tell you have to calculate them yourself by counting the number of `"web_search_preview"` tool calls it made.

I count 77 of those. OpenAI's [pricing page](https://openai.com/api/pricing/) says $10.00 / 1K calls, so 1 cent per call, so that's 77 cents on search.

It also fired up code interpreter for a few things (mostly co-ordinate trasforms with `pyproj`) - the pricing page says "$0.03 / session" so I guess that's another 3 cents.

Total cost: 77 + 30.4076 + 3 = **110.4076 cents**, $1.10.

#### The results

I [added a feature]() to my [JSON string extractor](https://tools.simonwillison.net/json-string-extractor) tool to help display the result. Here's [the long strings extracted]() from that full JSON.

The thought process started like this:

> **Searching for orchestrions**
>
> I’m looking at a static page about the historical context of orchestrions, but it seems like it doesn't list where surviving ones are located. This museum might be in Switzerland and could include images. To find currently existing orchestrions, I need to explore mechanical music museums like Speelklok or check old hotels that might still have them. An orchestrion is a large self-playing instrument, often with pipes or violins. Let's search for mechanical music museums featuring orchestrions!

I [vibe-coded up](https://gist.github.com/simonw/d225134d348435c8106070cb74c78888) a quick viewer for this using Claude Code, here's [that full trace in a UI](https://tools.simonwillison.net/deep-research-viewer#gist=3454a4ce40f8547a5c65c911de611ff4). That one claims 45 searches rather than 77, I asked Claude Code and it noted that some of those `"type": "web_search_preview"` calls were `"action": "search"` but others were `"action": "open_page"`. I don't know if `"open_page"` calls count the same as searches for pricing, but the tool shows 45 searches and 24 pages visited (and 12 code executions).

![UI showing 17 thinking steps, 45 searches, 24 pages visited, 12 code executions and 180 total steps - then a thinknig block with the researching orchestrions output I quoted earlier, then a search step for "surving orchestrions" locations](https://static.simonwillison.net/static/2025/deep-research-viewer.jpg)

The output also included the JSON I had asked for - a [JSON array of 19 orchestrions](https://gist.github.com/simonw/2a0b26633802149a44e15cf1cd396f86). I dropped that in a Gist and [opened it in Datasette Lite](https://lite.datasette.io/?json=https://gist.github.com/simonw/2a0b26633802149a44e15cf1cd396f86#/data/raw) to explore it.

Then I switched back to Claude Code and had it [convert that](https://gist.github.com/simonw/ee3854ffc5d5da06591c1106d6594aa5#file-make-orchestrion-txt-L14) to GeoJSON, so I could [view it GitHub's GeoJSON viewer](https://gist.github.com/simonw/cfcee19020ad11f8fbf56267b08e466a).

Finally I had Claude Code [knock out](https://gist.github.com/simonw/ee3854ffc5d5da06591c1106d6594aa5#file-make-orchestrion-txt-L70) a custom HTML viewer just for that file, with de-duplication across identical venues. Here's [the resulting HTML](https://gist.github.com/simonw/b9f5416b37c4ceec46d8447b52be0ad2), which you can see rendered via `gitpreview.github.io` here:

https://gistpreview.github.io/?b9f5416b37c4ceec46d8447b52be0ad2

![Screenshot of the site. It lists details of an orchestrion at the Brentford Musical Museum in London.](https://static.simonwillison.net/static/2025/orchestrions-around-the-world.jpg)

#### How well did it do?

It found me 19 orchestrions across 7 venues in 7 different countries.

I haven't fact-checked them all, but the first one - at the Musical MUseum in Brentford, London - is one that I've [seen with my own eye](https://www.niche-museums.com/115). 

This clearly isn't a comprehensive list, but I'm not sure asking "deep research" tools for a comprehensive list really plays into their strengths. There's a limit on how many tool calls they can churn through in a single session.

I don't consider the results publishable outside of a TIL post explaining what I did precisely because the information still needs to be verified.

It did however highlight both [Museum Speelklok](https://www.museumspeelklok.nl/en/) in Utrecht and [The Sanfilippo Foundation](https://www.sanfilippofoundation.org/orchestrian-room.html) in Barrington, Illinois as two places I should make a pilgrimage to as soon as possible!
