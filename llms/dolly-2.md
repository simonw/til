# Running Dolly 2.0 on Paperspace

[Dolly 2.0](https://www.databricks.com/blog/2023/04/12/dolly-first-open-commercially-viable-instruction-tuned-llm) looks to be a big deal. It calls itself "the first open source, instruction-following LLM, fine-tuned on a human-generated instruction dataset licensed for research and commercial use."

I've been trying to run it. I failed to get it to work on my M2 MacBook Pro, so I fired up a 30GB GPU instance on [Paperspace](https://paperspace.com/) instead.

It sort-of worked. It's taking nearly 12 minutes to respond to a prompt yet, so I'm suspicious that I'm not using the right incantations to get it to actually run on the GPU there.

Here's what I did.

1. Sign into Paperspace with my GitHub account
2. Start a new instance - I used the "from scratch" option
3. Open the web-based terminal, run `python -v` to confirm it has Python (it's running 3.9.16)
4. `pip install transformers torch accelerate -U`
5. Run `python`

Then within Python I ran this:

```python
from transformers import pipeline
import torch
import time

instruct_pipeline = pipeline(
    model="databricks/dolly-v2-12b",
    torch_dtype=torch.bfloat16,
    trust_remote_code=True,
    device_map="auto"
)
```
I wrote a little utility function to measure my prompt response time:

```python
def prompt(s):
    start = time.time()
    response = instruct_pipeline(s)     
    end = time.time()
    print(end - start)
    return response
```
Then tested it like this:
```pycon
>>> prompt("First man on the moon?")
716.0470576286316
```
The response:

> Apollo 11 was the American spaceflight that first landed humans on the Moon. Commander Neil Armstrong and lunar module pilot Buzz Aldrin landed the Apollo Lunar Module Eagle on July 20, 1969, at 20:17,  and Armstrong became the first person to step onto the Moon's surface six hours and 39 minutes later, on July 21 at 02:56 UTC. Aldrin joined him 19 minutes later, and they spent about two and a quarter hours together exploring the site they had named Tranquility Base upon landing. Armstrong and Aldrin collected 47.5 pounds (21.5 kg) of lunar material to bring back to Earth as pilot Michael Collins flew the Apollo Command Module Columbia in lunar orbit, and were on the Moon's surface for 21 hours, 36 minutes before lifting off to rejoin Columbia.

The good news: it generated a decent looking answer! But it took 716s - nearly 12 minutes - to do that.

I'm clearly doing something wrong here.

## Dolly v2-2-8b or v2-3b on Colab

Databricks [released smaller checkpoints](https://twitter.com/vagabondjack/status/1646532406198026240) in response to feedback on how hard it was to run the larger models.

Kevin Wu shared [this Colab notebook](https://colab.research.google.com/drive/1A8Prplbjr16hy9eGfWd3-r34FOuccB2c?usp=sharing#scrollTo=TFDTEMuUNeBT) which runs the smaller Dolly v2-2-8b model on Google's Colab infrastructure.

This worked well for me, and returned answers to prompts in 10-30s running against a backend with 12.7GB of system RAM and 15GB of GPU.

The notebook ran this code:

```python
!pip -q install git+https://github.com/huggingface/transformers # need to install from github
!pip -q install accelerate>=0.12.0
```
Then:
```python
import torch
from transformers import pipeline

# use dolly-v2-12b if you're using Colab Pro+, using pythia-2.8b for Free Colab
generate_text = pipeline(
    model="databricks/dolly-v2-2-8b", 
    torch_dtype=torch.bfloat16, 
    trust_remote_code=True,
    device_map="auto"
)
```
I added this:
```python
import time
def prompt(s):
    start = time.time()
    response = generate_text(s)     
    end = time.time()
    print(end - start)
    return response
```
And now I can call `prompt("my prompt here")` to run a prompt.

One slight mystery: this loads `dolly-v2-2-8b` from Hugging Face but I can't find a corresponding page for that model now - https://huggingface.co/databricks/dolly-v2-2-8b redirects to https://huggingface.co/databricks/dolly-v2-3b - it looks like you can use `databricks/dolly-v2-3b` to get the same model, so maybe something was renamed on Hugging Face.
