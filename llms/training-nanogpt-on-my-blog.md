# Training nanoGPT entirely on content from my blog

This is a follow-up to [Running nanoGPT on a MacBook M2 to generate terrible Shakespeare](https://til.simonwillison.net/llms/nanogpt-shakespeare-m2).

I used [nanoGPT](https://github.com/karpathy/nanoGPT) by Andrej Karpathy to train a GPT model entirely against content from my blog!

It can now produce junk output that sounds a little bit like I do.

Example output:

> I'm not learning the idea of authentication. Instead, you're missing content management, which is a great example of a web application that has just one of the web developers. What are good worth a single list on which people are using in JavaScript - this data for your web applications, other alternatives that you can pull them in the HTML in an additional Python objects of JavaScript, and just a small server-side web server as well as web-based applications.

And here's what I get if I start it with the prompt "Datasette is":

> Datasette is a great idea about on the idea to worry about an end of a browser for that can be used to build a Django-freedraw.
>
> I don't want to see your own Datasette instance to be able to run Datasette and then wrote more about this script - which means that you can try that out if your issue their email or with a password.

I mainly used the same technique [described in my previous article](https://til.simonwillison.net/llms/nanogpt-shakespeare-m2) - but I started by creating my own training set, rather than using the Shakespeare example.

## Initial setup

I already had a clone of the `nanoGPT` repository, created like this:

```bash
git clone https://github.com/karpathy/nanoGPT
```
I had installed the following into a fresh Python virtual environment:
```
pip install transformers datasets tiktoken tqdm wandb numpy
pip install httpx
pip install \
  --pre torch torchvision torchaudio \
  --extra-index-url https://download.pytorch.org/whl/nightly/cpu
```


In the `nanoGPT` folder I created a `data/simonwillisonblog` folder.

## Fetching the data

I created a `fetch.py` file in my `simonwillisonblog` folder containing the following:

```python
import httpx
import json
import re

fp = open("input.nl-json", "w")

tag_re = re.compile('<.*?>')

url = "https://datasette.simonwillison.net/simonwillisonblog/blog_entry.json?_col=title&_col=body&_shape=objects&_size=max"

while url:
    data = httpx.get(url).json()
    for item in data["rows"]:
        title = item["title"]
        body = tag_re.sub('', item["body"])
        fp.write(json.dumps([title, body]) + "\n")
    url = data["next_url"]
```
This uses [HTTPX](https://www.python-httpx.org/) (similar to `requests`) to download the "title" and "body" columns from all 2,953 of my blog entries, dating back to 2002.

It uses [this Datasette table](https://datasette.simonwillison.net/simonwillisonblog/blog_entry), which is a mirror of my blog's Django PostgreSQL database.

It saves them as newline-delimited JSON.

I ran `python fetch.py`. The resulting `input.nl-json` file is 4.2MB long and looks like this:

```
["WaSP Phase II", "The Web Standards project has launched Phase II."]
["Blogging aint easy", "Blogging isn't nearly as easy as it looks. After several days ..."]
```
Each line of the file is a JSON array containing the title and body.

## Splitting the data into training and validation sets

I created `data/simonwillisonblog2/prepare.py` as a modified version of the [prepare.py script](https://github.com/karpathy/nanoGPT/blob/e58f0cfa9466dafe226b51ce6678e2b8fac652d5/data/shakespeare/prepare.py) from the `nanoGPT` repository:

```python
import os
import json
import tiktoken
import numpy as np
import random

input_file_path = os.path.join(os.path.dirname(__file__), 'input.nl-json')

entries = []
with open(input_file_path, 'r') as f:
    for line in f:
        if line.strip():
            entries.append(json.loads(line))

# Shuffle entries
random.shuffle(entries)

n = len(entries)
train_entries = entries[:int(n*0.9)]
val_entries = entries[int(n*0.9):]

# Turn those into strings
train_data = " ".join(
    "{} {}".format(*entry) for entry in train_entries
)
val_data = " ".join(
    "{} {}".format(*entry) for entry in val_entries
)

# encode with tiktoken gpt2 bpe
enc = tiktoken.get_encoding("gpt2")
train_ids = enc.encode_ordinary(train_data)
val_ids = enc.encode_ordinary(val_data)
print(f"train has {len(train_ids):,} tokens")
print(f"val has {len(val_ids):,} tokens")

# export to bin files
train_ids = np.array(train_ids, dtype=np.uint16)
val_ids = np.array(val_ids, dtype=np.uint16)
train_ids.tofile(os.path.join(os.path.dirname(__file__), 'train.bin'))
val_ids.tofile(os.path.join(os.path.dirname(__file__), 'val.bin'))
```
My code is everything up to the `# encode with tiktoken gpt2 bpe` comment.

I load the newline-JSON file into an in-memory array, then run `random.shuffle()` to shuffle the entries. That way the training set and validation set shouldn't be biased by differences in my writing style with later as opposed to earlier blog entries.

I split the entries into 90% training and 10% validation.

Then I use Andrej's code to tokenize the two collections of text (using [tiktoken](https://github.com/openai/tiktoken)) and store those tokens as serialized numpy arrays.

## Training the model

Now that I've prepared the data, I can train the model.

I ran the `train.py` script in the repository root like this:

```
 python train.py \
  --dataset=simonwillisonblog \
  --n_layer=4 \
  --n_head=4 \
  --n_embd=64 \
  --compile=False \
  --eval_iters=1 \
  --block_size=64 \
  --batch_size=8 \
  --device=mps
```

The `--dataset` option points to my new `simonwillisoblog` folder. `--device=mps` is needed for the M2 MacBook Pro - using `--device=cpu` runs about 3 times slower.

I ran this for iter 20,143 iterations before hitting Ctrl+C to stop it.

The script writes out a model checkpoint every 2,000 iterations. You can modify the `eval_interval=` variable in the script to change that - I suggest switching it to something lower like 200, since then you can try sampling the model more frequently while it trains.

Getting to 20,000 iterations took around 45 minutes.

Here's a plot of the loss rate over time using my [@simonw/plot-loss-from-nanogpt](https://observablehq.com/@simonw/plot-loss-from-nanogpt) Observable notebook.

<img width="659" alt="The chart starts at a loss of over 10 at 0 iterations, then falls quickly to 6 at around 1,000 iterations, then falls much more slowly and noisily until it gets to around 3.9 at 20,000 iterations" src="https://user-images.githubusercontent.com/9599/217942712-2ca827b9-11c3-46ef-882f-697c815776d9.png">

The checkpointed model file is 39MB and lives in `out/ckpt.pt`. I uploaded a copy of my 20,000 iteration model here:

https://static.simonwillison.net/static/2023/nanogpt-simonwillisonblog-20000-iterations/ckpt.pt

## Sampling the model

To sample, I ran the provided `sample.py` script:
```
% python sample.py
number of parameters: 3.42M
No meta.pkl found, assuming GPT-2 encodings...
... output shows here ...
```
This script defaults to starting using a newline as the initial prompt. You can set this to something else by editing the `start=` line in the script.

For example:
```python
start = "Datasette is"
```
If you try setting it to an empty string you'll get an error, so set it to `"\n"` if you don't want to provide a prompt.

## It's just my blog entries

An important note since this has come up a few times when I talk to people about this: this model is _not_ an example of fine-tuning an existing model using my own content.

I'm literally training a complete model here from scratch!

The only information this model has about words is the 4.2MB of blog content that I've fed to it.

A real, useful model like GPT-2 or GPT-3 is trained on a vastly larger corpus of text, and uses a great deal more processing power than is available on my laptop.

It's pretty fascinating seeing quite how much you can get done with just 4.2MB of data and under an hour of training, though.
