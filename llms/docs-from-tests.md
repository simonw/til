# Generating documentation from tests using files-to-prompt and LLM

I was experimenting with [wasmtime-py](https://github.com/bytecodealliance/wasmtime-py) today and found the [current documentation](https://bytecodealliance.github.io/wasmtime-py/) didn't quite give me the information that I needed.

The package has [a solid looking test suite](https://github.com/bytecodealliance/wasmtime-py/tree/main/tests), so I decided to see if I could generate additional documentation based on that.

I started with a checkout of the repo:

```bash
cd /tmp
git clone https://github.com/bytecodealliance/wasmtime-py
```
The tests are all in the `test/` folder, so I used my [files-to-prompt](https://github.com/simonw/files-to-prompt) tool to turn every `.py` file in that folder into a single prompt, using the XML-ish format that Claude likes (the `-c` option):

```bash
files-to-prompt wasmtime-py/tests -e py -c
```
Piping that through [ttok](https://github.com/simonw/ttok) shows that it's about 34,780 OpenAI tokens. I pasted the whole thing (` | pbcopy` to copy to my clipboard) into my [Claude token counter](https://tools.simonwillison.net/claude-token-counter) tool and got 43,490 - easily enough to fit Claude 3.5 Sonnet's 200,000 limit.

So I ran this:

```bash
files-to-prompt -e py wasmtime-py/tests -c | \
  llm -m claude-3.5-sonnet -s \
  'write detailed usage documentation including realistic examples'
```
I'm using [llm-claude-3](https://github.com/simonw/llm-claude-3) here and a system prompt of:

> `write detailed usage documentation including realistic examples`

Here's a short exceprt of the result:

> ## Basic Usage
> 
> ### Engine and Store
> 
> ```python
> from wasmtime import Engine, Store
> 
> # Create an engine
> engine = Engine()
> 
> # Create a store 
> store = Store(engine)
> ```
> 
> The Engine handles compilation settings and caching. The Store holds runtime state for instances.
> 
> ### Loading Modules
> 
> ```python
> from wasmtime import Module
> 
> # From WAT text format
> module = Module(engine, '(module)')
> 
> # From binary Wasm
> with open('module.wasm', 'rb') as f:
>     module = Module(engine, f.read())
> ```

You can see [the full transcript here](https://gist.github.com/simonw/351cffbd254af5cbf329377fb95fcc13), saved using `llm logs -c | pbcopy` (I then hand-edited in a `<details><summary>` to hide the lengthy piped input). As always I'm sharing the transcript in a private Gist to keep this AI-generated, unverified text from being indexed by search engines.

At the end of the first chunk of output Claude offered the following:

> This documentation covers the core functionality. The bindings also support more advanced features like:
> 
> * Component model and interface types
> * Resource types and references
> * Custom linking and importing
> * Memory management controls
> * Execution limits and interruption
>
> Let me know if you would like me to expand on any of these topics!

So I followed up with another prompt (using `llm -c` for "continue current conversation"):

```bash
llm -c 'write a detailed section about memory management and one about execution limits'
```

This produced [a useful continuation of the documentation](https://gist.github.com/simonw/351cffbd254af5cbf329377fb95fcc13#response-1).

How good is this documentation? It's pretty solid! The _only_ thing it had to go on was the content of those tests, so I can be reasonably confident it didn't make any glaringly terrible mistakes and that the examples it gave me are more likely than not to execute.

Someone with more depth of experience with the project than me could take this as an initial draft and iterate on it to create verified, generally useful documentation.
