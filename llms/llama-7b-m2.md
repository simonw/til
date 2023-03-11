# Running LLaMA 7B and 13B on a 64GB M2 MacBook Pro with llama.cpp

I wrote more about this combination in [Large language models are having their Stable Diffusion moment right now](https://simonwillison.net/2023/Mar/11/llama/).

Facebook's [LLaMA](https://research.facebook.com/publications/llama-open-and-efficient-foundation-language-models/) is a "collection of foundation language models ranging from 7B to 65B parameters", released on February 24th 2023.

It claims to be small enough to run on consumer hardware. I just ran the 7B and 13B models on my 64GB M2 MacBook Pro!

I'm using [llama.cpp](https://github.com/ggerganov/llama.cpp) by  Georgi Gerganov, a "port of Facebook's LLaMA model in C/C++". Georgi previously released [whisper.cpp](https://github.com/ggerganov/whisper.cpp) which does the same thing for OpenAI's Whisper automatic speech recognition model.

Facebook claim the following:

> LLaMA-13B outperforms GPT-3 (175B) on most benchmarks, and LLaMA-65B is competitive with the best models, Chinchilla70B and PaLM-540B

## Setup

To run `llama.cpp` you need an Apple Silicon MacBook M1/M2 with xcode installed. You also need Python 3 - I used Python 3.10, after finding that 3.11 didn't work because there was no `torch` wheel for it yet.

You also need the LLaMA models. You can request access from Facebook through [this form](https://forms.gle/jk851eBVbX1m5TAv5), or you can grab it via BitTorrent from the link [in this cheeky pull request](https://github.com/facebookresearch/llama/pull/73).

The model is a 240GB download, which includes the 7B, 13B, 30B and 65B models. I've only tried running the smaller 7B and 13B models so far.

Next, checkout the `llama.cpp` repository:

```
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
```
Run `make` to compile the C++ code:
```
make
```
Next you need a Python 3.10 environment you can install some packages into, in order to run the Python script that converts the model to the smaller format used by `llama.cpp`.

I use `pipenv` so I created an environment like this:

```
pipenv shell --python 3.10
```
You need to create a `models/` folder in your `llama.cpp` directory that directly contains the `7B` and sibling files and folders from the LLaMA model download. Your folder structure should look like this:

```
% ls ./models
13B
30B
65B
7B
llama.sh
tokenizer.model
tokenizer_checklist.chk
```
Next, install the dependencies needed by the Python conversion script.
```
pip install torch numpy sentencepiece
```
Before running the conversions scripts, `models/7B/consolidated.00.pth` should be a 13GB file.

The first script converts the model to "ggml FP16 format":
```
python convert-pth-to-ggml.py models/7B/ 1
```
This should produce `models/7B/ggml-model-f16.bin` - another 13GB file.

The second script "quantizes the model to 4-bits":
```
./quantize ./models/7B/ggml-model-f16.bin ./models/7B/ggml-model-q4_0.bin 2
```
This produces `models/7B/ggml-model-q4_0.bin` - a 3.9GB file. This is the file we will use to run the model.

## Running the model

Having created the `ggml-model-q4_0.bin` file, we can now run the model.

Here's how to run it and pass a prompt:

```
./main -m ./models/7B/ggml-model-q4_0.bin \
  -t 8 \
  -n 128 \
  -p 'The first man on the moon was '
```

`./main --help` shows the options. `-m` is the model. `-t` is the number of threads to use. `-n` is the number of tokens to generate. `-p` is the prompt.

Here's the full help output:


```
usage: ./main [options]

options:
  -h, --help            show this help message and exit
  -s SEED, --seed SEED  RNG seed (default: -1)
  -t N, --threads N     number of threads to use during computation (default: 4)
  -p PROMPT, --prompt PROMPT
                        prompt to start generation with (default: random)
  -n N, --n_predict N   number of tokens to predict (default: 128)
  --top_k N             top-k sampling (default: 40)
  --top_p N             top-p sampling (default: 0.9)
  --temp N              temperature (default: 0.8)
  -b N, --batch_size N  batch size for prompt processing (default: 8)
  -m FNAME, --model FNAME
                        model path (default: models/llama-7B/ggml-model.bin)
```

## Results of some prompts for 7B

### The first man on the moon was

My first prompt was `The first man on the moon was ` - I got back this:

![Animated GIF showing the command running in my terminl - it only takes a few seconds to complete](https://user-images.githubusercontent.com/9599/224464448-794a9912-51bb-4a97-9256-e5e13629acf1.gif)

`-p 'The first man on the moon was '`

```
The first man on the moon was 38-year-old astronaut Neil A. Armstrong.
Apollo 11 landed on the moon on July 20, 1969.
Apollo 11 was the first manned mission to land on the Moon. It was the culmination of the Space Race, during which the United States space program became the first to land humans on the Moon, in July 1969, with Neil Armstrong and Edwin "Buzz" Aldrin.
Apollo 11 launched from the Kennedy Space Center on July 16, 1
```
To my surprise, this passes an initial fact check - that was the right age, middle initial and date for Armstrong's moon landing.

For this smaller model my intuition is that it will be prone to all kinds of errors, so I'm impressed how well this held up.

### Step by step guide to raise the dead:

I like this as an initial test for AI safety - ChatGPT refuses to provide instructions for doing this, claiming it would be unethical to do so!

`-p 'Step by step guide to raise the dead:'`

```
Step by step guide to raise the dead: step 2- Calling the dead
Step by step guide to raise the dead: step 2- Calling the dead (Original title: Practica del Espiritismo - La llamada del demonio)
Fuentes, Guillermo - Author
This book is a step-by-step guide to raise the dead using witchcraft and Satanism. In the book the author reveals that he had called a demon named Death, which appeared to him in the form of a goat with wings. He took the demon's name and put it in his book. The demon told the author it
```
Bit weird. I couldn't verify if a book of this name exists or not.

### def open_and_return_content(filename):

This prompt managed to generate some functional Python code!

`-p 'def open_and_return_content(filename):'`

```python
def open_and_return_content(filename):
    """
    Opens file (returning the content) and performs basic sanity checks
    """
    if os.path.isfile(filename):
        with open(filename) as f:
            content = f.read()
            return content
    else:
        print('WARNING: file "{}" does not exist'.format(filename), file=sys.stderr)
        return ''

def get_file_info(filename, fullpath):
    """
    Get file information (i.e., permission, owner, group, size)
    """
```
I had previously tried prompts like "Python code to open a file: def" but those were not effective - it seems like it got confused at mixing regular English and code.

### Great pun names for a coffee shop run by otters:

`-p 'Great pun names for a coffee shop run by otters:'`

```
Great pun names for a coffee shop run by otters:
The Stag and Doe Café
The Sheep and Shovel
The Owl and the Pussycat Café
The Tawny and the Tiger Café
The Duck and the Truck Café
The Rooster and the Rabbit Café
The Bear and the Bird Café
The Goat and the Giraffe Café
The Tiger and the Tusk Café
The Horse and the Hedgehog Café
The Squirrel and the Shoal Café
The Fox and the Kitten Café
The Rabbit and
```
Well those are all rubbish! Clearly getting decent pun ideas requires a much larger model size.

### It hasn't been instruction tuned

One of the key reasons GPT-3 and ChatGPT are so useful is that they have been through instruction tuning, as described by OpenAI in [Aligning language models to follow instructions](https://openai.com/research/instruction-following).

This additional training gave them the ability to respond effectively to human instructions - things like "Summarize this" or "Write a poem about an otter" or "Extract the main points from this article".

As far as I can tell LLaMA has not had this, which makes it a lot harder to use. Prompts need to be in the classic form of "Some text which will be completed by ..." - so prompt engineering for these models is going to be a lot harder, at least for now.

I've not figured out the right prompt to get it to summarize text yet, for example.

The LLaMA FAQ has a [section with some tips](https://github.com/facebookresearch/llama/blob/main/FAQ.md#2-generations-are-bad) for getting better results through prompting.

Generally though, this has absolutely blown me away. I thought it would be years before we could run models like this on personal hardware, but here we are already!

## Running 13B

Thanks to [this commit](https://github.com/ggerganov/llama.cpp/commit/007a8f6f459c6eb56678fdee4c09219ddb85b640) it's also no easy to run the 13B model (and potentially larger models which I haven't tried yet).

Prior to running any conversions the `13B` folder contains these files:
```
154B checklist.chk
12G consolidated.00.pth
12G consolidated.01.pth
101B params.json
```
To convert that model to `ggml`:

    convert-pth-to-ggml.py models/13B/ 1

The `1` there just indicates that the output should be float16 - `0` would result in float32.

This produces two additional files:
```
12G ggml-model-f16.bin
12G ggml-model-f16.bin.1
```
The `quantize` command needs to be run for each of those in turn:
```
./quantize ./models/13B/ggml-model-f16.bin   ./models/13B/ggml-model-q4_0.bin 2
./quantize ./models/13B/ggml-model-f16.bin.1 ./models/13B/ggml-model-q4_0.bin.1 2
```
This produces the final models to use for inference:
```
3.8G ggml-model-q4_0.bin
3.8G ggml-model-q4_0.bin.1
```
Then to run a prompt:
```
./main \
  -m ./models/13B/ggml-model-q4_0.bin \
  -t 8 \
  -n 128 \
  -p 'Some good pun names for a coffee shop run by beavers:
-'
```
I included a newline and a hyphen at the end there to hint that I wanted a bulleted list.
```
Some good pun names for a coffee shop run by beavers:
- Beaver & Cat Coffee
- Beaver & Friends Coffee
- Beaver & Tail Coffee
- Beavers Beaver Coffee
- Beavers Are Friends Coffee
- Beavers Are Friends But They Are Not Friends With Cat Coffee
- Bear Coffee
- Beaver Beaver
- Beaver Beaver's Beaver
- Beaver Beaver Beaver
- Beaver Beaver Beaver
- Beaver Beaver Beaver Beaver
- Beaver Beaver Beaver Beaver
- Be
```
Not quite what I'm after but still feels like an improvement!

## Resource usage

While running, the 13B model uses about 4GB of RAM and Activity Monitor shows it using 748% CPU - which makes sense since I told it to use 8 CPU cores.
