# How streaming LLM APIs work

I decided to have a poke around and see if I could figure out how the HTTP streaming APIs from the various hosted LLM providers actually worked. Here are my notes so far.

## The general pattern

All three of the APIs I investigated worked roughly the same: they return data with a `content-type: text/event-stream` header, which matches the [server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events) mechanism, then stream blocks separated by `\r\n\r\n`. Each block has a `data:` JSON line. Anthropic also include a `event:` line with an event type.

Annoyingly these can't be directly consumed using the browser [EventSource](https://developer.mozilla.org/en-US/docs/Web/API/EventSource) API because that only works for GET requests, and these APIs all use POST.

## OpenAI

The following `curl` incantation runs a prompt through GPT-4o Mini and requests a streaming respones. The `"stream_options": {"include_usage": true}` bit requests that the final message in the stream include details of how many input and output tokens were charged while processing the prompt.

```bash
curl https://api.openai.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Tell me a joke"}],
    "stream": true,
    "stream_options": {
      "include_usage": true
    }
  }' \
  --no-buffer
```
That `--no-buffer` option ensures `curl` outptus the stream to the console as it arrives. Here's what I got back, with the middle truncated (see [this Gist](https://gist.github.com/simonw/47678d1437cefda06d299cbb8e5e873f) for the whole thing):
```
data: {"id":"chatcmpl-A8dyC7f6pKkQ516qqRHK6ep7Z3yG9","object":"chat.completion.chunk","created":1726623632,"model":"gpt-4o-mini-2024-07-18","system_fingerprint":"fp_483d39d857","choices":[{"index":0,"delta":{"role":"assistant","content":"","refusal":null},"logprobs":null,"finish_reason":null}],"usage":null}

data: {"id":"chatcmpl-A8dyC7f6pKkQ516qqRHK6ep7Z3yG9","object":"chat.completion.chunk","created":1726623632,"model":"gpt-4o-mini-2024-07-18","system_fingerprint":"fp_483d39d857","choices":[{"index":0,"delta":{"content":"Why"},"logprobs":null,"finish_reason":null}],"usage":null}

data: {"id":"chatcmpl-A8dyC7f6pKkQ516qqRHK6ep7Z3yG9","object":"chat.completion.chunk","created":1726623632,"model":"gpt-4o-mini-2024-07-18","system_fingerprint":"fp_483d39d857","choices":[{"index":0,"delta":{"content":" did"},"logprobs":null,"finish_reason":null}],"usage":null}

[...]

data: {"id":"chatcmpl-A8dyC7f6pKkQ516qqRHK6ep7Z3yG9","object":"chat.completion.chunk","created":1726623632,"model":"gpt-4o-mini-2024-07-18","system_fingerprint":"fp_483d39d857","choices":[{"index":0,"delta":{"content":"!"},"logprobs":null,"finish_reason":null}],"usage":null}

data: {"id":"chatcmpl-A8dyC7f6pKkQ516qqRHK6ep7Z3yG9","object":"chat.completion.chunk","created":1726623632,"model":"gpt-4o-mini-2024-07-18","system_fingerprint":"fp_483d39d857","choices":[{"index":0,"delta":{},"logprobs":null,"finish_reason":"stop"}],"usage":null}

data: {"id":"chatcmpl-A8dyC7f6pKkQ516qqRHK6ep7Z3yG9","object":"chat.completion.chunk","created":1726623632,"model":"gpt-4o-mini-2024-07-18","system_fingerprint":"fp_483d39d857","choices":[],"usage":{"prompt_tokens":11,"completion_tokens":18,"total_tokens":29,"completion_tokens_details":{"reasoning_tokens":0}}}

data: [DONE]
```
Those newlines between the chunks are actually `\r\n` sequences.

Interesting HTTP headers (I used `curl -vv` to see these):
```
content-type: text/event-stream; charset=utf-8
access-control-expose-headers: X-Request-ID
openai-organization: user-r...
openai-processing-ms: 81
openai-version: 2020-10-01
strict-transport-security: max-age=15552000; includeSubDomains; preload
x-ratelimit-limit-requests: 30000
x-ratelimit-limit-tokens: 150000000
x-ratelimit-remaining-requests: 29999
x-ratelimit-remaining-tokens: 149999979
x-ratelimit-reset-requests: 2ms
x-ratelimit-reset-tokens: 0s
x-request-id: req_31f3a97f8a5d473aebfa2fa074935618
```

## Anthropic Claude

