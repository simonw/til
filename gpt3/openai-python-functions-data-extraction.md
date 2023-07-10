# Using OpenAI functions and their Python library for data extraction

Here's the pattern I figured out for using the [openai](https://github.com/openai/openai-python) Python library to extract structured data from text using a single call to the model.

The official documentation [mostly demonstrates](https://github.com/openai/openai-cookbook/blob/main/examples/How_to_call_functions_with_chat_models.ipynb) how to do this by calling their HTTP API directly. Here's how to do it with the `openai` Python library instead.

Since I want to extract multiple locations in a single call, here I'm defining a `extract_locations()` function that gets passed an array of objects. Each object has a `name` and a `country_iso_alpha2`.

Passing `function_call={"name": "extract_locations"}` at the end _forces_ OpenAI to reply with a call to that function.

Note that normally you would be expected to implement a `extract_locations(locatinos)` function, call it with the data from OpenAI and then pass the results back to the model for the next step in the conversation.

But for structured data extraction, that's not necessary - we can instead use the function calling system to get the JSON data out in a single call.

You'll need to set `OPENAI_API_KEY` to your API key before running this.

```python
import openai
import json

completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-0613",
    messages=[{"role": "user", "content": "I went to London and then stopped in Istanbul and Utrecht."}],
    functions=[
        {
            "name": "extract_locations",
            "description": "Extract all locations mentioned in the text",
            "parameters": {
                "type": "object",
                "properties": {
                    "locations": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "The name of the location"
                                },
                                "country_iso_alpha2": {
                                    "type": "string",
                                    "description": "The ISO alpha-2 code of the country where the location is situated"
                                }
                            },
                            "required": ["name", "country_iso_alpha2"]
                        }
                    }
                },
                "required": ["locations"],
            },
        },
    ],
    function_call={"name": "extract_locations"}
)
choice = completion.choices[0]
encoded_data = choice.message.function_call.arguments
print(json.dumps(json.loads(encoded_data), indent=4))
```
The output from this is:
```json
{
    "locations": [
        {
            "name": "London",
            "country_iso_alpha2": "GB"
        },
        {
            "name": "Istanbul",
            "country_iso_alpha2": "TR"
        },
        {
            "name": "Utrecht",
            "country_iso_alpha2": "NL"
        }
    ]
}
```
## Adding streaming isn't worth it

Add `stream=True` to the `ChatCompletion.create()` call to turn on streaming. If you do this, you will then get back a generator you can iterate over to collect the fragments of JSON. The chunks from that generator look like this:
```python
{
  "id": "chatcmpl-7aYZDy1mAkW578SREa2say4gORGoq",
  "object": "chat.completion.chunk",
  "created": 1688947039,
  "model": "gpt-3.5-turbo-0613",
  "choices": [
    {
      "index": 0,
      "delta": {
        "role": "assistant",
        "content": null,
        "function_call": {
          "name": "extract_locations",
          "arguments": ""
        }
      },
      "finish_reason": null
    }
  ]
}
{
  "id": "chatcmpl-7aYZDy1mAkW578SREa2say4gORGoq",
  "object": "chat.completion.chunk",
  "created": 1688947039,
  "model": "gpt-3.5-turbo-0613",
  "choices": [
    {
      "index": 0,
      "delta": {
        "function_call": {
          "arguments": "{\n"
        }
      },
      "finish_reason": null
    }
  ]
}
{
  "id": "chatcmpl-7aYZDy1mAkW578SREa2say4gORGoq",
  "object": "chat.completion.chunk",
  "created": 1688947039,
  "model": "gpt-3.5-turbo-0613",
  "choices": [
    {
      "index": 0,
      "delta": {
        "function_call": {
          "arguments": " "
        }
      },
      "finish_reason": null
    }
  ]
}
{
  "id": "chatcmpl-7aYZDy1mAkW578SREa2say4gORGoq",
  "object": "chat.completion.chunk",
  "created": 1688947039,
  "model": "gpt-3.5-turbo-0613",
  "choices": [
    {
      "index": 0,
      "delta": {
        "function_call": {
          "arguments": " \""
        }
      },
      "finish_reason": null
    }
  ]
}
```
As you can see, you would need to glue together those `choices.delta.function_call.arguments` blocks into a string of JSON and then evaluate it. Since JSON doesn't parse correctly until you've retrieved the whole thing I don't think it's worth using `stream=True` with the functions mechanism at all.

I guess you could feed the results into [ijson](https://pypi.org/project/ijson/) and iteratively parse objects as they become available, but I have trouble imagining a scenario in which the effort would be worthwhile there.
