# Setting a custom price for a model in AgentsView

I'm a recent convent to [AgentsView](https://www.agentsview.io), Wes McKinney's (previously of Pandas fame) Python toolkit for analyzing transcripts of coding agents from your own computer.

AgentsView can calculate your token spending based on those transcripts, across multiple different coding agents (Claude Code, Codex, Pi and more.)

You can run it via `uvx` like this to get as ASCII table of spending numbers in your terminal:

    uvx agentsview usage daily

Example output:
```
DATE        INPUT     OUTPUT   CACHE_CR  CACHE_RD    COST      MODELS
----        -----     ------   --------  --------    ----      ------
...
2026-06-04  5248968   387578   149428    78087993    $77.72    gpt-5.5, claude-opus-4-8
2026-06-05  963595    115773   0         8383360     $8.62     gpt-5.5, gpt-5.4-mini, deepseek/deepseek-v4-flash, meta-llama/llama-3.2-3b-instruct:free, nvidia/nemotron-nano-9b-v2:free
2026-06-06  324888    36869    0         3231872     $4.35     gpt-5.5
2026-06-07  669027    46379    0         7486464     $8.48     gpt-5.5
2026-06-08  3346262   253637   0         49214208    $48.95    gpt-5.5
2026-06-09  787043    427018   1098673   78305086    $97.79    claude-fable-5, gpt-5.5, claude-haiku-4-5-20251001
----        -----     ------   --------  --------    ----      ------
TOTAL       73610282  7260576  4399393   1717538611  $1472.87  
```

Anthropic's latest model [Claude Fable 5](https://www.anthropic.com/news/claude-fable-5-mythos-5) came out today. The pricing data AgentsView uses doesn't yet include that model.

So I had [Claude Fable 5 reverse engineer AgentsView](https://claude.ai/share/28310314-36fe-4bc7-bf04-4060714ed5de) with the following prompt against [claude.ai](https://claude.ai):

> `Clone https://github.com/kenn-io/agentsview and tell me how I can set a price for a model that it does not know the price of yet`

It turns out you can add custom pricing information to your `~/.agentsview/config.toml` file. Here's what I added:

```toml
[custom_model_pricing."claude-fable-5"]
input = 10.0
output = 50.0
cache_creation = 12.50
cache_read = 1
```
I think those numbers are right, I got them [from this pricing page](https://platform.claude.com/docs/en/about-claude/pricing). Fable is 2x the price of Opus for input and output.

With the config file edited I can run Fable again to get pricing estimates. I used the `serve` command to get a web application on port 8080:

![Screenshot of a cost analytics dashboard. Cost Attribution - Click to hide from chart - toggle buttons for Project / Model / Agent and Treemap / List. A treemap shows a large red block: prod_datasette_agent $74.06 89.3%, then blue: cloud $3.98 4.8%, teal: datasette $2.81 3.4%, pink: money $1.92 2.3%, and a thin orange sliver. A legend lists 1 prod_datasette_agent $74.06, 2 cloud $3.98, 3 datasette $2.81, 4 money $1.92, 5 simon $0.15. Below left, Top Sessions by Cost: 1 Claude - Review ./datasette-agent and ./datasette-apps - we are going to a... - prod_datasette_agent · 08a1f374-0e77-420f-be2d-af805d67e8aa - 55.9M $74.06; 2 Claude - issues.db is a copy of the Datasette issues database. There are a... - datasette · 8caa2d2d-b91f-43b3-bf3a-4268995b6011 - 826.8k $2.81; 3 Claude - Consult fly-docs and then look at datasette.cloud (which launche... - cloud · bfcacc70-09d7-4b27-aaec-4bb8accd9fec - 924.7k $2.61; 4 Claude - simonwillisonblog.db is a copy of my blog, plus all my software re... - money · 0c0fb9dc-6347-4e1b-9307-3709a7cdf0c8 - 542.9k $1.92; 5 Claude - Look in datasette.cloud and figure out all remaining steps and dec... - cloud · 45963b5f-608a-4caa-ad6b-6ae81e1dbf0d - 455k $1.37; 6 Claude - simon - simon · deeccb5d-9e90-4b1e-bfe6-c2b271e1b1d4 - 26.4k $0.15. Below right, Cache Efficiency with horizontal bars: Cache Reads 57.6M (nearly full green bar), Cache Writes 769.3K, Uncached Input 64.4K, Output 300.9K (all tiny bars), and a green highlighted note: $516.62 saved vs uncached.](https://static.simonwillison.net/static/2026/agentsview-fable.jpg)

I've used the equivalent of $82.92 in tokens since getting access to Fable 5 about four and a half hours ago. This is all included in my $100/month Claude Max subscription though, which [based on prior experience](https://simonwillison.net/2026/May/27/product-market-fit/#enterprise-customers-are-now-paying-api-prices) will likely give me around 10x the token usage compared to if I was paying list price.