Here's the same prompt agaist Claude 3 Sonnet:
```bash
curl https://api.anthropic.com/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "claude-3-sonnet-20240229",
    "messages": [{"role": "user", "content": "Tell me a joke"}],
    "stream": true,
    "max_tokens": 1024
  }' \
  --no-buffer
```
The `max_tokens` option is required by the Anthropic API.

I got back this (it's shorter so I didn't truncate it):
```
event: message_start
data: {"type":"message_start","message":{"id":"msg_01SxRKvzSAbPKgXu4781JHjw","type":"message","role":"assistant","model":"claude-3-sonnet-20240229","content":[],"stop_reason":null,"stop_sequence":null,"usage":{"input_tokens":11,"output_tokens":1}}               }

event: content_block_start
data: {"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}    }

event: ping
data: {"type": "ping"}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"Here"}  }

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"'s a silly"}}

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" joke for you:"}           }

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"\n\nWhy"}     }

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" can"}    }

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"'t a bicycle"}      }

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" stand up by"} }

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":" itself?"}    }

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"\nBecause it's two"} }

event: content_block_delta
data: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"-tired!"}   }

event: content_block_stop
data: {"type":"content_block_stop","index":0             }

event: message_delta
data: {"type":"message_delta","delta":{"stop_reason":"end_turn","stop_sequence":null},"usage":{"output_tokens":30}           }

event: message_stop
data: {"type":"message_stop"             }
```
Interesting HTTP headers:
```
content-type: text/event-stream; charset=utf-8
cache-control: no-cache
anthropic-ratelimit-requests-limit: 4000
anthropic-ratelimit-requests-remaining: 3999
anthropic-ratelimit-requests-reset: 2024-09-21T19:44:06Z
anthropic-ratelimit-tokens-limit: 400000
anthropic-ratelimit-tokens-remaining: 399000
anthropic-ratelimit-tokens-reset: 2024-09-21T19:43:44Z
request-id: req_0189EJVDRQDoLyxjoNqG8Dw7
```

## Google Gemini

Google Gemini returns much larger tokens chunks, so I had to prompt "Tell me a very long joke" to get back a streaming response that included multiple parts:

```bash
curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:streamGenerateContent?alt=sse&key=${GOOGLE_API_KEY}" \
  -H 'Content-Type: application/json' \
  -d '{
    "contents": [
      {
        "parts": [
          {"text": "Tell me a very long joke"}
        ]
      }
    ]
  }' \
  --no-buffer
```
I got back this:
```
data: {"candidates": [{"content": {"parts": [{"text": "A man walks into a library and asks for books about paranoia. The librarian whispers"}],"role": "model"},"finishReason": "STOP","index": 0,"safetyRatings": [{"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","probability": "NEGLIGIBLE"},{"category": "HARM_CATEGORY_HATE_SPEECH","probability": "NEGLIGIBLE"},{"category": "HARM_CATEGORY_HARASSMENT","probability": "NEGLIGIBLE"},{"category": "HARM_CATEGORY_DANGEROUS_CONTENT","probability": "NEGLIGIBLE"}]}],"usageMetadata": {"promptTokenCount": 6,"candidatesTokenCount": 16,"totalTokenCount": 22}}

data: {"candidates": [{"content": {"parts": [{"text": ", \"They're right behind you!\" The man screams and runs out of the library.\nA few days later, he returns and asks for books about"}],"role": "model"},"finishReason": "STOP","index": 0,"safetyRatings": [{"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","probability": "NEGLIGIBLE"},{"category": "HARM_CATEGORY_HATE_SPEECH","probability": "NEGLIGIBLE"},{"category": "HARM_CATEGORY_HARASSMENT","probability": "NEGLIGIBLE"},{"category": "HARM_CATEGORY_DANGEROUS_CONTENT","probability": "NEGLIGIBLE"}]}],"usageMetadata": {"promptTokenCount": 6,"candidatesTokenCount": 48,"totalTokenCount": 54}}

data: {"candidates": [{"content": {"parts": [{"text": " invisibility. The librarian whispers, \"They're right behind you!\" Again, the man screams and runs out.\nThe next day, the man comes back and asks for books about immortality. The librarian whispers, \"They're on the second floor, to the left.\" The man starts to go upstairs,"}],"role": "model"},"finishReason": "STOP","index": 0,"safetyRatings": [{"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","probability": "NEGLIGIBLE"},{"category": "HARM_CATEGORY_HATE_SPEECH","probability": "NEGLIGIBLE"},{"category": "HARM_CATEGORY_HARASSMENT","probability": "NEGLIGIBLE"},{"category": "HARM_CATEGORY_DANGEROUS_CONTENT","probability": "NEGLIGIBLE"}]}],"usageMetadata": {"promptTokenCount": 6,"candidatesTokenCount": 112,"totalTokenCount": 118}}

data: {"candidates": [{"content": {"parts": [{"text": " then turns and whispers to the librarian, \"Are you sure they're there?\" The librarian whispers back, \"I'm not sure. I just saw you go up there.\""}],"role": "model"},"finishReason": "STOP","index": 0,"safetyRatings": [{"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT","probability": "NEGLIGIBLE"},{"category": "HARM_CATEGORY_HATE_SPEECH","probability": "NEGLIGIBLE"},{"category": "HARM_CATEGORY_HARASSMENT","probability": "NEGLIGIBLE"},{"category": "HARM_CATEGORY_DANGEROUS_CONTENT","probability": "NEGLIGIBLE"}]}],"usageMetadata": {"promptTokenCount": 6,"candidatesTokenCount": 149,"totalTokenCount": 155}}
```
HTTP headers:
```
content-type: text/event-stream
content-disposition: attachment
vary: Origin
vary: X-Origin
vary: Referer
date: Sat, 21 Sep 2024 19:46:22 GMT
server: scaffolding on HTTPServer2
x-xss-protection: 0
x-frame-options: SAMEORIGIN
x-content-type-options: nosniff
server-timing: gfet4t7; dur=911
alt-svc: h3=":443"; ma=2592000,h3-29=":443"; ma=2592000
```

