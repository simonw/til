# Using LLM in the shebang line of a script

[This comment](https://news.ycombinator.com/item?id=48073246#48090590) on Hacker News inspired me to investigate patterns for using my [LLM](https://llm.datasette.io/) CLI tool in a shebang line:

> But seriously, you can put a shebang on an english text file now (if you're sufficiently brave) [...]

LLM can end up installed in all sorts of unpredictable places so the best way to run it is via the `#!/usr/bin/env` pattern.

Here's how to make English (or Spanish or any other language) text executable via LLM:

```
#!/usr/bin/env -S llm -f
Generate an SVG of a pelican riding a bicycle
```

Save this as `pelican.sh` and make it executable with:
```bash
chmod +x pelican.sh
```
Then run it:
```bash
./pelican.sh
```
Other arguments will be passed through to LLM, so if you want to use a different model:
```bash
./pelican.sh -m gpt-5.4-nano
```
This prompt often returns commentary in addition to an SVG. To extract just the first code block in the response add the `-x` LLM option:

```
#!/usr/bin/env -S llm -x -f
Generate an SVG of a pelican riding a bicycle
```

The `-f` option needs to come last as it will be passed the path to the script file.

## How this works

    #!/usr/bin/env -S llm -f

The `-S` (for split) option to `env` is required because, without it, the `env` command will treat the rest of the line as the full name of the command, producing this error:

> `/usr/bin/env: 'llm -f': No such file or directory`

With `-S` the `-f` is passed as an argument to LLM, and then the path to the file itself is passed after that:

    llm -f path/to/pelican.sh

This takes advantage of [LLM's fragments mechanism](https://llm.datasette.io/en/stable/fragments.html). The argument to `-f` is the path to a file, and the contents of that file will then be appended to the prompt.

## Adding tools

Scripts like this are a lot more interesting if they can execute tools.

LLM has some [default tools](https://llm.datasette.io/en/stable/tools.html#default-tools) which you can try out. Here's how to use the `llm_time` tool which makes the current time available for the model to call:

```
#!/usr/bin/env -S llm -T llm_time -f
Write a haiku that mentions the exact current time
```
I got (at 17:52 UTC):

> Whispers of the hour,  
> Seventeen fifty-two chimes,  
> Time flows ever on.

## Using templates

LLM supports [templates](https://llm.datasette.io/en/stable/templates.html) - YAML files that can mix a prompt, system prompt, model options, and tool definitions.

These can be used with a shebang line by ending that line with a `-t`, for example:
```yaml
#!/usr/bin/env -S llm -t
prompt: Write a haiku
system: Output Spanish
```

I got this:

> Brisa en el bosque,  
> hojas susurran sueños,  
> paz en el silencio.

Templates can include parameters, for example:

```yaml
#!/usr/usr/bin/env -S llm -t
prompt: |
  Two line poem about $animal who lives in $place
```

This needs to be run like this:
```bash
./poem.sh -p animal skunk -p place "hovercraft port"
```
> In hovercraft's hum, where the engines start,  
> A skunk claims his kingdom, with pride and art.

## Templates with tools

The most interesting way to use templates is with embedded tool functions. Here's a simple example of that, saved as `calc.sh`:
```yaml
#!/usr/bin/env -S llm -t
model: gpt-5.4-mini
system: |
  Use tools to run calculations
functions: |
  def add(a: int, b: int) -> int:
      return a + b
  def multiply(a: int, b: int) -> int:
      return a * b
```
Then:
```bash
chmod 755 calc.sh
./calc.sh 'what is 2344 * 5252 + 134' --td
```
Which outputs (thanks to the `--td` tool debug option):
```
Tool call: multiply({'a': 2344, 'b': 5252})
  12310688

Tool call: add({'a': 12310688, 'b': 134})
  12310822

2344 × 5252 + 134 = **12,310,822**
```

Here's a more complex example which defines a tool for searching my blog:

```yaml
#!/usr/usr/bin/env -S llm -t
model: gpt-5.5
system: |
  You answer questions from Simon Willison's blog
functions: |
  import httpx

  url = "https://datasette.simonwillison.net/simonwillisonblog.json"
  sql = """
  WITH results AS (
    SELECT 'entry' AS type, blog_entry.id AS id, blog_entry.slug AS slug,
           blog_entry.title AS title, blog_entry.created AS created,
           snippet(blog_entry_fts, -1, '<mark>', '</mark>', '…', 100) AS snippet,
           blog_entry_fts.rank AS rank
    FROM blog_entry_fts JOIN blog_entry ON blog_entry.rowid = blog_entry_fts.rowid
    WHERE blog_entry_fts MATCH :q
    UNION ALL
    SELECT 'blogmark', blog_blogmark.id, blog_blogmark.slug,
           blog_blogmark.link_title, blog_blogmark.created,
           snippet(blog_blogmark_fts, -1, '<mark>', '</mark>', '…', 100),
           blog_blogmark_fts.rank
    FROM blog_blogmark_fts JOIN blog_blogmark ON blog_blogmark.rowid = blog_blogmark_fts.rowid
    WHERE blog_blogmark_fts MATCH :q
    UNION ALL
    SELECT 'quotation', blog_quotation.id, blog_quotation.slug,
           blog_quotation.source, blog_quotation.created,
           snippet(blog_quotation_fts, -1, '<mark>', '</mark>', '…', 100),
           blog_quotation_fts.rank
    FROM blog_quotation_fts JOIN blog_quotation ON blog_quotation.rowid = blog_quotation_fts.rowid
    WHERE blog_quotation_fts MATCH :q
    UNION ALL
    SELECT 'note', id, slug, title, created,
           -- crude snippet: ~100 chars around the first match
           -- because notes do not yet have FTS enabled
           '…' || substr(body, max(1, instr(lower(body), lower(:q)) - 40), 200) || '…',
           0.0  -- no real rank available
    FROM blog_note
    WHERE body LIKE '%' || :q || '%' OR title LIKE '%' || :q || '%'
  )
  SELECT snippet FROM results
  ORDER BY rank
  LIMIT 20
  """

  def search_blog(query: str) -> str:
      """Search Simon's blog"""
      return httpx.get(url, params={"sql": sql, "q": query}).text
```

This sets up a tool called `search_blog(query)` which then executes an HTTP request against my [datasette.simonwillison.net](https://datasette.simonwillison.net/) Datasette instance carrying a SQL query that searches various types of content.

Result:
```bash
./blog.sh "Has Simon implemented GraphQL?"
```
Output:

> Yes. Simon implemented GraphQL support for Datasette as a plugin called **`datasette-graphql`**.
>
> He described it as “a plugin that adds GraphQL query support to Datasette,” and later as a “Datasette plugin providing an automatic GraphQL API for your SQLite databases.” It can expose Datasette tables through GraphQL, including nested fields based on foreign-key relationships.

Here's the [full log](https://gist.github.com/simonw/551375ddec4dea1994bcaf299c473396) of that response showing the tool calls that were executed.
