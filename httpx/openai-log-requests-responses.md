# Logging OpenAI API requests and responses using HTTPX

My [LLM](https://llm.datasette.io/) tool has a feature where you can set a `LLM_OPENAI_SHOW_RESPONSES` environment variable to see full debug level details of any HTTP requests it makes to the OpenAI APIs.

This broke when I upgraded the [OpenAI Python library](https://github.com/openai/openai-python) it depends on, because OpenAI switched from using [requests](https://requests.readthedocs.io/) to using [HTTPX](https://www.python-httpx.org/) and my previous mechanism [had hooked into requests](https://github.com/simonw/llm/blob/e9a6998ca38946cfef75bdb7535d8bdc652ef381/llm/default_plugins/openai_models.py#L19-L26).

I [figured out](https://github.com/simonw/llm/issues/404) how to do this against HTTPX, using the [event hooks](https://www.python-httpx.org/advanced/#event-hooks) mechanism in that library.

## Passing a custom HTTPX client to OpenAI

Using the OpenAI library starts with a client object created like this:
```python
import openai

client = openai.OpenAI(api_key="...")

# Then to run a prompt:
chat_completion = client.chat.completions.create(
    messages=[{
        "role": "user",
        "content": "Say hello",
    }],
    model="gpt-3.5-turbo",
)
print(chat_completion.choices[0].message.content)
```
The document [describes the http_client=](https://github.com/openai/openai-python/blob/main/README.md#configuring-the-http-client) parameter to that `OpenAI()` constructor, which can be used to pass in a custom HTTPX client object.

Here's a basic illustration of that, using event hooks:

```python
import httpx

client = openai.OpenAI(
    http_client=httpx.Client(
        event_hooks={
            "request": [print],
            "response": [print]
        }
    )
)
```
This sets the `print()` function as a hook for both the request and the response. Running a prompt shows the following:
```
<Request('POST', 'https://api.openai.com/v1/chat/completions')>
<Response [200 OK]>
```
## Showing detailed request and response data

I iterated my way to the following as a `response` hook. Note that you can access the original request using `response.request` so its possible to output details of both the request and the response in the same response hook:

```python
import textwrap, json

def log_response(response: httpx.Response):
    request = response.request
    print(f"Request: {request.method} {request.url}")
    print("  Headers:")
    for key, value in request.headers.items():
        if key.lower() == "authorization":
            value = "[...]"
        if key.lower() == "cookie":
            value = value.split("=")[0] + "=..."
        print(f"    {key}: {value}")
    print("  Body:")
    try:
        request_body = json.loads(request.content)
        print(
            textwrap.indent(
                json.dumps(request_body, indent=2), "    "
            )
        )
    except json.JSONDecodeError:
        print(textwrap.indent(request.content.decode(), "    "))
    print(f"Response: status_code={response.status_code}")
    print("  Headers:")
    for key, value in response.headers.items():
        if key.lower() == "set-cookie":
            value = value.split("=")[0] + "=..."
        print(f"    {key}: {value}")


client = openai.OpenAI(
    http_client=httpx.Client(
        event_hooks={
            "response": [log_response]
        }
    )
)
```
Running a prompt through this client produces the following output:
```
Request: POST https://api.openai.com/v1/chat/completions
  Headers:
    host: api.openai.com
    accept-encoding: gzip, deflate, br
    connection: keep-alive
    accept: application/json
    content-type: application/json
    user-agent: OpenAI/Python 1.0.0
    x-stainless-lang: python
    x-stainless-package-version: 1.0.0
    x-stainless-os: MacOS
    x-stainless-arch: arm64
    x-stainless-runtime: CPython
    x-stainless-runtime-version: 3.10.10
    authorization: [...]
    content-length: 82
  Body:
    {
      "messages": [
        {
          "role": "user",
          "content": "Say hello"
        }
      ],
      "model": "gpt-3.5-turbo"
    }
Response: status_code=200
  Headers:
    date: Fri, 26 Jan 2024 20:21:50 GMT
    content-type: application/json
    transfer-encoding: chunked
    connection: keep-alive
    access-control-allow-origin: *
    cache-control: no-cache, must-revalidate
    openai-model: gpt-3.5-turbo-0613
    openai-organization: user-r3e61fpak04cbaokp5buoae4
    openai-processing-ms: 391
    openai-version: 2020-10-01
    strict-transport-security: max-age=15724800; includeSubDomains
    x-ratelimit-limit-requests: 5000
    x-ratelimit-limit-tokens: 160000
    x-ratelimit-remaining-requests: 4999
    x-ratelimit-remaining-tokens: 159980
    x-ratelimit-reset-requests: 12ms
    x-ratelimit-reset-tokens: 7ms
    x-request-id: e13258766ce769e69b19b18075c88388
    cf-cache-status: DYNAMIC
    set-cookie: __cf_bm=...
    server: cloudflare
    cf-ray: 84bb76eb1ad22314-SJC
    content-encoding: br
    alt-svc: h3=":443"; ma=86400
```
I'm pretty happy with this. It redacts the `authorization` and `set-cookie` headers, which feels like the right thing to do. It pretty-prints the JSON for the request body, if possible.

## Logging the response body

There's just one missing feature: it's not showing the full content of the response.

Initially I tried displaying the response body using this:
```python
print(f"  Body: {response.content}")
```
But... this broke!

It turns out the OpenAI library takes advantage of streaming responses... but accessing `response.content` exhausted the streaming body before the OpenAI client code had a chance to read from it, which broke the library.

After a [bunch of trial and error](https://github.com/simonw/llm/issues/404#issuecomment-1912377907) I settled on the following pattern:

```python
from httpx._transports.default import ResponseStream

class _LoggingStream(ResponseStream):
    def __iter__(self) -> Iterator[bytes]:
        for chunk in super().__iter__():
            print(f"    {chunk.decode()}")
            yield chunk


def log_response(response: httpx.Response):
    # ... previous code goes here
    response.stream._stream = _LoggingStream(response.stream._stream)
```

This is a bit of a nasty hack. It's using undocumented HTTPX internals to wrap the underlying iterator with one that prints out each chunk of bytes before it is returned.

It worked... but revealed another problem. I started seeing output that looked like this, in non-streaming situations:

```
  b'\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\x03T\x90MS\xc20\x10\x86\xef\xfd\x15q\xcf\xd4iSD\xe8\xd1\xd1\x19\xbf\x0f^\x1d\xa7S\xd2\xa5\x04\xd3lL\x16\x15\x19\xfe\xbb\x93R@/9\xbco\x9e\xcd\xb3\xd9&B\x80n\xa0\x14\xa0\x965\xab\xce\x99tj\x1e/\x8b\x8d\xb5v\xfat\xf7|\xff1^\xa3\xca\xe4\xd5\xe6z\xf5\xf0\xf3r\x03\xa3H\xd0|\x85\x8a\x0f\xd4\xb9\xa2\xce\x19dMv_+\x8f5c\x9c\x9a_f\x139+\xe4\xe4\xa2/:'
  b'j\xd0D\xacu\x9c\x8e\xd3<\xcf&\xa9\xf3\xf8\xa9\xf1k \x97\xa4\x15\x06(\xc5k"\x84\x10\xdb\xfe\x8c\x8e\xb6\xc1o(E6:$\x1d\x86P\xb7\x08\xe5\xf1\x92\x10\xe0\xc9\xc4\x04\xea\x10t\xe0\xda2\x8cN\xa5"\xcbh{\xed[}\x06C\xb1;N4\xd4:O\xf3\xf8\xba]\x1bs\xcc\x17\xda\xea\xb0\xac<\xd6\x81l\xa4\x03\x93\xdb\xe3\xbbD\x88\xb7\xde|\xfdO\x06\x9c\xa7\xceq\xc5\xf4\x8e6\x0e\xcc\x07q8\xfd\xd5\xa9\x94C\xc7\xc4\xb5\xf9\xc3\xc8d\xd0\x83\xb0\t\x8c]\xb5\xd0\xb6E\xef\xbc\xdeo\xb1pU\x83\xb3b,\xa5\x9c\x16\x90\xec\x92_\x00\x00\x00\xff\xff\x03\x00sG:\x03\xcf\x01\x00\x00'
```
That's gzipped data, returned as two separate chunks which makes it hard for my code to deflate it.

I ended up solving this with another hack:

```python
def no_accept_encoding(request: httpx.Request):
    request.headers.pop("accept-encoding", None)


client = openai.OpenAI(
    http_client=httpx.Client(
        event_hooks={
            "request": [no_accept_encoding],
            "response": [log_response]
        }
    )
)
```
Here I've added a request hook which modifies the request to remove the `accept-encoding: gzip, deflate` request header. This causes the server to serve uncompressed content, side-stepping the issue entirely.

My full code for this is in [llm/utils.py](https://github.com/simonw/llm/blob/029d8e9e26806f53fb8198c583872677d53f3b98/llm/utils.py#L53-L95).

Here's what the resulting output looks like, for both streaming and non-streaming variants:

```bash
LLM_OPENAI_SHOW_RESPONSES=1 llm 'say hi shortly'
```
```
Request: POST https://api.openai.com/v1/chat/completions
  Headers:
    host: api.openai.com
    connection: keep-alive
    accept: application/json
    content-type: application/json
    user-agent: OpenAI/Python 1.10.0
    x-stainless-lang: python
    x-stainless-package-version: 1.10.0
    x-stainless-os: MacOS
    x-stainless-arch: arm64
    x-stainless-runtime: CPython
    x-stainless-runtime-version: 3.10.4
    authorization: [...]
    x-stainless-async: false
    content-length: 108
  Body:
    {
      "messages": [
        {
          "role": "user",
          "content": "say hi shortly"
        }
      ],
      "model": "gpt-4-1106-preview",
      "stream": true
    }
Response: status_code=200
  Headers:
    date: Fri, 26 Jan 2024 18:30:33 GMT
    content-type: text/event-stream
    transfer-encoding: chunked
    connection: keep-alive
    access-control-allow-origin: *
    cache-control: no-cache, must-revalidate
    openai-model: gpt-4-1106-preview
    openai-organization: user-r3e61fpak04cbaokp5buoae4
    openai-processing-ms: 239
    openai-version: 2020-10-01
    strict-transport-security: max-age=15724800; includeSubDomains
    x-ratelimit-limit-requests: 5000
    x-ratelimit-limit-tokens: 5000000
    x-ratelimit-remaining-requests: 4999
    x-ratelimit-remaining-tokens: 4999979
    x-ratelimit-reset-requests: 12ms
    x-ratelimit-reset-tokens: 362ms
    x-request-id: cc3f280e037add93f5e09ae130d30f5f
    cf-cache-status: DYNAMIC
    set-cookie: __cf_bm=...
    server: cloudflare
    cf-ray: 84bad3e8b99cce38-SJC
    alt-svc: h3=":443"; ma=86400
  Body:
    data: {"id":"chatcmpl-8lLGDDIjeBjBNEzYeoq4ibZX8jz9F","object":"chat.completion.chunk","created":1706293833,"model":"gpt-4-1106-preview","system_fingerpr
    int":"fp_b4fb435f51","choices":[{"index":0,"delta":{"role":"assistant","content":""},"logprobs":null,"finish_reason":null}]}


    data: {"id":"chatcmpl-8lLGDDIjeBjBNEzYeoq4ibZX8jz9F","object":"chat.completion.chunk","created":1706293833,"model":"gpt-4-1106-preview","system_fingerprint":"fp_b4fb435f51","choices":[{"index":0,"delta":{"content":"Hi"},"logprobs":null,"finish_reason":null}]}

data: {"id":"chatcmpl-8lLGDDIjeBjBNEzYeoq4ibZX8jz9F","object":"chat.completion.chunk","created":1706293833,"model":"gpt-4-1106-preview","system_fingerprint":"fp_b4fb435f51","choices":[{"index":0,"delta":{"content":"!"},"logprobs":null,"finish_reason":null}]}


Hi!    data: {"id":"chatcmpl-8lLGDDIjeBjBNEzYeoq4ibZX8jz9F","object":"chat.completion.chunk","created":1706293833,"model":"gpt-4-1106-preview","system_fingerprint":"fp_b4fb435f51","choices":[{"index":0,"delta":{},"logprobs":null,"finish_reason":"stop"}]}

data: [DONE]
```
```bash
$LLM_OPENAI_SHOW_RESPONSES=1 llm 'say hi shortly' --no-stream
```
```
Request: POST https://api.openai.com/v1/chat/completions
  Headers:
    host: api.openai.com
    connection: keep-alive
    accept: application/json
    content-type: application/json
    user-agent: OpenAI/Python 1.10.0
    x-stainless-lang: python
    x-stainless-package-version: 1.10.0
    x-stainless-os: MacOS
    x-stainless-arch: arm64
    x-stainless-runtime: CPython
    x-stainless-runtime-version: 3.10.4
    authorization: [...]
    x-stainless-async: false
    content-length: 109
  Body:
    {
      "messages": [
        {
          "role": "user",
          "content": "say hi shortly"
        }
      ],
      "model": "gpt-4-1106-preview",
      "stream": false
    }
Response: status_code=200
  Headers:
    date: Fri, 26 Jan 2024 18:30:39 GMT
    content-type: application/json
    content-length: 463
    connection: keep-alive
    access-control-allow-origin: *
    cache-control: no-cache, must-revalidate
    openai-model: gpt-4-1106-preview
    openai-organization: user-r3e61fpak04cbaokp5buoae4
    openai-processing-ms: 386
    openai-version: 2020-10-01
    strict-transport-security: max-age=15724800; includeSubDomains
    x-ratelimit-limit-requests: 5000
    x-ratelimit-limit-tokens: 5000000
    x-ratelimit-remaining-requests: 4999
    x-ratelimit-remaining-tokens: 4999978
    x-ratelimit-reset-requests: 12ms
    x-ratelimit-reset-tokens: 362ms
    x-request-id: 77cef3ff578689ba666796dacf0e928a
    cf-cache-status: DYNAMIC
    set-cookie: __cf_bm=...
    server: cloudflare
    cf-ray: 84bad40b7d452523-SJC
    alt-svc: h3=":443"; ma=86400
  Body:
    {
  "id": "chatcmpl-8lLGIvcbYwG9zm5ix1gem1FSXZiFn",
  "object": "chat.completion",
  "created": 1706293838,
  "model": "gpt-4-1106-preview",
  "choices": [
    {
   
       "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hi!"
      },
      "logprobs": null,
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 2,
    "total_tokens": 12
  },
  "system_fingerprint": "fp_b4fb435f51"
}

Hi!
```
