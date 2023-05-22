# mlc-chat - RedPajama-INCITE-Chat-3B on macOS

MLC (Machine Learning Compilation) on May 22nd 2023: [Bringing Open Large Language Models to Consumer Devices](https://mlc.ai/blog/2023/05/22/bringing-open-large-language-models-to-consumer-devices)

> RedPajama on Apple Silicon is achieved by compiling the LLM using Metal for M1/M2 GPUs

The instructions [they provided](https://mlc.ai/mlc-llm/#windows-linux-mac) didn't quite give me all the information I needed to get this to work. Here's what I did instead.

**UPDATE:** The official instructions now cover `RedPajama-INCITE-Chat-3B` as well.

## Install Conda

Their instructions require Conda. I installed `miniconda` using Homebrew like this:

    brew install --cask miniconda

## Following their initial instructions for Vicuna-7B

These worked for getting the `mlc-chat-vicuna-v1-7b` model running on my laptop.

First I created `mlc-chat/dist/prebuilt` and pulled some models and files from their repos:

```bash
mkdir mlc-chat
cd mlc-chat
mkdir -p dist/prebuilt
# git lfs install - not necessary, I already had Git LFS
cd dist/prebuilt
git clone https://huggingface.co/mlc-ai/mlc-chat-vicuna-v1-7b-q3f16_0
git clone https://github.com/mlc-ai/binary-mlc-llm-libs.git lib
cd ../..
```
Then I created a Conda environment and installed some packages into that:
```bash
conda create -n mlc-chat
conda activate mlc-chat
conda install -c mlc-ai -c conda-forge mlc-chat-nightly
conda init zsh
# Quit and re-open terminal
cd mlc-chat
conda activate mlc-chat
```
Having done this, I could run the Vicuna model like so:
```bash
mlc_chat_cli --local-id vicuna-v1-7b-q3f16_0
```
```
Use MLC config: "/Users/simon/not-in-backups/mlc-chat/dist/prebuilt/mlc-chat-vicuna-v1-7b-q3f16_0/mlc-chat-config.json"
Use model weights: "/Users/simon/not-in-backups/mlc-chat/dist/prebuilt/mlc-chat-vicuna-v1-7b-q3f16_0/ndarray-cache.json"
Use model library: "/Users/simon/not-in-backups/mlc-chat/dist/prebuilt/lib/vicuna-v1-7b-q3f16_0-metal.so"
Loading model...
You can use the following special commands:
  /help               print the special commands
  /exit               quit the cli
  /stats              print out the latest stats (token/sec)
  /reset              restart a fresh chat
  /reload [local_id]  reload model "local_id" from disk, or reload the current model if `local_id` is not specified

[11:59:01] /Users/catalyst/Workspace/mlc-chat-conda-build/tvm/src/runtime/metal/metal_device_api.mm:165: Intializing Metal device 0, name=Apple M2 Max
USER: Write a rap battle between a pelican and a cheesecake
ASSISTANT: (Verse 1)
I'm a pelican, I'm the king of the sea
I'm a big bird with a big appetite for cheesecake
I'll be taking that piece of cheesecake right off your plate
I'll be feasting on the creamy goodness that's sweet

(Chorus)
You'll never see me coming for that slice
I'll be the one taking it all in this lunch time
So beware my sharp beak and talons, I'm coming for that slice
I'll be the one with a big appetite for that cheesecake good
# ...
```
## Figuring out how to run RedPajama-INCITE-Chat-3B

This wasn't covered in their documentation, but I figured it out through trial and error.
```bash
cd dist/prebuilt
git clone https://huggingface.co/mlc-ai/mlc-chat-RedPajama-INCITE-Chat-3B-v1-q4f16_0
cd ../..
```
Now I can run that model like so:
```
mlc_chat_cli --local-id RedPajama-INCITE-Chat-3B-v1-q4f16_0
```
```
Use MLC config: "/Users/simon/not-in-backups/mlc-chat/dist/prebuilt/mlc-chat-RedPajama-INCITE-Chat-3B-v1-q4f16_0/mlc-chat-config.json"
Use model weights: "/Users/simon/not-in-backups/mlc-chat/dist/prebuilt/mlc-chat-RedPajama-INCITE-Chat-3B-v1-q4f16_0/ndarray-cache.json"
Use model library: "/Users/simon/not-in-backups/mlc-chat/dist/prebuilt/lib/RedPajama-INCITE-Chat-3B-v1-q4f16_0-metal.so"
Loading model...
You can use the following special commands:
  /help               print the special commands
  /exit               quit the cli
  /stats              print out the latest stats (token/sec)
  /reset              restart a fresh chat
  /reload [local_id]  reload model "local_id" from disk, or reload the current model if `local_id` is not specified

[12:01:41] /Users/catalyst/Workspace/mlc-chat-conda-build/tvm/src/runtime/metal/metal_device_api.mm:165: Intializing Metal device 0, name=Apple M2 Max
<human>: Write a rap battle between a pelican and a cheesecake
<bot>: Who's got more bounce?
The pelican's got a bounce like no other.

Pelicans are known for their unique style,
they're like a flying dunk in the truest form.
They're like a wall in the sky,
a wall that can't be broken.

But I'd argue that I've got more bounce
than you could ever imagine,
I'm like a cheesecake with a lot more flavor,
I'm like a cheesecake that'll never quit.

I'm like a cheesecake with a lot more flavor,
I'm like a cheesecake that'll never quit,
I'm like a cheesecake that'll never quit.

I'm like a cheesecake that'll never quit,
I'm like a cheesecake that'll never quit,
I'm like a cheesecake that'll never quit.
```
