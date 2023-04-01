# Using the ChatGPT streaming API from Python

I wanted to stream the results from the ChatGPT API as they were generated, rather than waiting for the entire thing to complete before displaying anything.

Here's how to do that with the [openai Python library](https://github.com/openai/openai-python):

```python
import openai
openai.api_key = open("/Users/simon/.openai-api-key.txt").read().strip()

for chunk in openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[{
        "role": "user",
        "content": "Generate a list of 20 great names for sentient cheesecakes that teach SQL"
    }],
    stream=True,
):
    content = chunk["choices"][0].get("delta", {}).get("content")
    if content is not None:
        print(content, end='')
```
Running this code in a Jupyter notebook does the following:

![It outputs a list of cheesecakes one token at a time](https://user-images.githubusercontent.com/9599/229312744-a2013a06-3a53-4a46-9e40-3080e4887ff7.gif)

## Using async/await

The OpenAI Python library can also work with `asyncio`. Here's how to do the above using their `async/await` support - with the `.acreate()` method:

```python
async for chunk in await openai.ChatCompletion.acreate(
    model="gpt-3.5-turbo",
    messages=[{
        "role": "user",
        "content": "Generate a list of 20 great names for sentient cheesecakes that teach SQL"
    }],
    stream=True,
):
    content = chunk["choices"][0].get("delta", {}).get("content")
    if content is not None:
        print(content, end='')
```

## Those chunks

Here's what those chunks look like - the first two and then the last two:
```
{
  "choices": [
    {
      "delta": {
        "role": "assistant"
      },
      "finish_reason": null,
      "index": 0
    }
  ],
  "created": 1680380941,
  "id": "chatcmpl-70c8LVUSYoSbdQTyONgJfcVU542wO",
  "model": "gpt-3.5-turbo-0301",
  "object": "chat.completion.chunk"
}

{
  "choices": [
    {
      "delta": {
        "content": "1"
      },
      "finish_reason": null,
      "index": 0
    }
  ],
  "created": 1680380941,
  "id": "chatcmpl-70c8LVUSYoSbdQTyONgJfcVU542wO",
  "model": "gpt-3.5-turbo-0301",
  "object": "chat.completion.chunk"
}

# ... lots more here ...

{
  "choices": [
    {
      "delta": {
        "content": "ina"
      },
      "finish_reason": null,
      "index": 0
    }
  ],
  "created": 1680380941,
  "id": "chatcmpl-70c8LVUSYoSbdQTyONgJfcVU542wO",
  "model": "gpt-3.5-turbo-0301",
  "object": "chat.completion.chunk"
}

{
  "choices": [
    {
      "delta": {},
      "finish_reason": "stop",
      "index": 0
    }
  ],
  "created": 1680380941,
  "id": "chatcmpl-70c8LVUSYoSbdQTyONgJfcVU542wO",
  "model": "gpt-3.5-turbo-0301",
  "object": "chat.completion.chunk"
}
```
