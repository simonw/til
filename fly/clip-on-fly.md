# Deploying the CLIP embedding model on Fly

Inspired by [Drew Breunig's Faucet Finder](https://www.dbreunig.com/2023/09/26/faucet-finder.html) I decided I wanted to deploy an API somewhere that could calculate [CLIP embeddings](https://simonwillison.net/2023/Sep/12/llm-clip-and-chat/) for me.

I ended up deploying a Datasette instance to [Fly.io](https://fly.io/) using my [llm-clip](https://github.com/simonw/llm-clip) and [datasette-llm-embed](https://github.com/simonw/datasette-llm-embed) plugins.

This was a little tricky because CLIP has much larger memory requirements than most of the applications that I deploy using Datasette. Here's how I got it to work.

## Building the app with Dockerfile and fly.toml

I ended up needing two files. The first was a `Dockerfile`, and the second was a `fly.toml` file to configure the deployment.

Here's the `Dockerfile`:

```dockerfile
FROM python:3.11.0-slim-bullseye
COPY . /app
WORKDIR /app

RUN pip install -U torch torchvision --extra-index-url https://download.pytorch.org/whl/cpu
RUN pip install -U datasette datasette-scale-to-zero datasette-block-robots datasette-llm-embed llm-clip
# Download the CLIP model
RUN llm embed -m clip -c 'hello world'

# Create metadata.json file
RUN echo '{"plugins": {"datasette-scale-to-zero": {"duration": "10m"}}}' > /app/metadata.json

# Expose and start the service
ENV PORT 8080
EXPOSE 8080
CMD datasette serve --host 0.0.0.0 --cors --port $PORT -m /app/metadata.json
```
The trickiest detail here was installing `torch` and `torchvision`. It turns out the Fly builder application I was using had access to CUDA libraries, which caused it to install the ultra-heavy version of PyTorch - multiple GBs of data.

After much experimentation I found that this incantation causes PyTorch to be installed with CPU-only dependencies, which is a fraction of the size:

    pip install -U torch torchvision \
      --extra-index-url https://download.pytorch.org/whl/cpu

The rest of the `Dockerfile` is pretty standard - it installs some Datasette plugins plus `llm-clip`.

One trick I'm using is to run `llm embed -m clip -c 'hello world'` as part of the build process. This causes the CLIP model to be downloaded from Hugging Face and cached as part of the Docker image build process, which means it's baked into the container and available immediately when the app starts up.

My `fly.toml` file looks like this:

```toml
app = "clip-datasette-on-fly"

[[services]]
  internal_port = 8080
  protocol = "tcp"

  [services.concurrency]
    hard_limit = 25
    soft_limit = 20

  [[services.ports]]
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

  [[services.tcp_checks]]
    interval = 10000
    timeout = 2000
```

## Deploying the application

I ran the following commands in the same directory as the `fly.toml` and `Dockerfile` files to create the application and then deploy it:

```bash
flyctl apps create clip-datasette-on-fly
flyctl deploy
```

The app name needs to be unique across all of Fly, so you will need to change this if you want to deploy your own copy.

The default deployment didn't have enough memory to run CLIP without crashing. I ran these commands to fix that:

```bash
flyctl scale vm performance-1x
flyctl scale memory 8192
```
If this machine ran all the time it would cost me $61.02/month - but I've installed the [datasette-scale-to-zero](https://github.com/simonw/datasette-scale-to-zero) and configured it to stop the server after 10m of no activity, which should save a lot of money. 

I also installed [datasette-block-robots](https://github.com/simonw/datasette-block-robots) to prevent search engines from crawling the site and waking it up more than strictly necessary.

## Using it from an Observable Notebook

My [Search for Faucets with CLIP, API edition](https://observablehq.com/@simonw/search-for-faucets-with-clip-api) Observable notebook makes calls to my newly deployed API to calculate CLIP embeddings for text, then passes the result to Drew's Faucet Finder to find matching faucets.

The relevant JavaScript looks like this, where `text` is the text to be embedded:

```javascript
hex_embedding = {
  try {
    return (
      await (
        await fetch(
          `https://clip-datasette-on-fly.fly.dev/_memory.json?sql=select+hex(llm_embed(%27clip%27%2C+%3Aq))+as+x&q=${encodeURIComponent(
            text
          )}&_shape=array`
        )
      ).json()
    )[0].x;
  } catch {
    return "";
  }
}
```
Here's [the HTML version](https://clip-datasette-on-fly.fly.dev/_memory?sql=select+hex%28llm_embed%28%27clip%27%2C+%3Aq%29%29+as+x&q=purple+and+gold) of that SQL query.
