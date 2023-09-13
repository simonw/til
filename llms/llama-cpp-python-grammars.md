# Using llama-cpp-python grammars to generate JSON

[llama.cpp](https://github.com/ggerganov/llama.cpp) recently added the ability to control the output of any model using a grammar.

This is an incredibly powerful technique for working with a Large Language Model. Effectively it lets you insert custom code into the model's output generation process, ensuring that the overall output exactly matches the grammar that you specify.

This works by directly modifying the next-token selection logic, restricting the model to only being able to pick from the tokens that fulfill the rules of the grammar at any given point.

The most exciting possibility for this in my opinion is building a version of OpenAI Functions on top of models like Llama 2 that can run on your own device.

I hadn't quite figured out how to use these yet, until Ian Maurer [tipped me in the right direction](https://twitter.com/imaurer/status/1699467351937224828).

Here's how to get started with them using the [llama-cpp-python](https://github.com/abetlen/llama-cpp-python) Python library.

First, install it - and make sure you have a recent version, grammars only landed on August 17th (though there have been a ton of releases since then, it's a very fast moving project).
```bash
pip install -U llama-cpp-python
```
You need a grammar. There's a set of examples in the [llama.cpp/grammars](https://github.com/ggerganov/llama.cpp/tree/master/grammars) folder.

My favourite so far is the `json_arr` one, which guarantees that the response will be a valid JSON array:

https://github.com/ggerganov/llama.cpp/blob/b52b29ab9d601bb298050bcd2261169bc917ba2c/grammars/json_arr.gbnf

I'll fetch that straight into Python using `httpx`.

You also need a model. I'm using Llama 13B as GGUF from [TheBloke/Llama-2-13B-GGUF](https://huggingface.co/TheBloke/Llama-2-13B-GGUF) - I downloaded the 8bit quantized model, a 13.8GM file from here:

https://huggingface.co/TheBloke/Llama-2-13B-GGUF/resolve/main/llama-2-13b.Q8_0.gguf

Here's my Python code that exercises it.

First, import the modules and load the grammar:

```python
from llama_cpp.llama import Llama, LlamaGrammar
import httpx
grammar_text = httpx.get("https://raw.githubusercontent.com/ggerganov/llama.cpp/master/grammars/json_arr.gbnf").text
grammar = LlamaGrammar.from_string(grammar_text)
```

Now load the model:
```python
llm = Llama("llama-2-13b.Q8_0.gguf")
```
This spews out a ton of debug output, some of which looks like this:
```
llama_model_loader: loaded meta data with 19 key-value pairs and 363 tensors from /Users/simon/Downloads/llama-2-13b.Q8_0.gguf (version GGUF V2 (latest))
llama_model_loader: - tensor    0:                token_embd.weight q8_0     [  5120, 32000,     1,     1 ]
...
llama_new_context_with_model: kv self size  =  400.00 MB
llama_new_context_with_model: compute buffer total size =   75.47 MB
AVX = 0 | AVX2 = 0 | AVX512 = 0 | AVX512_VBMI = 0 | AVX512_VNNI = 0 | FMA = 0 | NEON = 1 | ARM_FMA = 1 | F16C = 0 | FP16_VA = 1 | WASM_SIMD = 0 | BLAS = 1 | SSE3 = 0 | SSSE3 = 0 | VSX = 0 | 
```
Now we can prompt it, feeding in the grammar object as `grammer=` and setting `max_tokens=-1` for unlimited output tokens:
```python
response = llm(
    "JSON list of name strings of attractions in SF:",
    grammar=grammar, max_tokens=-1
)
```
The result is a JSON string in `response['choices'][0]['text']`, so we can pretty-print it like this:
```python
import json
print(json.dumps(json.loads(response['choices'][0]['text'], indent=4))
```
Which gave me:
```json
[
    {
        "address": {
            "country": "US",
            "locality": "San Francisco",
            "postal_code": 94103,
            "region": "CA",
            "route": "Museum Way",
            "street_number": 151
        },
        "geocode": {
            "latitude": 37.782569,
            "longitude": -122.406605
        },
        "name": "SFMOMA",
        "phone": "(415) 357-4000",
        "website": "http://www.sfmoma.org/"
    },
    {
        "address": {
            "country": "US",
            "locality": "San Francisco",
            "postal_code": 94129,
            "region": "CA",
            "route": "The Presidio",
            "street_number": 104
        },
        "geocode": {
            "latitude": 37.806566,
            "longitude": -122.440633
        },
        "name": "Walt Disney Family Museum",
        "phone": "(415) 345-6800",
        "website": "http://www.waltdisney.org/museum"
    }
]
```
As promised, the grammar ensured I got back a valid JSON array, with no filler text ("Here's the data you asked for as JSON:") which Llama 2 is very prone to including.

## Generating grammars

The model invented the shape of the JSON data. The next challenge will be to figure out how to build grammars that specify the actual JSON shape that I want.

I [got GPT-4 to prototype that for me a bit](https://chat.openai.com/share/bf84aed9-d2a3-4175-ac6e-d2f0873092d7), but it needs a lot more work before it's usable.

[Grammar Builder](https://grammar.intrinsiclabs.ai/) by Intrinsic Labs is an interesting tool here - it can generate GBNF grammars from TypeScript declarations, and is accompanied by [an open source library](https://github.com/IntrinsicLabsAI/gbnfgen) that does the same trick. More about that in [this discussion thread](https://github.com/ggerganov/llama.cpp/discussions/2494).

## Watch out for invalid JSON due to token truncation

Here's one thing to watch out for: the grammar trick doesn't 100% guarantee that you will get back valid JSON, because there's always a chance that the model will run out of tokens before it's managed to produce a completed JSON array.

I don't see any way to resolve this, unfortunately: the grammar is considered entirely separately from the part of the model that might decide that it needs to wrap things up because it's running out of tokens.

There are tricks for dealing with incomplete JSON though, especially if it's producing an array of objects where you could discard the incomplete object at the end.

Next time I dig into this I plan to experiment with [using ijson](https://til.simonwillison.net/json/ijson-stream), a streaming JSON parser, to try and account for this.
