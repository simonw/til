# Processing a stream of chunks of JSON with ijson

A follow-up to [Using OpenAI functions and their Python library for data extraction](https://til.simonwillison.net/gpt3/openai-python-functions-data-extraction) and [Using the ChatGPT streaming API from Python](https://til.simonwillison.net/gpt3/python-chatgpt-streaming-api). If I have a stream of chunks of a larger JSON document, how can I output full individual JSON objects as soon as they are available?

My completed JSON will look like this:

```json
{
  "items": [
    {
      "title": "Classic and Custom Car Show",
      "date": "Sat, Sep 2",
      "venue_name": "1700 W Hillsdale Blvd • San Mateo, CA",
      "start_time": "9:00 AM"
    },
    {
      "title": "【衛蘭、王君馨、衛詩、鍾舒漫、吉中鳴牧師】MMO AINEO LIVE 愛你喲！佈道會（三藩市站）",
      "date": "Sat, Aug 26",
      "venue_name": "San Mateo Performing Arts Center • San Mateo, CA",
      "start_time": "7:30 PM"
    },
    {
      "title": "San Francisco Small Business Expo 2023",
      "date": "Fri, Aug 18",
      "venue_name": "Hyatt Regency San Francisco Airport • Burlingame, CA",
      "start_time": "10:00 AM"
    },
    {
      "title": "Stanford Genetics Conference on Structural Variants and DNA Repeats",
      "date": "Thu, Sep 7",
      "venue_name": "Stanford Center for Academic Medicine • Palo Alto, CA",
      "start_time": "8:00 AM"
    },
    {
      "title": "DJ QUIK / ROJAI / Z-MAN / DJ SAURUS",
      "date": "Fri, Aug 18",
      "venue_name": "The Longboard Margarita Bar • Pacifica, CALIFORNIA",
      "start_time": "9:00 PM"
    },
    {
      "title": "DUE SOUTH W/ CHERRY GLAZERR, MOMMA (DUO), KING ISIS (FREE!)",
      "date": "Sat, Aug 26",
      "venue_name": "Jerry Garcia Amphitheater • San Francisco, CA",
      "start_time": "2:30 PM"
    }
  ]
}
```
If that's going to arrive as a sequence of chunks, how can I display those items as soon as they become available?

After much experimentation I figured out this recipe using [ijson](https://pypi.org/project/ijson/):
```python
import ijson
import json
import time

chunks = [
    '{\n  "items": [\n    {\n      "ti',
    'tle": "Classic and Custom Car ',
    'Show",\n      "date": "Sat, Sep',
    ' 2",\n      "venue_name": "1700',
    " W Hillsdale Blvd • San Mateo,",
    ' CA",\n      "start_time": "9:0',
    '0 AM"\n    },\n    {\n      "titl',
    'e": "【衛蘭、王君馨、衛詩、鍾舒漫、吉中鳴牧師】MMO ',
    'AINEO LIVE 愛你喲！佈道會（三藩市站）",\n   ',
    '   "date": "Sat, Aug 26",\n    ',
    '  "venue_name": "San Mateo Per',
    "forming Arts Center • San Mate",
    'o, CA",\n      "start_time": "7',
    ':30 PM"\n    },\n    {\n      "ti',
    'tle": "San Francisco Small Bus',
    'iness Expo 2023",\n      "date"',
    ': "Fri, Aug 18",\n      "venue_',
    'name": "Hyatt Regency San Fran',
    "cisco Airport • Burlingame, CA",
    '",\n      "start_time": "10:00 ',
    'AM"\n    },\n    {\n      "title"',
    ': "Stanford Genetics Conferenc',
    "e on Structural Variants and D",
    'NA Repeats",\n      "date": "Th',
    'u, Sep 7",\n      "venue_name":',
    ' "Stanford Center for Academic',
    ' Medicine • Palo Alto, CA",\n  ',
    '    "start_time": "8:00 AM"\n  ',
    '  },\n    {\n      "title": "DJ ',
    "QUIK / ROJAI / Z-MAN / DJ SAUR",
    'US",\n      "date": "Fri, Aug 1',
    '8",\n      "venue_name": "The L',
    "ongboard Margarita Bar • Pacif",
    'ica, CALIFORNIA",\n      "start',
    '_time": "9:00 PM"\n    },\n    {',
    '\n      "title": "DUE SOUTH W/ ',
    "CHERRY GLAZERR, MOMMA (DUO), K",
    'ING ISIS (FREE!)",\n      "date',
    '": "Sat, Aug 26",\n      "venue',
    '_name": "Jerry Garcia Amphithe',
    'ater • San Francisco, CA",\n   ',
    '   "start_time": "2:30 PM"\n   ',
    " }\n  ]\n}",
]


events = ijson.sendable_list()
coro = ijson.items_coro(events, "items.item")

seen_events = set()

for chunk in chunks:
    coro.send(chunk.encode("utf-8"))
    if events:
        # Any we have not seen yet?
        unseen_events = [e for e in events if json.dumps(e) not in seen_events]
        if unseen_events:
            for event in unseen_events:
                seen_events.add(json.dumps(event))
                print(json.dumps(event))
                time.sleep(1)
```
You create an `ijson` coroutine, then send it chunks of JSON data. It will write new items to the `sendable_list()` as soon as they are available.

The hardest part to figure out was this:

```python
coro = ijson.items_coro(events, "items.item")
```
This is the syntax to indicate that I'm interested in the array items in the `{"items": [...]}` object.

The confusing part is that `item` here is a reserved word in `ijson` which means "individual items of an array". I'm not sure what you are meant to do if your nested object also has a key called `"item"` - I guess work to avoid that situation from coming up!

This works though. The above code, when executed, prints out each of the nested objects one at a time, with a 1 second sleep between each one.