## Bonus: accessing these streams using HTTPX

I like using the [HTTPX](https://www.python-httpx.org/) client library for Python. Here's how to use that to show the output of a stream to the console, using the handy [httpx-sse](https://github.com/florimondmanca/httpx-sse) package:

```python
import os
import json
import asyncio
import httpx
from httpx_sse import aconnect_sse

async def stream_openai_response(prompt):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "gpt-4-turbo-preview",
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        "stream_options": {
            "include_usage": True
        }
    }
    async with httpx.AsyncClient() as client:
        async with aconnect_sse(client, "POST", url, json=data, headers=headers) as event_source:
            async for sse in event_source.aiter_sse():
                if sse.event == "error":
                    print(f"Error: {sse.data}")
                elif sse.event == "usage":
                    usage = json.loads(sse.data)
                    print(f"Usage: {usage}")
                else:
                    try:
                        chunk = json.loads(sse.data)
                        if chunk['choices'][0]['finish_reason'] is not None:
                            break
                        content = chunk['choices'][0]['delta'].get('content', '')
                        print(content, end='', flush=True)
                    except json.JSONDecodeError:
                        print(f"Failed to parse JSON: {sse.data}")

async def main():
    prompt = "Tell me a joke"
    await stream_openai_response(prompt)

if __name__ == "__main__":
    asyncio.run(main())
```

## Bonus  2: Processing streaming events in JavaScript with fetch()

With [the help of Claude](https://gist.github.com/simonw/209b46563b520d1681a128c11dd117bc), here's some JavaScript code (using asynchronous iterators) that can make an API request to this kind of stream and log out the events as they come in:
```javascript
async function* sseStreamIterator(apiUrl, requestBody, extraHeaders)  {
  const response = await fetch(apiUrl, {
    method: 'POST',
    headers: { ...{'Content-Type': 'application/json'}, ...(extraHeaders || {}) },
    body: JSON.stringify(requestBody),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break; // value is always undefined is done is true

    // stream: true ensures multi-byte characters are handled correctly
    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split(/\r?\n\r?\n/);
    buffer = events.pop() || '';

    for (const event of events) {
      const lines = event.split(/\r?\n/);
      const parsedEvent = {};

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const dataContent = line.slice(6);
          try {
            parsedEvent.data = JSON.parse(dataContent);
          } catch (error) {
            parsedEvent.data = null;
            parsedEvent.data_raw = dataContent;
          }
        } else if (line.includes(': ')) {
          const [key, value] = line.split(': ', 2);
          parsedEvent[key] = value;
        }
      }

      if (Object.keys(parsedEvent).length > 0) {
        yield parsedEvent;
      }
    }
  }
}

async function handleSSE() {
  const apiUrl = 'https://api.openai.com/v1/chat/completions';
  const requestBody = {
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Tell me a joke"}],
    "stream": true,
    "stream_options": {
      "include_usage": true
    }
  };
  for await (const event of sseStreamIterator(apiUrl, requestBody, {
    Authorization: 'Bearer sk-...'
  })) {
    console.log(event);
  }
}

handleSSE()
```
