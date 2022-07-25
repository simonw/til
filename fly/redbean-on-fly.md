# Deploying a redbean app to Fly

[redbean](https://redbean.dev/) is a fascinating project - it provides a web server in a self-contained executable which you can add assets (or dynamic Lua code) to just by zipping them into the same binary package.

I decided to try running it on [Fly](https://fly.io). Here's the recipe that worked for me.

## The Dockerfile

I copied this Dockerfile, unmodified, from https://github.com/kissgyorgy/redbean-docker/blob/master/Dockerfile-multistage by György Kiss:

```dockerfile
FROM alpine:latest as build

ARG DOWNLOAD_FILENAME=redbean-original-2.0.8.com

RUN apk add --update zip bash
RUN wget https://redbean.dev/${DOWNLOAD_FILENAME} -O redbean.com
RUN chmod +x redbean.com

# normalize the binary to ELF
RUN sh /redbean.com --assimilate

# Add your files here
COPY assets /assets
WORKDIR /assets
RUN zip -r /redbean.com *

# just for debugging purposes
RUN ls -la /redbean.com
RUN zip -sf /redbean.com


FROM scratch

COPY --from=build /redbean.com /
CMD ["/redbean.com", "-vv", "-p", "80"]
```

It uses a multi-stage build to download redbean, copy in the contents of your `assets/` folder, zip those back up and then create a TINY container from `scratch` that copies in just that executable.

I made an `assets/` folder with something fun in it (a copy of my [Datasette Lite](https://github.com/simonw/datasette-lite) app) like this:
```
mkdir assets
cd assets
wget https://lite.datasette.io/index.html
wget https://lite.datasette.io/webworker.js
```
## Deploying to Fly

First I needed to create a new application. I ran this:

    fly apps create redbean-on-fly

Then I needed a `fly.toml` file. I created this one (copied from a previous example, but I updated the internal server port and the name):

```toml
app = "redbean-on-fly"

kill_signal = "SIGINT"
kill_timeout = 5

[[services]]
  internal_port = 80
  protocol = "tcp"

  [services.concurrency]
    hard_limit = 25
    soft_limit = 20

  [[services.ports]]
    handlers = ["http"]
    port = "80"

  [[services.ports]]
    handlers = ["tls", "http"]
    port = "443"

  [[services.tcp_checks]]
    interval = 10000
    timeout = 2000
    grace_period = "10s"
```

Finally, I deployed the app by running this in the same directory as `fly.toml`:

    fly deploy

This uploaded the `Dockerfile` and `assets/` folder to Fly, ran the build there, then deployed the result.
