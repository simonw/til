# Using Codex CLI with gpt-oss:120b on an NVIDIA DGX Spark via Tailscale

I've written about the [DGX Spark](https://simonwillison.net/2025/Oct/14/nvidia-dgx-spark/) before. Here's how I got OpenAI's Codex CLI to run on my Mac against a gpt-oss:120b model running on the DGX Spark via a Tailscale network.

## Setting up Tailscale

I installed Tailscale on the Spark a while ago and didn't make detailed notes. The Spark runs Ubuntu so I followed the [Tailscale Linux installation instructions](https://tailscale.com/kb/1031/install-linux).

My Mac is signed into Tailscale as well. I obtained the IP address for the Spark from the MacOS system tray menu: Network Devices -> My Devices -> spark-18b3 (the hostname). 

For me that was:

    100.113.1.114

## Ollama on the Spark

I installed [Ollama](https://ollama.com/) on the Spark using their [installation script](https://ollama.com/download/linux). This got it running as a service, but the default settings bind it to localhost only. I wanted to access it from other machines, so I did the following (with the [help of Claude Code](https://gistpreview.github.io/?8185e078044004e2d4c3f86fc979fd23)):

```bash
sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo bash -c 'cat > /etc/systemd/system/ollama.service.d/override.conf <<EOF
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
EOF'
```
Then restarted Ollama:
```bash
sudo systemctl daemon-reload
sudo systemctl restart ollama
```
I confirmed it was running by visiting this URL on my Mac:

`http://100.113.1.114:11434/`

Which returned the text:

    Ollama is running

## Hitting Ollama from the Mac

I had Ollama installed on my Mac already as well, which meant the `ollama` client tool was available.

Setting the `OLLAMA_HOST` environment variable to point to the Spark means that client tool can talk to that Ollama server instead.

Here's an example session on my Mac. `ollama ls` on its own shows the models installed locally on my Mac:

```
~ % ollama ls
NAME                ID              SIZE      MODIFIED      
gpt-oss:20b         aa4295ac10c3    13 GB     7 weeks ago      
gemma3:270m         b16d6d39dfbd    241 MB    2 months ago     
gemma3:4b           c0494fe00251    3.3 GB    7 months ago     
deepseek-r1:1.5b    a42b25d8c10a    1.1 GB    9 months ago     
llama3.2:3b         a80c4f17acd5    2.0 GB    10 months ago    
```
But if I add `OLLAMA_HOST=` before the command I talk to the Spark instead:

```
~ % OLLAMA_HOST=100.113.1.114:11434 ollama ls
NAME            ID              SIZE      MODIFIED    
llama3.2:3b     a80c4f17acd5    2.0 GB    6 weeks ago    
gpt-oss:120b    f7f8e2f8f4e0    65 GB     7 weeks ago    
gpt-oss:20b     aa4295ac10c3    13 GB     7 weeks ago    
qwen3:4b        e55aed6fe643    2.5 GB    7 weeks ago    
```
It already had the 120b model, but if it didn't I could pull it with this command:

```
OLLAMA_HOST=100.113.1.114:11434 ollama pull gpt-oss:120b
```
I can start an interactive chat session with the model like this:

```
~ % OLLAMA_HOST=100.113.1.114:11434 ollama run gpt-oss:120b  
>>> hi
Thinking...
The user says "hi". Need to respond friendly. Probably ask how can help.
...done thinking.

Hello! 👋 How can I assist you today?
```
Or use my [LLM](https://llm.datasette.io/) tool with the llm-ollama plugin like so:
```bash
uv tool install llm
llm install llm-ollama
OLLAMA_HOST=100.113.1.114:11434 llm -m gpt-oss:120b \
   "Write a haiku about Tailscale"
```
Cute:
```
Clouds become a thread  
Phones and laptops link as one  
Network breathes as one
```
Setting `export OLLAMA_HOST=100.113.1.114:11434` saves me from having to type it each time.

## Running the Codex CLI

This was harder to figure out - I'm not sure the Ollama mechanis is particularly stable, so I ended up checking out [openai/codex](https://github.com/openai/codex) and having Codex with GPT-5 figure out how to configure that OLLAMA_HOST setting. Here's [that transcript](https://gistpreview.github.io/?54dcf8b4b77ddfb87111af9c759b54e6).

The recipe that worked for me was this one:

```bash
CODEX_OSS_BASE_URL=http://100.113.1.114:11434/v1 \
  codex --oss --model gpt-oss:120b
```
The `CODEX_OSS_BASE_URL` environment variable tells Codex CLI where to find the Ollama server API endpoint. By default it uses the smaller gpt-oss:20b model, but passing `--model gpt-oss:120b` tells it to use the 120b model instead.

## Building Space Invaders

I ran this sequence of prompts inside Codex:

- `make /tmp/invaders and cd to that`
- `build space invaders as a single HTML file`
- `init a git repo and commit your code`
- `Make the space invaders different colors`

Here's [the resulting game](https://static.simonwillison.net/static/2025/gpt-oss-120b-invaders.html), and a copy of [the transcript](https://gistpreview.github.io/?ce40fafd9c3258e74246fdd2489c461b).

So it works! I can now run Codex on my Mac against a competent-enough model on the Spark, via Tailscale which means I can access it using my laptop anywhere in the world.

I don't think I'll use this heavily - GPT-5 and Sonnet 4.5 remain wildly more capable than gpt-oss:120b - but it's neat to be able to do this.
