# A simple Python wrapper for the ChatGPT API

OpenAI [released an API for ChatGPT]() yesterday. It's 1/10th of the price of the `text-davinci-003` model!

Their official [openai](https://pypi.org/project/openai/) Python package has been upgraded to add support for it (in [this commit](https://github.com/openai/openai-python/commit/62b73b9bd426d131910534ae6e0d23d7ae4f8fde#diff-5e240d0df76d48fb0e4ad86868f0e2d4f58e8f249037faa4d366b420a7c36e6c)).

Unlike the regular GPT-3 APIs, this one takes an array of messages that looks like this:

```json
[
  {
    "role": "system",
    "content": "You are a 1700s pirate with an exagerated UK westcountry accent"
  },
  {
    "role": "user",
    "content": "Introduce yourself"
  }
]
```
The "system" role is a way to give the bot additional instructions about how to behave.

This is enough to generate a response - but it's your responsibility to then pass back that response with each subsequent API call in order to maintain context of the prior conversation:
```json
[
  {
    "role": "system",
    "content": "You are a 1700s pirate with an exagerated UK westcountry accent"
  },
  {
    "role": "user",
    "content": "Introduce yourself"
  },
  {
    "role": "assistant",
    "content": "Arrr, me hearties! Shiver me timbers, my name is Cap'n Percy of the Jolly Roger crew! I hail from the land of rolling hills and endless fields, the ol' Westcountry of England. I may not be the finest bloke ye'll come across, but I can sail me ship through any storm and loot any vessel that comes in me way. So hoist the main sails and let's begin the adventure, me hearty!"
  },
  {
    "role": "user",
    "content": "What's your favourite bougie cocktail?"
  }
]
```
(It replied "Bougie cocktails? Ye're speakin' fancy words, matey! I prefer me good ol' rum, straight up or with some water, but if ye really want me to choose a bougie drink, I'd say a Dark 'n Stormy - a mix of dark rum, ginger beer, and lime juice. It's a drink fit for a seafarin' pirate like meself, arrr!")

## A Python wrapper

I built this simple wrapper class to automate the process of recording the conversation and replaying it back to the API each time:

```python
import openai

class ChatBot:
    def __init__(self, system=""):
        self.system = system
        self.messages = []
        if self.system:
            self.messages.append({"role": "system", "content": system})
    
    def __call__(self, message):
        self.messages.append({"role": "user", "content": message})
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result
    
    def execute(self):
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=self.messages)
        # Uncomment this to print out token usage each time, e.g.
        # {"completion_tokens": 86, "prompt_tokens": 26, "total_tokens": 112}
        # print(completion.usage)
        return completion.choices[0].message.content
```
Now I can do the following:
```pycon
>>> simon = ChatBot("You are a chatbot imitating Simon Willison. Pretend to be Simon.")
>>> simon("Tell me about yourself")
```
Without that "Pretend to be X" note it will sometimes mention that it's a chatbot that is only imitating the person.
